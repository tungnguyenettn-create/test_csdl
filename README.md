# 🏦 Banking Database – Setup & Testing Guide

## 1. Connect to PostgreSQL (Windows)

Với windows mở terminal và chạy:

```bash
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

Với ubuntu mở terminal và chạy:
```bash
sudo -u postgres psql
```

---

## 2. Initialize Database

Tạo database mới để test:

```sql
DROP DATABASE IF EXISTS test;
CREATE DATABASE test;
\c test
```

---

## 3. Create Schema

Chạy file tạo schema:

```sql
\i create_database.sql
```

Kiểm tra schema:

```sql
\dt              -- list all tables
\d branch
\d employee
\d customer
\d account
\d trans
\d in_bank_trans
\d out_bank_trans
\d bill
\d withdraw
\d deposit
```

---

## 4. Load Stored Procedures

```sql
\i procedure.sql
```

---

## 5. Run Test Script

```sql
\i test.sql
```

---
## 6. Procedure Usage

Tất cả stored procedures được gọi bằng cú pháp:

```sql
CALL procedure_name(parameters);
```

---

### 🏢 Branch

```sql
CALL create_branch(
    p_city VARCHAR,
    p_branch_name VARCHAR
);
```

---

### 👨‍💼 Employee

```sql
CALL create_employee(
    p_branch_id INT,
    p_employee_name VARCHAR,
    p_identity_card VARCHAR,
    p_employee_password VARCHAR
);
```

```sql
CALL deactivate_employee(
    p_employee_id INT
);
```

---

### 👤 Customer

```sql
CALL create_customer(
    p_full_name VARCHAR,
    p_identity_card VARCHAR,
    p_nationality VARCHAR,
    p_dob DATE,
    p_city VARCHAR,
    p_address VARCHAR,
    p_branch_id INT
);
```

---

### 💳 Account

```sql
CALL create_account(
    p_account_id VARCHAR,
    p_customer_id INT,
    p_account_password VARCHAR,
    p_employee_id INT,
    p_initial_balance NUMERIC DEFAULT 0
);
```

```sql
CALL close_account(
    p_account_id VARCHAR
);
```

---

### 💸 Transactions

#### 🔁 In-bank transfer

```sql
CALL in_bank_transfer(
    p_source_account_id VARCHAR,
    p_destination_account_id VARCHAR,
    p_amount NUMERIC,
    p_description VARCHAR
);
```

---

#### 🌍 Out-bank transfer

```sql
CALL out_bank_transfer(
    p_source_account_id VARCHAR,
    p_amount NUMERIC,
    p_description VARCHAR,
    p_out_bank_branch VARCHAR,
    p_out_bank_id VARCHAR
);
```

---

#### 🧾 Pay bill

```sql
CALL pay_bill(
    p_account_id VARCHAR,
    p_amount NUMERIC,
    p_description VARCHAR,
    p_bill_type VARCHAR
);
```

---

#### 💵 Withdraw cash

```sql
CALL withdraw_cash(
    p_account_id VARCHAR,
    p_employee_id INT,
    p_amount NUMERIC,
    p_description VARCHAR
);
```

---

#### 💰 Deposit cash

```sql
CALL deposit_cash(
    p_account_id VARCHAR,
    p_employee_id INT,
    p_amount NUMERIC,
    p_description VARCHAR
);
```

---

## 📌 Notes

* `p_amount` phải > 0 trong tất cả các transaction
* `employee` phải **active** để thực hiện `withdraw` / `deposit`
* `account` phải ở trạng thái **open**
* Các procedure đều có **exception handling**, nên nếu sai sẽ báo lỗi rõ ràng

---


---

## 7. TODO / Testing Checklist

### Basic Operations

* [ ] Tạo mới:

  * branch
  * employee
  * customer
  * account

### Transaction Testing

* [ ] Test các loại giao dịch:

  * `in_bank_transfer`
  * `out_bank_transfer`
  * `pay_bill`
  * `withdraw_cash`
  * `deposit_cash`

### Constraint & Exception Testing

* [ ] `deactivate_employee` rồi thử:

  * withdraw / deposit → phải bị chặn

* [ ] `close_account` rồi thử:

  * thực hiện transaction → phải bị chặn

### Concurrency Testing

* [ ] Thực hiện update song song (2 session):

  * kiểm tra có xảy ra **lost update** không
  * verify `FOR UPDATE` lock hoạt động đúng

---

## 8. Notes

* Tất cả transaction procedures đều:

  * Validate input
  * Check business constraints
  * Dùng `FOR UPDATE` để tránh race condition

* Thiết kế sử dụng:

  * **TPT (Table Per Type)** cho transaction (`trans` + subtype tables)

---

## 9. Requirements

* PostgreSQL 15+
* `psql` CLI

---

## 10. Tips

Nếu bị lỗi:

```
psql is not recognized
```

→ cần add vào PATH:

```
C:\Program Files\PostgreSQL\15\bin
```

---

## Author Notes

Project này tập trung vào:

* Transaction safety
* Concurrency control
* Business rule enforcement bằng stored procedures
