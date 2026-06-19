from flask import Blueprint, request, jsonify
import jwt
import datetime

# Gom hết đồ bảo mật từ auth.py về đây
from auth import JWT_SECRET, token_required  
import account_db 

customer_bp = Blueprint('customer', __name__)

# 1. API ĐĂNG NHẬP
@customer_bp.route('/api/customer/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    result = account_db.login_db(username, password)
    
    if result == 2: 
        payload = {
            "customer_id": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1) 
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return jsonify({"status": "success", "token": token}), 200
    elif result == 1:
        return jsonify({"status": "error", "message": "Sai mật khẩu!"}), 401
    elif result == 0:
        return jsonify({"status": "error", "message": "Tài khoản không tồn tại!"}), 404
    else:
        return jsonify({"status": "error", "message": "Lỗi kết nối Database!"}), 500


# 2. API LẤY SỐ DƯ (Gọi decorator từ auth.py cực mượt)
@customer_bp.route('/api/customer/balance', methods=['GET'])
@token_required
def get_balance(current_user): 
    balance = account_db.get_balance(current_user)
    return jsonify({
        "status": "success", 
        "account_id": current_user, 
        "balance": balance
    }), 200


# 3. API LẤY THÔNG TIN CÁ NHÂN
@customer_bp.route('/api/customer/my-info', methods=['GET'])
@token_required
def get_my_info(current_user):
    user_info = account_db.get_user_from_account(current_user)
    if user_info:
        return jsonify({"status": "success", "data": user_info}), 200
    return jsonify({"status": "error", "message": "Không tìm thấy thông tin tài khoản"}), 404


# 4. API ĐỔI MẬT KHẨU
@customer_bp.route('/api/customer/change-password', methods=['PUT'])
@token_required
def change_password(current_user):
    data = request.get_json()
    new_password = data.get("new_password")
    
    if not new_password:
        return jsonify({"status": "error", "message": "Vui lòng nhập mật khẩu mới!"}), 400
        
    result = account_db.update_password(current_user, new_password)
    if result == 1:
        return jsonify({"status": "success", "message": "Đổi mật khẩu thành công!"}), 200
    else:
        return jsonify({"status": "error", "message": "Lỗi hệ thống không thể đổi mật khẩu"}), 500