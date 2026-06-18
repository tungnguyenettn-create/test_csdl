from flask import Blueprint, request, jsonify
from auth import verify_customer_token  # Import hàm check token từ auth.py

transfers_bp = Blueprint('transfers', __name__)

@transfers_bp.route('/api/customer/transfer', methods=['POST'])
def transfer():
    # 1. Kiểm tra Token của khách hàng gửi lên
    user_info = verify_customer_token()
    if not user_info:
        return jsonify({"status": "error", "message": "Token không hợp lệ hoặc đã hết hạn!"}), 401
        
    # 2. Nhận dữ liệu giao dịch
    data = request.get_json()
    dest_acc = data.get("dest_account")
    amount = data.get("amount")
    
    # Trả về data rác báo thành công
    return jsonify({
        "status": "success",
        "result_code": 1,
        "message": f"Khách hàng {user_info['username']} đã chuyển thành công {amount} VNĐ đến tài khoản {dest_acc}."
    })