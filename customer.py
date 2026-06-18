from flask import Blueprint, request, jsonify
import jwt
import datetime
from auth import JWT_SECRET  # Import chìa khóa bí mật từ auth.py

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/api/customer/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    # Dữ liệu rác để test đăng nhập
    if username == "user123" and password == "password123":
        payload = {
            "customer_id": "CUST-9999",
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1) # Token sống 1 tiếng
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return jsonify({"status": "success", "token": token})
    
    return jsonify({"status": "error", "message": "Sai tài khoản hoặc mật khẩu rồi!"}), 401