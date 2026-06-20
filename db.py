# db.py
import psycopg2

# Cấu hình kết nối tới PostgreSQL đang chạy trong Docker của bạn
DB_CONFIG = {
    "host": "postgres_test_container",        # Docker map port ra máy thật nên vẫn là localhost
    "port": 5432,                             # Cổng của Postgres trong Docker đã map ra ngoài
    "database": "test",                       # Tên database của bạn
    "user": "postgres",                       # Tài khoản
    "password": "ubuntu8s9reat"               # Mật khẩu bạn đã thiết lập
}

def get_db_connection():
    """
    Hàm tạo và trả về một kết nối (connection) mới tới Postgres Docker.
    Mỗi khi hàm con cần dùng SQL, chỉ cần gọi hàm này.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Lỗi kết nối Database Docker: {e}")
        return None

# KHỐI CODE TEST CHẠY ĐỘC LẬP
if __name__ == "__main__":
    print("--- ĐANG KIỂM TRA KẾT NỐI TỚI POSTGRES DOCKER ---")
    
    # 1. Thử gọi hàm kết nối
    connection = get_db_connection()
    
    if connection is not None:
        print("✅ Kết nối cơ sở dữ liệu THÀNH CÔNG!")
        
        try:
            # 2. Tạo cursor để chạy một câu lệnh SQL test đơn giản
            cur = connection.cursor()
            cur.execute("SELECT version();")
            db_version = cur.fetchone()
            
            print(f"🐳 Postgres trong Docker của bạn đang chạy phiên bản:")
            print(f"   => {db_version[0]}")
            
            # Đóng cursor
            cur.close()
        except Exception as sql_error:
            print(f"❌ Kết nối được nhưng chạy lệnh SQL test bị lỗi: {sql_error}")
        finally:
            # 3. Luôn đóng kết nối sau khi test xong
            connection.close()
            print("🔒 Đã ngắt kết nối an toàn.")
    else:
        print("❌ Kết nối THẤT BẠI! Bạn hãy check lại:")
        print("   1. Docker Container chứa Postgres đã bật chưa? (Lệnh: docker ps)")
        print("   2. Các thông tin port, user, password trong DB_CONFIG có đúng không?")