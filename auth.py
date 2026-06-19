# auth.py
from functools import wraps
from flask import request, jsonify
import jwt

# Chìa khóa bí mật của bạn (giữ nguyên cái cũ của bạn nhé)
JWT_SECRET = "ubuntu8s9reat_secret_key" 
# auth.py (Đoạn cập nhật hàm token_required)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Cách 1: Kiểm tra xem Header có gửi Authorization không (Chuẩn hệ thống)
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"status": "error", "message": "Sai định dạng Token!"}), 401
                
        # Cách 2: Nếu Header không có, tìm Token trên URL (?token=...) để test cho dễ
        if not token:
            token = request.args.get('token')

        # Nếu cả 2 cách đều không tìm thấy Token
        if not token:
            return jsonify({"status": "error", "message": "Không tìm thấy Token! Vui lòng đăng nhập trước."}), 401

        try:
            # Giải mã token
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user_account = data['customer_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "Token đã hết hạn!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "error", "message": "Token không hợp lệ!"}), 401

        return f(current_user_account, *args, **kwargs)
        
    return decorated