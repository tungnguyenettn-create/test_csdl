DO $$
DECLARE
    i INT;
    v_bill_id INT;
    v_source_acc VARCHAR(255);
    v_dest_acc VARCHAR(255);
    v_provider_name VARCHAR(255);
BEGIN
    -- ============================================================
    -- STEP 1: Core Bill Types (Exactly 4 rows)
    -- ============================================================
    CALL add_bill_type('Electricity');
    CALL add_bill_type('Water');
    CALL add_bill_type('Internet');
    CALL add_bill_type('Mobile');

    -- ============================================================
    -- STEP 2: Branches, External Banks, and Bill Providers (30 rows each)
    -- ============================================================
    FOR i IN 1..30 LOOP
        CALL create_branch('City ' || i, 'Branch ' || i);
        CALL add_out_bank('EXT-BANK-' || i, 'External Bank Branch ' || i);
        
        v_bill_id := ((i - 1) % 4) + 1; 
        
        CASE v_bill_id
            WHEN 1 THEN v_provider_name := 'EVN Power Co ' || i;
            WHEN 2 THEN v_provider_name := 'Clean Water Corp ' || i;
            WHEN 3 THEN v_provider_name := 'NetSpeed Telecom ' || i;
            ELSE v_provider_name := 'Mobility Cell ' || i;
        END CASE;
        
        CALL add_bill_provider(v_provider_name, v_bill_id);
    END LOOP;

    -- ============================================================
    -- STEP 3: Employees & Customers (30 rows each)
    -- ============================================================
    FOR i IN 1..30 LOOP
        CALL create_employee(i, 'Teller ' || i, 'EMP-ID-' || i, 'hashed_pwd');
        
        CALL create_customer(
            'Customer ' || i, 
            'CUST-ID-' || i, 
            'VN', 
            ('1990-01-01'::DATE + (i || ' days')::INTERVAL)::DATE, 
            'City ' || i, 
            'Address ' || i, 
            i
        );
    END LOOP;

    -- ============================================================
    -- STEP 4: Accounts (30 rows)
    -- ============================================================
    FOR i IN 1..30 LOOP
        CALL create_account('ACC-' || lpad(i::text, 5, '0'), i, 'pin_hash', i, 75000.000);
    END LOOP;

    -- ============================================================
    -- STEP 5: In-Bank Transfers (30 rows)
    -- ============================================================
    FOR i IN 1..30 LOOP
        v_source_acc := 'ACC-' || lpad(i::text, 5, '0');
        v_dest_acc   := 'ACC-' || lpad(((i % 30) + 1)::text, 5, '0');
        
        CALL in_bank_transfer(v_source_acc, v_dest_acc, 150.000, 'Split dinner bill');
    END LOOP;

    -- ============================================================
    -- STEP 6: Out-Bank Transfers (30 rows)
    -- ============================================================
    FOR i IN 1..30 LOOP
        v_source_acc := 'ACC-' || lpad(i::text, 5, '0');
        CALL sp_out_bank_transaction(v_source_acc, 'EXT-BANK-' || i, 250.000, 'Online purchase wire');
    END LOOP;

    -- ============================================================
    -- STEP 7: Bill Payments (30 rows)
    -- Beautifully clean signature: account_id, provider_id, amount
    -- ============================================================
    FOR i IN 1..30 LOOP
        v_source_acc := 'ACC-' || lpad(i::text, 5, '0');
        CALL sp_pay_bill(v_source_acc, i, 65.500); 
    END LOOP;

    -- ============================================================
    -- STEP 8: Cash Withdrawals (30 rows)
    -- ============================================================
    FOR i IN 1..30 LOOP
        v_source_acc := 'ACC-' || lpad(i::text, 5, '0');
        CALL withdraw_cash(v_source_acc, i, 400.000, 'Weekend pocket cash');
    END LOOP;

END $$;