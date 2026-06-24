# history_bp.py
from flask import Blueprint, request, jsonify
from auth import token_required  # Sử dụng lại file auth.py quản lý Token của bạn
import history_db

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/customer/history_all', methods=['GET'])
@token_required
def get_account_history_all(current_user): # current_user lấy tự động từ Token giống route cũ
    try:
        # Gọi hàm lấy toàn bộ lịch sử chi tiết từ history_db
        data = history_db.get_all_history(current_user)
        
        return jsonify({
            "status": "success",
            "account_id": current_user,
            "message": "Lấy toàn bộ lịch sử giao dịch chi tiết thành công",
            "total_records": len(data), # Tiện thể đếm luôn tổng số lượng giao dịch trả về
            "data": data
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Đã xảy ra lỗi khi lấy lịch sử giao dịch: {str(e)}"
        }), 500

@history_bp.route('/api/customer/history', methods=['GET'])
@token_required
def get_account_history(current_user): # current_user lấy tự động từ Token
    # Lấy tham số loại thống kê (?type=daily hoặc ?type=monthly). Mặc định là daily
    view_type = request.args.get('type', 'daily').lower()
    
    if view_type == 'daily':
        data = history_db.get_daily_history(current_user)
        message = "Lấy lịch sử biến động số dư 7 ngày qua thành công"
    elif view_type == 'monthly':
        data = history_db.get_monthly_history(current_user)
        message = "Lấy lịch sử biến động số dư theo tháng (1 năm qua) thành công"
    else:
        return jsonify({
            "status": "error", 
            "message": "Giá trị tham số 'type' không hợp lệ! Chỉ chấp nhận 'daily' hoặc 'monthly'."
        }), 400

    return jsonify({
        "status": "success",
        "account_id": current_user,
        "view_type": view_type,
        "message": message,
        "data": data
    }), 200
