

CREATE OR REPLACE FUNCTION fn_get_account_history(p_account_id VARCHAR(255))
RETURNS TABLE (
    transaction_id INT,
    transaction_time TIMESTAMP,
    transaction_type VARCHAR(50),
    amount_change NUMERIC(22,3),
    description VARCHAR(255),
    status t_status
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.trans_id,
        t.trans_time,
        -- Determine the transaction category
        CASE 
            WHEN dep.trans_id IS NOT NULL THEN 'Deposit'
            WHEN wtd.trans_id IS NOT NULL THEN 'Withdrawal'
            WHEN bll.trans_id IS NOT NULL THEN 'Bill Payment'
            WHEN obt.trans_id IS NOT NULL THEN 'External Wire'
            WHEN ibt.trans_id IS NOT NULL AND t.affected_account_id = p_account_id THEN 'Internal Transfer (Sent)'
            WHEN ibt.trans_id IS NOT NULL AND ibt.destination_account_id = p_account_id THEN 'Internal Transfer (Received)'
            ELSE 'Unknown'
        END::VARCHAR(50) AS transaction_type,
        
        -- Determine if funds were added or subtracted
        CASE
            -- If it's a deposit, funds are added
            WHEN dep.trans_id IS NOT NULL THEN t.trans_amount
            -- If this account was the receiver of an internal transfer, funds are added
            WHEN ibt.destination_account_id = p_account_id THEN t.trans_amount
            -- In all other scenarios where this account is the affected_account_id, funds were deducted
            ELSE -t.trans_amount
        END AS amount_change,
        
        t.trans_description,
        t.trans_status
    FROM 
        trans t
    -- Left join all child tables to identify the transaction type
    LEFT JOIN deposit dep ON t.trans_id = dep.trans_id
    LEFT JOIN withdraw wtd ON t.trans_id = wtd.trans_id
    LEFT JOIN bill bll ON t.trans_id = bll.trans_id
    LEFT JOIN out_bank_trans obt ON t.trans_id = obt.trans_id
    LEFT JOIN in_bank_trans ibt ON t.trans_id = ibt.trans_id
    WHERE 
        -- Account must be either the sender/initiator OR the receiver of an internal transfer
        t.affected_account_id = p_account_id 
        OR ibt.destination_account_id = p_account_id
    ORDER BY 
        t.trans_time DESC;
END;
$$;

CREATE OR REPLACE FUNCTION fn_in_bank_transfer(
    p_source_account_id      VARCHAR(255),
    p_destination_account_id VARCHAR(255),
    p_amount                 NUMERIC(22,3),
    p_description            VARCHAR(255)
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_source_balance NUMERIC(22,3);
    v_new_trans_id   INT;
BEGIN
    -- Guard: trùng tài khoản
    IF p_source_account_id = p_destination_account_id THEN
        RETURN 0;
    END IF;

    -- Guard: số tiền không hợp lệ
    IF p_amount <= 0 THEN
        RETURN -1;
    END IF;

    -- Khóa và kiểm tra tài khoản nguồn
    SELECT balance INTO v_source_balance
    FROM account
    WHERE account_id = p_source_account_id AND account_status = 'open'
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN 2; -- Sai hoặc khóa tài khoản nguồn
    END IF;

    -- Khóa và kiểm tra tài khoản đích
    PERFORM 1
    FROM account
    WHERE account_id = p_destination_account_id AND account_status = 'open'
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN 3; -- Sai hoặc khóa tài khoản đích
    END IF;

    -- Guard: Kiểm tra số dư
    IF p_amount > v_source_balance THEN
        RETURN 4; -- Hết tiền
    END IF;

    -- Cập nhật số dư
    UPDATE account SET balance = balance - p_amount WHERE account_id = p_source_account_id;
    UPDATE account SET balance = balance + p_amount WHERE account_id = p_destination_account_id;

    -- Ghi log TPT
    INSERT INTO trans (affected_account_id, trans_amount, trans_description, trans_status)
    VALUES (p_source_account_id, p_amount, p_description, 'finished')
    RETURNING trans_id INTO v_new_trans_id;

    INSERT INTO in_bank_trans (trans_id, destination_account_id)
    VALUES (v_new_trans_id, p_destination_account_id);

    RAISE NOTICE 'Transferred % from "%" to "%". Transaction ID: %.',
        p_amount, p_source_account_id, p_destination_account_id, v_new_trans_id;

    RETURN 1; -- Thành công
EXCEPTION WHEN OTHERS THEN
    RETURN -99; -- Lỗi hệ thống đột xuất
END;
$$;


CREATE OR REPLACE FUNCTION fn_out_bank_transaction(
    p_source_account VARCHAR(255),
    p_destination_bank_id VARCHAR(255),
    p_amount NUMERIC,
    p_description VARCHAR(255)
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_trans_id INT;
    v_source_status a_status;
    v_source_balance NUMERIC;
    v_bank_exists BOOLEAN;
BEGIN
    -- 1. Validation
    IF p_amount <= 0 THEN
        RETURN -1;
    END IF;

    -- 2. Lock Row
    SELECT account_status, balance INTO v_source_status, v_source_balance 
    FROM account WHERE account_id = p_source_account FOR UPDATE;

    IF NOT FOUND OR v_source_status = 'closed' THEN
        RETURN 2; -- Tài khoản nguồn sai/đóng
    END IF;

    IF v_source_balance < p_amount THEN
        RETURN 4; -- Hết tiền
    END IF;

    -- 3. Verify Destination Bank
    SELECT EXISTS(SELECT 1 FROM out_bank_supported WHERE out_bank_id = p_destination_bank_id) INTO v_bank_exists;
    IF NOT v_bank_exists THEN
        RETURN 5; -- Ngân hàng không được hỗ trợ
    END IF;

    -- 4. Execute Deduction
    UPDATE account SET balance = balance - p_amount WHERE account_id = p_source_account;

    -- 5. Record Transaction
    INSERT INTO trans (affected_account_id, trans_amount, trans_description, trans_status)
    VALUES (p_source_account, p_amount, p_description, 'finished')
    RETURNING trans_id INTO v_trans_id;

    INSERT INTO out_bank_trans (trans_id, destination_bank_id)
    VALUES (v_trans_id, p_destination_bank_id);

    RAISE NOTICE 'Out-bank transaction successful. ID: %, Amount: %', v_trans_id, p_amount;
    RETURN 1;
EXCEPTION WHEN OTHERS THEN
    RETURN -99;
END;
$$;

CREATE OR REPLACE FUNCTION fn_pay_bill(
    p_source_account   VARCHAR(255),
    p_bill_provider_id INT,
    p_amount           NUMERIC
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_trans_id       INT;
    v_source_status  a_status;
    v_source_balance NUMERIC;
    v_customer_name  VARCHAR(255);
    v_bill_type      VARCHAR(255);
    v_provider_name  VARCHAR(255);
    v_auto_desc      VARCHAR(255);
    v_current_time   TIMESTAMP := NOW();
BEGIN
    -- 1. Validation
    IF p_amount <= 0 THEN
        RETURN -1;
    END IF;

    -- 2. Lock and Validate Account
    SELECT a.account_status, a.balance, c.full_name 
    INTO v_source_status, v_source_balance, v_customer_name
    FROM account a
    JOIN customer c ON a.customer_id = c.customer_id
    WHERE a.account_id = p_source_account FOR UPDATE;

    IF NOT FOUND OR v_source_status = 'closed' THEN
        RETURN 2;
    END IF;

    IF v_source_balance < p_amount THEN
        RETURN 4;
    END IF;

    -- 3. Derive Bill Type and Provider Name
    SELECT t.bill_type, p.bill_provider_name 
    INTO v_bill_type, v_provider_name
    FROM bill_provider_supported p
    JOIN bill_type_supported t ON p.bill_id = t.bill_id
    WHERE p.bill_provider_id = p_bill_provider_id;

    IF NOT FOUND THEN
        RETURN 6; -- Nhà cung cấp hóa đơn không tồn tại
    END IF;

    -- 4. Generate Automatic Description
    v_auto_desc := v_customer_name || ' pay ' || v_bill_type || ' ' || v_provider_name || ' at ' || TO_CHAR(v_current_time, 'YYYY-MM-DD HH24:MI:SS');

    -- 5. Execute Deduction
    UPDATE account SET balance = balance - p_amount WHERE account_id = p_source_account;

    -- 6. Record Transactions (TPT Model)
    INSERT INTO trans (affected_account_id, trans_amount, trans_description, trans_time, trans_status)
    VALUES (p_source_account, p_amount, v_auto_desc, v_current_time, 'finished')
    RETURNING trans_id INTO v_trans_id;

    INSERT INTO bill (trans_id, bill_provider_id)
    VALUES (v_trans_id, p_bill_provider_id);

    RAISE NOTICE 'Bill paid successfully. Description: %', v_auto_desc;
    RETURN 1;
EXCEPTION WHEN OTHERS THEN
    RETURN -99;
END;
$$;

CREATE OR REPLACE FUNCTION fn_withdraw_cash(
    p_account_id  VARCHAR(255),
    p_employee_id INT,
    p_amount      NUMERIC(22,3),
    p_description VARCHAR(255)
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance      NUMERIC(22,3);
    v_new_trans_id INT;
BEGIN
    -- Guard: số tiền
    IF p_amount <= 0 THEN
        RETURN -1;
    END IF;

    -- Guard: nhân viên
    IF NOT EXISTS (SELECT 1 FROM employee WHERE employee_id = p_employee_id AND emp_status = 'active') THEN
        RETURN 7; -- Nhân viên không tồn tại hoặc đã nghỉ việc
    END IF;

    -- Lock tài khoản
    SELECT balance INTO v_balance
    FROM account
    WHERE account_id = p_account_id AND account_status = 'open'
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN 2;
    END IF;

    -- Guard: số dư
    IF v_balance < p_amount THEN
        RETURN 4;
    END IF;

    -- Ghi log
    INSERT INTO trans (affected_account_id, trans_amount, trans_description, trans_status)
    VALUES (p_account_id, p_amount, p_description, 'finished')
    RETURNING trans_id INTO v_new_trans_id;

    INSERT INTO withdraw (trans_id, employee_id)
    VALUES (v_new_trans_id, p_employee_id);

    -- Trừ tiền
    UPDATE account SET balance = balance - p_amount WHERE account_id = p_account_id;

    RAISE NOTICE 'Withdrawal of % from "%" processed by employee ID %. Transaction ID: %.',
        p_amount, p_account_id, p_employee_id, v_new_trans_id;
        
    RETURN 1;
EXCEPTION WHEN OTHERS THEN
    RETURN -99;
END;
$$;