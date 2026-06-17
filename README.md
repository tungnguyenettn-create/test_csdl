# Hệ Thống Quản Lý Giao Dịch Ngân Hàng (Banking Transaction System)

Dự án này cung cấp một hệ thống cơ sở dữ liệu PostgreSQL hoàn chỉnh phục vụ cho các tính năng ngân hàng (chuyển khoản nội bộ, liên ngân hàng, thanh toán hóa đơn, nộp/rút tiền mặt) cùng mã nguồn Java JDBC kết nối xử lý giao dịch.

Hệ thống sử dụng **Docker** để tự động hóa quá trình cài đặt cơ sở dữ liệu, giúp khởi chạy toàn bộ schema, hàm (functions), thủ tục (stored procedures) và dữ liệu mẫu (sample data) chỉ với một câu lệnh duy nhất mà không cần cài đặt PostgreSQL thủ công trên máy.

---

## 🛠️ Yêu Cầu Hệ Thống

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã cài đặt các công cụ sau:
* **Docker** & **Docker Compose**
* **Java Development Kit (JDK) 17** hoặc mới hơn
* Một IDE bất kỳ (khuyên dùng **IntelliJ IDEA**)

---

## 🚀 Hướng Dẫn Khởi Chạy Cơ Sở Dữ Liệu (Docker)

Hệ thống hỗ trợ chạy mượt mà trên cả **Ubuntu (Linux)** và **Windows**. Vui lòng chọn hướng dẫn phù hợp với hệ điều hành của bạn dưới đây:

### 🐧 Trên Ubuntu / Linux

1. **Chuẩn bị và dọn dẹp cổng (Nếu có):**
   Nếu máy của bạn đang cài sẵn PostgreSQL chạy trực tiếp, hãy tắt nó đi để giải phóng cổng `5432`:
   ```bash
   sudo systemctl stop postgresql
   sudo systemctl disable postgresql