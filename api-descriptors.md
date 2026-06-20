
---

## 🔑 NHÓM API TÀI KHOẢN (`customer_bp`)

### 1. API Đăng nhập

* **URL:** `/api/customer/login`
* **Method:** `POST`
* **Headers:** `Content-Type: application/json`
* **Body (JSON):**

```json
{
  "username": "ACC-00024",
  "password": "pin_hash"
}

```

* **Phản hồi thành công (200 OK):**

```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6IkFDQy0wMDAyNCIsImV4cCI6MTc4MTk0NDAwMH0..."
}

```

> 💡 **Lưu ý:** Hãy copy chuỗi `token` này để điền vào phần **Bearer Token** ở các API phía dưới cần bảo mật.

* **Phản hồi thất bại (401 Unauthorized - Sai mật khẩu):**

```json
{
  "status": "error",
  "message": "Sai mật khẩu!"
}

```

---

### 2. API Lấy số dư tài khoản

* **URL:** `/api/customer/balance`
* **Method:** `GET`
* **Headers:** `Authorization: Bearer <TOKEN_CỦA_BẠN>`
* **Phản hồi thành công (200 OK):**

```json
{
  "account_id": "ACC-00024",
  "balance": 5000000.00,
  "status": "success"
}

```

---

### 3. API Lấy thông tin cá nhân

* **URL:** `/api/customer/my-info`
* **Method:** `GET`
* **Headers:** `Authorization: Bearer <TOKEN_CỦA_BẠN>`
* **Phản hồi thành công (200 OK):**

```json
{
  "status": "success",
  "data": {
    "customer_id": "ACC-00024",
    "fullname": "customer1",
    "identity_card": "1",
    "phone": "0987654321"
  }
}

```

---

### 4. API Đổi mật khẩu

* **URL:** `/api/customer/change-password`
* **Method:** `PUT`
* **Headers:** * `Authorization: Bearer <TOKEN_CỦA_BẠN>`
* `Content-Type: application/json`


* **Body (JSON):**

```json
{
  "new_password": "new_pin_hash"
}

```

* **Phản hồi thành công (200 OK):**

```json
{
  "status": "success",
  "message": "Đổi mật khẩu thành công!"
}

```

---

### 5. API Quên tài khoản (Tìm bằng CCCD)

* **URL:** `/api/customer/forget-account`
* **Method:** `GET`
* **Headers:** `Content-Type: application/json`
* **Body (JSON):**

```json
{
  "indentiy-card": "1"
}

```

> 💡 **Lưu ý kiểm tra:** Do mã Flask hiện tại của bạn đang viết là dùng `request.get_json()` cho phương thức `GET`, nên khi test bằng Postman, bạn vẫn phải chọn tab **Body -> raw -> JSON** mặc dù phương thức là `GET` nhé.

* **Phản hồi thành công (200 OK):**

```json
{
  "status": "success",
  "account_id": "ACC-00024"
}

```

---

## 💸 NHÓM API GIAO DỊCH VÀ CHUYỂN TIỀN (`transfers_bp`)

### 6. API Chuyển tiền nội bộ

* **URL:** `/api/transfers/in_bank_transfer`
* **Method:** `POST`
* **Headers:** * `Authorization: Bearer <TOKEN_CỦA_BẠN>`
* `Content-Type: application/json`


* **Body (JSON):** (Chuyển từ tài khoản trong token sang tài khoản đích)

```json
{
  "dest_account": "ACC-00015",
  "amount": "500000",
  "description": "Chuyen tien qua tang sinh nhat"
}

```

* **Phản hồi thành công (200 OK):**

```json
{
  "detail": "Tài khoản ACC-00024 đã chuyển thành công 500000 VNĐ đến ACC-00015.",
  "message": "Giao dịch hoàn tất thành công!",
  "result_code": 1,
  "status": "success"
}

```

* **Phản hồi thất bại (400 Bad Request - Ví dụ không đủ tiền):**

```json
{
  "message": "Thất bại: Tài khoản không đủ số dư.",
  "result_code": 4,
  "status": "error"
}

```

---

### 7. API Chuyển tiền liên ngân hàng

* **URL:** `/api/transfers/out_bank_transfer`
* **Method:** `POST`
* **Headers:** * `Authorization: Bearer <TOKEN_CỦA_BẠN>`
* `Content-Type: application/json`


* **Body (JSON):**

```json
{
  "desc_bank": "Agribank",
  "desc_acc": "9999999999",
  "amount": "200000",
  "description": "Thanh toan tien mua do"
}

```

* **Phản hồi thành công (200 OK):**

```json
{
  "detail": "Tài khoản ACC-00024 đã chuyển thành công 200000 VNĐ đến STK 9999999999 tại ngân hàng Agribank.",
  "message": "Giao dịch hoàn tất thành công!",
  "result_code": 1,
  "status": "success"
}

```

---

### 8. API Lấy danh sách ngân hàng liên kết được hỗ trợ

* **URL:** `/api/transfers/supported-banks`
* **Method:** `GET`
* **Headers:** `Authorization: Bearer <TOKEN_CỦA_BẠN>`
* **Phản hồi thành công (200 OK):**

```json
{
  "banks": ["36 BANK", "Agribank", "Vietcombank", "BIDV"],
  "status": "success"
}

```

---

### 9. API Thanh toán hóa đơn

* **URL:** `/api/transfers/pay-bill`
* **Method:** `POST`
* **Headers:** * `Authorization: Bearer <TOKEN_CỦA_BẠN>`
* `Content-Type: application/json`


* **Body (JSON):**

```json
{
  "provider_name": "EVN Hà Nội",
  "amount": "1250000"
}

```

* **Phản hồi thành công (200 OK):**

```json
{
  "detail": "Tài khoản ACC-00024 đã thanh toán hóa đơn thành công số tiền 1250000 VNĐ cho EVN Hà Nội.",
  "message": "Giao dịch hoàn tất thành công!",
  "result_code": 1,
  "status": "success"
}

```

---

### 10. API Lấy danh sách nhà cung cấp hóa đơn

* **URL:** `/api/transfers/supported-bill-providers?bill_type=Điện`
* **Method:** `GET`
* **Headers:** `Authorization: Bearer <TOKEN_CỦA_BẠN>`
* **Phản hồi thành công (200 OK):**

```json
{
  "bill_type": "Điện",
  "providers": ["EVN Hà Nội", "EVN TP.HCM", "EVN Miền Bắc"],
  "status": "success"
}

```

---

## 📜 NHÓM API LỊCH SỬ (`history_bp`)

### 11. API Xem lịch sử biến động số dư

* **URL 1 (Xem theo ngày):** `/api/customer/history?type=daily`
* **URL 2 (Xem theo tháng):** `/api/customer/history?type=monthly`
* **Method:** `GET`
* **Headers:** `Authorization: Bearer <TOKEN_CỦA_BẠN>`
* **Phản hồi thành công (200 OK - Xem theo ngày):**

```json
{
  "account_id": "ACC-00024",
  "message": "Lấy lịch sử biến động số dư 7 ngày qua thành công",
  "view_type": "daily",
  "status": "success",
  "data": [
    {
      "date": "19/06/2026",
      "amount": "-500000",
      "type": "Chuyển đi",
      "description": "Chuyen tien qua tang sinh nhat"
    },
    {
      "date": "15/06/2026",
      "amount": "+2000000",
      "type": "Nhận tiền",
      "description": "Nhan luong thang"
    }
  ]
}

```

---

## 📰 NHÓM API THÔNG TIN CHUNG (`info_bp`)

### 12. API Lấy danh sách chi nhánh ngân hàng

* **URL:** `/api/info/branches`
* **Method:** `GET` (Không cần Token)
* **Phản hồi thành công (200 OK):**

```json
{
  "status": "success",
  "branches": [
    {
      "id": 1,
      "name": "Chi nhánh Hà Nội",
      "address": "123 Đường Trần Hưng Đạo, Hoàn Kiếm, Hà Nội"
    },
    {
      "id": 2,
      "name": "Chi nhánh Cầu Giấy",
      "address": "26 Đường Xuân Thủy, Cầu Giấy, Hà Nội"
    }
  ]
}

```

---

### 13. API Lấy tin tức khuyến mãi / bảo trì

* **URL:** `/api/info/news`
* **Method:** `GET` (Không cần Token)
* **Phản hồi thành công (200 OK):**

```json
{
  "status": "success",
  "news": [
    {
      "title": "Lãi suất gửi tiết kiệm tháng 6 cực khủng lên tới 10%",
      "date": "18/06/2026"
    },
    {
      "title": "Bảo trì hệ thống từ 2h - 4h sáng chủ nhật",
      "date": "17/06/2026"
    }
  ]
}

```