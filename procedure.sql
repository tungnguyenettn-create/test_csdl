-- ============================================================
-- DATABASE: BANK
-- Description: Stored procedures for all core banking operations.
-- ============================================================


-- ============================================================
-- SECTION 1: BRANCH PROCEDURES
-- ============================================================

-- ------------------------------------------------------------
-- PROCEDURE: create_branch
-- Creates a new bank branch.
-- Raises an error if the branch name already exists.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE create_branch(
    p_city        VARCHAR(255),
    p_branch_name VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
DECLARE new_branch_id INT; 
BEGIN
    -- Guard: branch name must be unique (also enforced by UNIQUE constraint)
    IF EXISTS (SELECT 1 FROM branch WHERE branch_name = p_branch_name) THEN
        RAISE EXCEPTION 'Branch with name "%" already exists.', p_branch_name;
    END IF;

    INSERT INTO branch (city, branch_name)
    VALUES (p_city, p_branch_name)
    RETURNING branch_id INTO new_branch_id;

    RAISE NOTICE 'Branch "%" in "%" created successfully with id %.', p_branch_name, p_city, new_branch_id;
END;
$$;


-- ============================================================
-- SECTION 2: EMPLOYEE PROCEDURES
-- ============================================================

-- ------------------------------------------------------------
-- PROCEDURE: create_employee
-- Creates a new employee assigned to a branch.
-- New employees always start with emp_status = 'active' (schema default).
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE create_employee(
    p_branch_id         INT,
    p_employee_name     VARCHAR(255),
    p_identity_card     VARCHAR(255),
    p_employee_password VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
DECLARE new_employee_id INT; 
BEGIN
    -- Guard: branch must exist
    IF NOT EXISTS (SELECT 1 FROM branch WHERE branch_id = p_branch_id) THEN
        RAISE EXCEPTION 'Branch with ID % does not exist.', p_branch_id;
    END IF;

    -- Guard: identity card must be unique across all employees
    IF EXISTS (SELECT 1 FROM employee WHERE identity_card = p_identity_card) THEN
        RAISE EXCEPTION 'An employee with identity card "%" already exists.', p_identity_card;
    END IF;

    -- emp_status defaults to 'active' — no need to pass it explicitly
    INSERT INTO employee (branch_id, employee_name, identity_card, employee_password)
    VALUES (p_branch_id, p_employee_name, p_identity_card, p_employee_password)
    RETURNING employee_id  INTO new_employee_id;

    RAISE NOTICE 'Employee "%" created successfully at branch ID % with employee ID %.', p_employee_name, p_branch_id, new_employee_id;
END;
$$;

-- ------------------------------------------------------------
-- PROCEDURE: deactivate_employee
-- Marks an employee as 'inactive' (resigned / terminated).
-- Does NOT delete the row — historical withdraw/deposit records
-- must keep a valid FK reference to this employee.
-- After deactivation, the employee is blocked from processing
-- any new withdraw or deposit transactions.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE deactivate_employee(
    p_employee_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_employee_name VARCHAR(255);
BEGIN
    -- Guard: employee must exist and currently be active
    SELECT employee_name INTO v_employee_name
    FROM employee
    WHERE employee_id = p_employee_id AND emp_status = 'active';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Employee with ID % does not exist or is already inactive.', p_employee_id;
    END IF;

    UPDATE employee
    SET emp_status = 'inactive'
    WHERE employee_id = p_employee_id;

    RAISE NOTICE 'Employee "%" (ID: %) has been deactivated successfully.', v_employee_name, p_employee_id;
END;
$$;


-- ============================================================
-- SECTION 3: CUSTOMER PROCEDURES
-- ============================================================

-- ------------------------------------------------------------
-- PROCEDURE: create_customer
-- Registers a new customer at a branch.
-- Validates branch existence, unique identity card, and age >= 18.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE create_customer(
    p_full_name     VARCHAR(255),
    p_identity_card VARCHAR(255),
    p_nationality   VARCHAR(255),
    p_dob           DATE,
    p_city          VARCHAR(255),
    p_address       VARCHAR(255),
    p_branch_id     INT
)
LANGUAGE plpgsql
AS $$
DECLARE new_customer_id INT; 
BEGIN
    -- Guard: branch must exist
    IF NOT EXISTS (SELECT 1 FROM branch WHERE branch_id = p_branch_id) THEN
        RAISE EXCEPTION 'Branch with ID % does not exist.', p_branch_id;
    END IF;

    -- Guard: identity card must be unique across all customers
    IF EXISTS (SELECT 1 FROM customer WHERE identity_card = p_identity_card) THEN
        RAISE EXCEPTION 'A customer with identity card "%" already exists.', p_identity_card;
    END IF;

    -- Guard: customer must be at least 18 years old
    IF p_dob > CURRENT_DATE - INTERVAL '18 years' THEN
        RAISE EXCEPTION 'Customer must be at least 18 years old. DOB provided: %', p_dob;
    END IF;

    INSERT INTO customer (full_name, identity_card, nationality, dob, city, address, branch_id)
    VALUES (p_full_name, p_identity_card, p_nationality, p_dob, p_city, p_address, p_branch_id)
    RETURNING customer_id INTO new_customer_id;

    RAISE NOTICE 'Customer "%" registered successfully at branch ID %. with customer ID %', p_full_name, p_branch_id, new_customer_id;
END;
$$;


-- ============================================================
-- SECTION 4: ACCOUNT PROCEDURES
-- ============================================================

-- ------------------------------------------------------------
-- PROCEDURE: create_account
-- Opens a new bank account for an existing customer.
-- open_date and close_date use schema defaults — not passed explicitly.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE create_account(
    p_account_id       VARCHAR(255),
    p_customer_id      INT,
    p_account_password VARCHAR(255),
    p_employee_id      INT,                        -- Moved before p_initial_balance so the DEFAULT below is valid
    p_initial_balance  NUMERIC(22,3) DEFAULT 0     -- Optional; defaults to 0 if not provided
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_description VARCHAR(255) := 'Initial deposit on account opening';  -- v_ prefix for local variables
BEGIN
    -- Guard: customer must exist
    IF NOT EXISTS (SELECT 1 FROM customer WHERE customer_id = p_customer_id) THEN
        RAISE EXCEPTION 'Customer with ID % does not exist.', p_customer_id;
    END IF;

    -- Guard: account ID must be unique
    IF EXISTS (SELECT 1 FROM account WHERE account_id = p_account_id) THEN
        RAISE EXCEPTION 'Account with ID "%" already exists.', p_account_id;
    END IF;

    -- Guard: initial balance cannot be negative
    IF p_initial_balance < 0 THEN
        RAISE EXCEPTION 'Initial balance cannot be negative. Provided: %', p_initial_balance;
    END IF;

    -- Create the account shell with zero balance
    -- open_date, close_date, account_status all use schema-level defaults
    INSERT INTO account (account_id, customer_id, account_password)
    VALUES (p_account_id, p_customer_id, p_account_password);

    -- Only call deposit_cash if there is an actual amount to deposit.
    -- Skipping this when p_initial_balance = 0 avoids tripping the
    -- "amount must be > 0" guard inside deposit_cash.
    IF p_initial_balance > 0 THEN
        -- deposit_cash handles the FOR UPDATE lock, trans + deposit TPT logging,
        -- and the balance credit — all in one atomic call
        CALL deposit_cash(p_account_id, p_employee_id, p_initial_balance, v_description);
    END IF;

    RAISE NOTICE 'Account "%" opened for customer ID % with initial balance %.', 
        p_account_id, p_customer_id, p_initial_balance;
END;
$$;

-- ------------------------------------------------------------
-- PROCEDURE: close_account
-- Closes an existing open account.
-- Blocked if the account still carries a non-zero balance —
-- customer must withdraw all funds first.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE close_account(
    p_account_id VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance NUMERIC(22,3);   -- Matches the schema column type exactly
BEGIN
    -- Guard: account must exist and currently be open
    SELECT balance INTO v_balance
    FROM account
    WHERE account_id = p_account_id AND account_status = 'open';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account "%" does not exist or is already closed.', p_account_id;
    END IF;

    -- Guard: balance must be fully withdrawn before closing
    IF v_balance > 0 THEN
        RAISE EXCEPTION 'Cannot close account "%". Remaining balance: %. Withdraw all funds first.', 
            p_account_id, v_balance;
    END IF;

    UPDATE account
    SET account_status = 'closed',
        close_date     = CURRENT_DATE
    WHERE account_id = p_account_id;

    RAISE NOTICE 'Account "%" closed successfully on %.', p_account_id, CURRENT_DATE;
END;
$$;


-- ============================================================
-- SECTION 5: TRANSACTION PROCEDURES
-- ============================================================

-- ------------------------------------------------------------
-- PROCEDURE: in_bank_transfer
-- Transfers money between two accounts within this bank.
-- Locks both rows with FOR UPDATE before touching balances to
-- prevent race conditions under concurrent sessions.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE in_bank_transfer(
    p_source_account_id      VARCHAR(255),
    p_destination_account_id VARCHAR(255),
    p_amount                 NUMERIC(22,3),
    p_description            VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_source_balance NUMERIC(22,3);
    v_new_trans_id   INT;
BEGIN
    -- Guard: source and destination cannot be the same account
    IF p_source_account_id = p_destination_account_id THEN
        RAISE EXCEPTION 'Source and destination accounts cannot be the same.';
    END IF;

    -- Guard: amount must be positive
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Transfer amount must be greater than zero. Provided: %', p_amount;
    END IF;

    -- Lock and validate source account
    -- FOR UPDATE holds a row-level lock until COMMIT, preventing concurrent balance changes
    SELECT balance INTO v_source_balance
    FROM account
    WHERE account_id = p_source_account_id AND account_status = 'open'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Source account "%" does not exist or is closed.', p_source_account_id;
    END IF;

    -- Lock and validate destination account
    PERFORM 1
    FROM account
    WHERE account_id = p_destination_account_id AND account_status = 'open'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Destination account "%" does not exist or is closed.', p_destination_account_id;
    END IF;

    -- Guard: source account must have sufficient funds
    IF p_amount > v_source_balance THEN
        RAISE EXCEPTION 'Insufficient funds in account "%". Available: %, Requested: %',
            p_source_account_id, v_source_balance, p_amount;
    END IF;

    -- Debit source, credit destination
    UPDATE account SET balance = balance - p_amount WHERE account_id = p_source_account_id;
    UPDATE account SET balance = balance + p_amount WHERE account_id = p_destination_account_id;

    -- Log base transaction (TPT: step 1 of 2)
    INSERT INTO trans (affected_account_id, trans_amount, trans_description, trans_status)
    VALUES (p_source_account_id, p_amount, p_description, 'finished')
    RETURNING trans_id INTO v_new_trans_id;

    -- Log in-bank sub-type record (TPT: step 2 of 2)
    INSERT INTO in_bank_trans (trans_id, destination_account_id)
    VALUES (v_new_trans_id, p_destination_account_id);

    RAISE NOTICE 'Transferred % from "%" to "%". Transaction ID: %.',
        p_amount, p_source_account_id, p_destination_account_id, v_new_trans_id;
END;
$$;


-- ------------------------------------------------------------
-- PROCEDURE: out_bank_transfer
-- Records an outgoing wire to an account at an external bank.
-- Debits the internal source account only — the receiving bank
-- handles the credit on their side.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE out_bank_transfer(
    p_source_account_id  VARCHAR(255),
    p_amount             NUMERIC(22,3),
    p_description        VARCHAR(255),
    p_out_bank_branch    VARCHAR(255),   -- Must match out_bank_trans.out_bank_branch column name
    p_out_bank_id        VARCHAR(255)    -- Must match out_bank_trans.out_bank_id column name
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance      NUMERIC(22,3);
    v_new_trans_id INT;
BEGIN
    -- Guard: amount must be positive
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Transfer amount must be greater than zero. Provided: %', p_amount;
    END IF;

    -- Lock and validate source account
    SELECT balance INTO v_balance
    FROM account
    WHERE account_id = p_source_account_id AND account_status = 'open'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Source account "%" does not exist or is closed.', p_source_account_id;
    END IF;

    -- Guard: sufficient funds
    IF p_amount > v_balance THEN
        RAISE EXCEPTION 'Insufficient funds in account "%". Available: %, Requested: %',
            p_source_account_id, v_balance, p_amount;
    END IF;

    -- Debit internal account
    UPDATE account
    SET balance = balance - p_amount
    WHERE account_id = p_source_account_id;

    -- Log base transaction (TPT: step 1 of 2)
    INSERT INTO trans (affected_account_id, trans_amount, trans_description, trans_status)
    VALUES (p_source_account_id, p_amount, p_description, 'finished')
    RETURNING trans_id INTO v_new_trans_id;

    -- Log out-bank sub-type record (TPT: step 2 of 2)
    -- Column names must match schema: out_bank_branch, out_bank_id
    INSERT INTO out_bank_trans (trans_id, destination_bank_branch, destination_bank_id)
    VALUES (v_new_trans_id, p_out_bank_branch, p_out_bank_id);

    RAISE NOTICE 'Wire of % from "%" to external account "%" at "%" completed. Transaction ID: %.',
        p_amount, p_source_account_id, p_out_bank_id, p_out_bank_branch, v_new_trans_id;
END;
$$;


-- ------------------------------------------------------------
-- PROCEDURE: pay_bill
-- Pays a utility / service bill by debiting a customer account.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE pay_bill(
    p_account_id  VARCHAR(255),
    p_amount      NUMERIC(22,3),
    p_description VARCHAR(255),
    p_bill_type   VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance      NUMERIC(22,3);
    v_new_trans_id INT;
BEGIN
    -- Guard: amount must be positive
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Bill amount must be greater than zero. Provided: %', p_amount;
    END IF;

    -- Lock and validate account
    SELECT balance INTO v_balance
    FROM account
    WHERE account_id = p_account_id AND account_status = 'open'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account "%" does not exist or is closed.', p_account_id;
    END IF;

    -- Guard: sufficient funds
    IF v_balance < p_amount THEN
        RAISE EXCEPTION 'Insufficient funds in account "%". Available: %, Required: %',
            p_account_id, v_balance, p_amount;
    END IF;

    -- Log base transaction (TPT: step 1 of 2)
    INSERT INTO trans (affected_account_id, trans_amount, trans_description, trans_status)
    VALUES (p_account_id, p_amount, p_description, 'finished')
    RETURNING trans_id INTO v_new_trans_id;

    -- Log bill sub-type record (TPT: step 2 of 2)
    INSERT INTO bill (trans_id, bill_type)
    VALUES (v_new_trans_id, p_bill_type);

    -- Debit account
    UPDATE account
    SET balance = balance - p_amount
    WHERE account_id = p_account_id;

    RAISE NOTICE '% bill of % paid from account "%". Transaction ID: %.',
        p_bill_type, p_amount, p_account_id, v_new_trans_id;
END;
$$;


-- ------------------------------------------------------------
-- PROCEDURE: withdraw_cash
-- Processes a cash withdrawal at a branch teller.
-- Blocks inactive employees from processing transactions.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE withdraw_cash(
    p_account_id  VARCHAR(255),
    p_employee_id INT,
    p_amount      NUMERIC(22,3),
    p_description VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance      NUMERIC(22,3);
    v_new_trans_id INT;
BEGIN
    -- Guard: amount must be positive
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Withdrawal amount must be greater than zero. Provided: %', p_amount;
    END IF;

    -- Guard: employee must exist AND be currently active
    -- Inactive employees (resigned/terminated) are not allowed to process transactions
    IF NOT EXISTS (SELECT 1 FROM employee WHERE employee_id = p_employee_id AND emp_status = 'active') THEN
        RAISE EXCEPTION 'Employee ID % does not exist or is inactive.', p_employee_id;
    END IF;

    -- Lock and validate account
    SELECT balance INTO v_balance
    FROM account
    WHERE account_id = p_account_id AND account_status = 'open'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account "%" does not exist or is closed.', p_account_id;
    END IF;

    -- Guard: sufficient funds
    IF v_balance < p_amount THEN
        RAISE EXCEPTION 'Insufficient funds in account "%". Available: %, Requested: %',
            p_account_id, v_balance, p_amount;
    END IF;

    -- Log base transaction (TPT: step 1 of 2)
    INSERT INTO trans (affected_account_id, trans_amount, trans_description, trans_status)
    VALUES (p_account_id, p_amount, p_description, 'finished')
    RETURNING trans_id INTO v_new_trans_id;

    -- Log withdraw sub-type record (TPT: step 2 of 2)
    INSERT INTO withdraw (trans_id, employee_id)
    VALUES (v_new_trans_id, p_employee_id);

    -- Debit account
    UPDATE account
    SET balance = balance - p_amount
    WHERE account_id = p_account_id;

    RAISE NOTICE 'Withdrawal of % from "%" processed by employee ID %. Transaction ID: %.',
        p_amount, p_account_id, p_employee_id, v_new_trans_id;
END;
$$;


-- ------------------------------------------------------------
-- PROCEDURE: deposit_cash
-- Processes a cash deposit at a branch teller.
-- Blocks inactive employees from processing transactions.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE deposit_cash(
    p_account_id  VARCHAR(255),
    p_employee_id INT,
    p_amount      NUMERIC(22,3),
    p_description VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_new_trans_id INT;
BEGIN
    -- Guard: amount must be positive
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Deposit amount must be greater than zero. Provided: %', p_amount;
    END IF;

    -- Guard: employee must exist AND be currently active
    IF NOT EXISTS (SELECT 1 FROM employee WHERE employee_id = p_employee_id AND emp_status = 'active') THEN
        RAISE EXCEPTION 'Employee ID % does not exist or is inactive.', p_employee_id;
    END IF;

    -- Validate account exists and is open
    -- Using SELECT + FOR UPDATE (not inside NOT EXISTS — that is invalid PostgreSQL syntax)
    PERFORM 1
    FROM account
    WHERE account_id = p_account_id AND account_status = 'open'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account "%" does not exist or is closed.', p_account_id;
    END IF;

    -- Log base transaction (TPT: step 1 of 2)
    INSERT INTO trans (affected_account_id, trans_amount, trans_description, trans_status)
    VALUES (p_account_id, p_amount, p_description, 'finished')
    RETURNING trans_id INTO v_new_trans_id;

    -- Log deposit sub-type record (TPT: step 2 of 2)
    INSERT INTO deposit (trans_id, employee_id)
    VALUES (v_new_trans_id, p_employee_id);

    -- Credit account
    UPDATE account
    SET balance = balance + p_amount
    WHERE account_id = p_account_id;

    RAISE NOTICE 'Deposit of % to "%" processed by employee ID %. Transaction ID: %.',
        p_amount, p_account_id, p_employee_id, v_new_trans_id;
END;
$$;

