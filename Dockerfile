# Sử dụng Python bản Alpine cho nhẹ, đồng bộ với Postgres của bạn
FROM python:3.10-alpine

# Cài đặt các tool hệ thống cần thiết (nếu thư viện python của bạn cần build C như psycopg2)
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev

# Đặt thư mục làm việc trong container
WORKDIR /app

# Copy file requirements vào trước để tận dụng cache của Docker
COPY requirements.txt .

# Cài đặt các dependency
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code nguồn vào container
COPY . .

# Mở port 5000 trong container
EXPOSE 5000

# Lệnh để chạy ứng dụng của bạn
CMD ["python3", "app.py"]