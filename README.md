# 🏦 Hệ Thống Quản Lý Giao Dịch Ngân Hàng (Banking Transaction System)

Dự án triển khai hệ thống cơ sở dữ liệu PostgreSQL cho các nghiệp vụ ngân hàng (Chuyển khoản nội bộ, liên ngân hàng, thanh toán hóa đơn, nộp/rút tiền mặt) kết nối với mã nguồn xử lý giao dịch bằng Java JDBC.

Hệ thống sử dụng **Docker** để tự động hóa môi trường. Toàn bộ cấu trúc bảng (Schema), hàm (Functions), thủ tục (Procedures) và dữ liệu mẫu (Sample Data) sẽ được tự động cài đặt và cấu hình chỉ với một câu lệnh duy nhất.

---

## 🛠️ Yêu Cầu Cài Đặt
* **Docker** & **Docker Compose**
* **Java Development Kit (JDK) 17** hoặc mới hơn
* IDE: **IntelliJ IDEA** (khuyên dùng)

---

## 🚀 Hướng Dẫn Khởi Chạy Cơ Sở Dữ Liệu (Docker)

Vui lòng chọn hướng dẫn theo hệ điều hành bạn đang sử dụng:

### 1. Trên Ubuntu / Linux 🐧
* **Bước 1 (Quan trọng):** Tắt dịch vụ PostgreSQL cài trực tiếp trên máy (nếu có) để tránh xung đột cổng `5432` kết hợp với vào quyền admin:
  ```bash
  sudo systemctl stop postgresql
  sudo systemctl disable postgresql
  sudo su 
  ``` 
* **Bước 2** Mở Terminal tại thư mục gốc của dự án (nơi có file `docker-compose.yml`) và chạy: 
``` bash 
  docker compose up -d 
```
* **Bước 3** Kiểm tra container đã hoạt động hay chưa 
``` bash
  docker ps
```

### 2. Trên Windows 🪟

* **Bước 1** Bật ứng dụng docker desktop lên 
* **Bước 2** Mở powershell/git bash ở thư mục của dự án và chạy 
```bash 
  docker-compose up -d 
```
hoặc 
```bash 
  docker compose up -d 
```

