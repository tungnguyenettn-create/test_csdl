from flask import Blueprint, jsonify
from auth import verify_customer_token  # Import hàm check token từ auth.py

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/customer/history', methods=['GET'])
def get_history():
    # Kiểm tra Token bảo mật
    user_info = verify_customer_token()
    if not user_info:
        return jsonify({"status": "error", "message": "Bạn chưa đăng nhập hoặc phiên hết hạn!"}), 401
        
    # Trả về danh sách lịch sử rác để test hiển thị lên Table JavaFX
    mock_transactions = [
        {"date": "2026-06-18 10:20", "type": "Chuyển khoản đi", "amount": "-500,000", "rem": "Tra tien do an Bach Khoa"},
        {"date": "2026-06-17 15:45", "type": "Nhận tiền đến", "amount": "+2,500,000", "rem": "Luong Thang 6"}
    ]
    
    return jsonify({
        "status": "success",
        "customer_id": user_info['customer_id'],
        "username": user_info['username'],
        "transactions": mock_transactions
    })