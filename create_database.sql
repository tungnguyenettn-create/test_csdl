-- ============================================================
-- DATABASE: BANK
-- Description: Schema for a banking system covering branches,
--              employees, customers, accounts, and all types
--              of transactions (in-bank, out-bank, bill,
--              withdraw, deposit).
-- ============================================================


-- ============================================================
-- SECTION 0: CLEANUP
-- Drop all tables in reverse dependency order to avoid FK
-- constraint violations during re-runs / development resets.
-- ============================================================

DROP TABLE IF EXISTS deposit;
DROP TABLE IF EXISTS withdraw;
DROP TABLE IF EXISTS bill;
DROP TABLE IF EXISTS out_bank_trans;
DROP TABLE IF EXISTS in_bank_trans;
DROP TABLE IF EXISTS trans;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS branch;

-- Drop custom ENUM types if they already exist
DROP TYPE IF EXISTS a_status;
DROP TYPE IF EXISTS t_status;
DROP TYPE IF EXISTS e_status;


-- ============================================================
-- SECTION 1: ENUM TYPE DEFINITIONS
-- Defined upfront so all CREATE TABLE statements can reference
-- them freely without ordering concerns.
-- ============================================================

-- Employee employment status
-- 'active'   — currently working, allowed to process transactions
-- 'inactive' — no longer working, blocked from processing new transactions
--              but their historical withdraw/deposit records are preserved
CREATE TYPE e_status AS ENUM ('active', 'inactive');

-- Account lifecycle status
-- 'open'   — account is active and usable
-- 'closed' — account has been closed, no further transactions allowed
CREATE TYPE a_status AS ENUM ('open', 'closed');

-- Transaction outcome status
-- 'finished'  — transaction completed successfully
-- 'cancelled' — transaction was attempted but did not complete
CREATE TYPE t_status AS ENUM ('finished', 'cancelled');


-- ============================================================
-- SECTION 2: BRANCH TABLE
-- No foreign-key dependencies — created first.
-- ============================================================

-- ------------------------------------------------------------
-- TABLE: branch
-- Represents a physical bank branch location.
-- All employees and customers are registered under a branch.
-- ------------------------------------------------------------
CREATE TABLE branch (
    branch_id   INT          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city        VARCHAR(255),                   -- City where the branch is located
    branch_name VARCHAR(255) UNIQUE NOT NULL    -- Display name; must be unique across all branches
);


-- ============================================================
-- SECTION 3: EMPLOYEE TABLE
-- Depends on: branch
-- ============================================================

-- ------------------------------------------------------------
-- TABLE: employee
-- Stores bank staff assigned to a specific branch.
-- Employees with status 'inactive' (resigned / terminated)
-- are retained in the table so that historical withdraw and
-- deposit records still have a valid FK reference, but they
-- are blocked from processing new transactions at the
-- procedure level.
-- ------------------------------------------------------------
CREATE TABLE employee (
    employee_id       INT          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id         INT          NOT NULL,                -- Branch this employee belongs to (FK → branch)
    employee_name     VARCHAR(255) NOT NULL,
    identity_card     VARCHAR(255) UNIQUE NOT NULL,         -- National ID — unique per person
    employee_password VARCHAR(255) NOT NULL,                -- Store bcrypt/argon2 hash, never plaintext
    emp_status        e_status     DEFAULT 'active'         -- 'active' = working | 'inactive' = no longer employed
);

ALTER TABLE employee
    ADD CONSTRAINT fk_employee_branch
    FOREIGN KEY (branch_id)
    REFERENCES branch (branch_id);


-- ============================================================
-- SECTION 4: CUSTOMER TABLE
-- Depends on: branch
-- ============================================================

-- ------------------------------------------------------------
-- TABLE: customer
-- Stores personal information for each bank customer.
-- A customer is registered at a home branch and may hold
-- one or more accounts.
-- ------------------------------------------------------------
CREATE TABLE customer (
    customer_id   INT          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id     INT          NOT NULL,                -- Home branch (FK → branch)
    full_name     VARCHAR(255) NOT NULL,
    identity_card VARCHAR(255) UNIQUE NOT NULL,         -- National ID — required and unique
    nationality   VARCHAR(255),
    dob           DATE         NOT NULL,                -- Date of birth — used for age validation
    city          VARCHAR(255),
    address       VARCHAR(255)
);

ALTER TABLE customer
    ADD CONSTRAINT fk_customer_branch
    FOREIGN KEY (branch_id)
    REFERENCES branch (branch_id);


-- ============================================================
-- SECTION 5: ACCOUNT TABLE
-- Depends on: customer
-- ============================================================

-- ------------------------------------------------------------
-- TABLE: account
-- Represents a bank account owned by a customer.
-- account_id is a bank-defined string (e.g. "VCB-0001234")
-- rather than a system integer to match real-world conventions.
-- ------------------------------------------------------------
CREATE TABLE account (
    account_id       VARCHAR(255) PRIMARY KEY,
    customer_id      INT          NOT NULL,                      -- Owner of this account (FK → customer)
    account_password VARCHAR(255) NOT NULL,                      -- Store hashed PIN, never plaintext
    balance          NUMERIC(22,3)        DEFAULT 0,             -- Current balance; always >= 0
    open_date        DATE                 DEFAULT CURRENT_DATE,  -- Defaults to today when opened
    close_date       DATE                 DEFAULT NULL,          -- NULL while the account is still active
    account_status   a_status             DEFAULT 'open',        -- Lifecycle state; starts as 'open'
    CHECK (balance >= 0)                                         -- Hard guard: balance can never go negative
);

ALTER TABLE account
    ADD CONSTRAINT fk_account_customer
    FOREIGN KEY (customer_id)
    REFERENCES customer (customer_id)
    ON DELETE RESTRICT;   -- Prevent deleting a customer who still has accounts


-- ============================================================
-- SECTION 6: TRANSACTION TABLES (TPT Inheritance)
--
-- Design pattern: Table-Per-Type (TPT)
--   • trans          — base record shared by ALL transaction types
--   • in_bank_trans  — transfer between two accounts in this bank
--   • out_bank_trans — outgoing wire to an external bank
--   • bill           — utility / service bill payment
--   • withdraw       — cash withdrawal processed by a teller
--   • deposit        — cash deposit processed by a teller
--
-- Each sub-type table's PK is also a FK back to trans (1-to-1).
-- `affected_account_id` in trans always refers to the internal
-- account that initiated or is directly involved in the event.
-- ============================================================

-- ------------------------------------------------------------
-- TABLE: trans (base transaction)
-- One row per financial event regardless of type.
-- Sub-type-specific columns live in the matching child table.
--
-- affected_account_id: the internal account involved in
-- this transaction (sender for transfers/wires/bills/withdrawals,
-- receiver for deposits). Neutral naming avoids misleading
-- semantics across all five sub-types.
-- ------------------------------------------------------------
CREATE TABLE trans (
    trans_id            INT           GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    affected_account_id VARCHAR(255)  NOT NULL,      -- The internal account involved (FK → account)
    trans_amount        NUMERIC(22,3) NOT NULL,       -- Value of the transaction; must be > 0
    trans_description   VARCHAR(255),                 -- Optional free-text memo or reference
    trans_time          TIMESTAMP     DEFAULT NOW(),  -- Exact date + time the transaction occurred
    trans_status        t_status      NOT NULL,       -- Outcome: 'finished' or 'cancelled'
    CHECK (trans_amount > 0)                          -- Guard: amounts must always be positive
);

ALTER TABLE trans
    ADD CONSTRAINT fk_trans_affected_account
    FOREIGN KEY (affected_account_id)
    REFERENCES account (account_id);


-- ------------------------------------------------------------
-- TABLE: in_bank_trans (intra-bank transfer)
-- Extends trans for transfers between two accounts within
-- this bank.
--   affected_account_id (in trans) = the SOURCE account (debited)
--   destination_account_id         = the DESTINATION account (credited)
-- ------------------------------------------------------------
CREATE TABLE in_bank_trans (
    trans_id               INT          PRIMARY KEY,  -- 1-to-1 with trans
    destination_account_id VARCHAR(255) NOT NULL      -- Receiving account (FK → account)
);

ALTER TABLE in_bank_trans
    ADD CONSTRAINT fk_in_bank_trans_id
    FOREIGN KEY (trans_id)
    REFERENCES trans (trans_id);

ALTER TABLE in_bank_trans
    ADD CONSTRAINT fk_in_bank_trans_destination
    FOREIGN KEY (destination_account_id)
    REFERENCES account (account_id);


-- ------------------------------------------------------------
-- TABLE: out_bank_trans (inter-bank / outgoing wire transfer)
-- Extends trans for transfers to accounts at external banks.
-- No FK on out_bank_id — the destination is outside this system.
--   affected_account_id (in trans) = the internal account debited
-- ------------------------------------------------------------
CREATE TABLE out_bank_trans (
    trans_id        INT          PRIMARY KEY,           -- 1-to-1 with trans
    destination_bank_branch VARCHAR(255) NOT NULL,      -- Branch name / code of the receiving external bank
    destination_bank_id     VARCHAR(255) NOT NULL       -- Account identifier at the external bank
);

ALTER TABLE out_bank_trans
    ADD CONSTRAINT fk_out_bank_trans_id
    FOREIGN KEY (trans_id)
    REFERENCES trans (trans_id);


-- ------------------------------------------------------------
-- TABLE: bill
-- Extends trans for bill payments (utilities, phone, insurance).
--   affected_account_id (in trans) = the account paying the bill
-- ------------------------------------------------------------
CREATE TABLE bill (
    trans_id  INT          PRIMARY KEY,   -- 1-to-1 with trans
    bill_type VARCHAR(255) NOT NULL       -- Service category: 'Electricity', 'Internet', etc.
);

ALTER TABLE bill
    ADD CONSTRAINT fk_bill_trans_id
    FOREIGN KEY (trans_id)
    REFERENCES trans (trans_id);


-- ------------------------------------------------------------
-- TABLE: withdraw
-- Extends trans for cash withdrawals processed at a teller.
--   affected_account_id (in trans) = the account being debited
--   employee_id                    = the teller who processed it
--
-- NOTE: employee FK intentionally has no ON DELETE RESTRICT so
-- that historical records survive if an employee becomes inactive.
-- Inactive employees are blocked at the procedure level, not here.
-- ------------------------------------------------------------
CREATE TABLE withdraw (
    trans_id    INT PRIMARY KEY,   -- 1-to-1 with trans
    employee_id INT NOT NULL       -- Teller who handled this withdrawal (FK → employee)
);

ALTER TABLE withdraw
    ADD CONSTRAINT fk_withdraw_trans_id
    FOREIGN KEY (trans_id)
    REFERENCES trans (trans_id);

ALTER TABLE withdraw
    ADD CONSTRAINT fk_withdraw_employee_id
    FOREIGN KEY (employee_id)
    REFERENCES employee (employee_id);


-- ------------------------------------------------------------
-- TABLE: deposit
-- Extends trans for cash deposits processed at a teller.
--   affected_account_id (in trans) = the account being credited
--   employee_id                    = the teller who processed it
--
-- NOTE: Same employee FK design rationale as withdraw above.
-- ------------------------------------------------------------
CREATE TABLE deposit (
    trans_id    INT PRIMARY KEY,   -- 1-to-1 with trans
    employee_id INT NOT NULL       -- Teller who handled this deposit (FK → employee)
);

ALTER TABLE deposit
    ADD CONSTRAINT fk_deposit_trans_id
    FOREIGN KEY (trans_id)
    REFERENCES trans (trans_id);

ALTER TABLE deposit
    ADD CONSTRAINT fk_deposit_employee_id
    FOREIGN KEY (employee_id)
    REFERENCES employee (employee_id);


-- ============================================================
-- SECTION 7: INDEXES
-- Added on high-frequency lookup and JOIN columns.
-- ============================================================

-- Quickly find all accounts belonging to a customer
CREATE INDEX idx_account_customer_id       ON account  (customer_id);

-- Quickly find all transactions for a given internal account
CREATE INDEX idx_trans_affected_account_id ON trans     (affected_account_id);

-- Quickly look up transactions by time range (e.g. monthly statements)
CREATE INDEX idx_trans_time                ON trans     (trans_time);

-- Quickly find all employees in a branch
CREATE INDEX idx_employee_branch_id        ON employee  (branch_id);

-- Quickly find all customers registered at a branch
CREATE INDEX idx_customer_branch_id        ON customer  (branch_id);