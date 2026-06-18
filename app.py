from flask import Flask, request, jsonify
import psycopg2
import decimal

app = Flask(__name__)

# Cấu hình kết nối Postgres (chỉ kết nối nội bộ trong máy bạn)
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "test",
    "user": "postgres",
    "password": "ubuntu8s9reat"
}

# Mã bí mật do bạn tự chế, chỉ có App Java và Backend của bạn biết
SECRET_API_KEY = "NganHangBachKhoa2026@SecureKey"

def verify_api_key():
    # Kiểm tra mã API Key trong Header của request
    api_key = request.headers.get("X-API-KEY")
    return api_key == SECRET_API_KEY

@app.route('/api/in-bank-transfer', methods=['POST'])

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "success",
        "message": "Hệ thống Backend Ngân Hàng đang hoạt động bảo mật. Cổng kết nối PostgreSQL đóng kín."
    }), 200
def in_bank_transfer():
    # 1. Kiểm tra bảo mật
    if not verify_api_key():
        return jsonify({"status": "error", "message": "Truy cập trái phép! API Key không hợp lệ."}), 401

    # 2. Lấy dữ liệu từ App Java gửi lên
    data = request.get_json()
    source_acc = data.get("source_account")
    dest_acc = data.get("dest_account")
    amount = data.get("amount")
    description = data.get("description")

    if not all([source_acc, dest_acc, amount]):
        return jsonify({"status": "error", "message": "Thiếu thông tin giao dịch"}), 400

    # 3. Kết nối DB nội bộ để thực thi Function
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Gọi Store Function fn_in_bank_transfer của bạn
        cur.execute("SELECT fn_in_bank_transfer(%s, %s, %s, %s);", (source_acc, dest_acc, amount, description))
        result_code = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        
        return jsonify({"status": "success", "result_code": result_code})
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Chạy backend ở cổng 5000
    app.run(host='0.0.0.0', port=5000)
