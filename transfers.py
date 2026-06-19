# transfers_bp.py
from flask import Blueprint, request, jsonify
from auth import token_required  # Tái sử dụng tấm khiên bảo mật từ file auth.py của bạn
import transfer_db

transfers_bp = Blueprint('transfers', __name__)

# API CHUYỂN TIỀN NỘI BỘ THỰC TẾ
@transfers_bp.route('/api/customer/transfer', methods=['POST'])
@token_required
def transfer(current_user): # current_user chính là tài khoản nguồn lấy tự động từ Token
    data = request.get_json()
    dest_acc = data.get("dest_account")
    amount = data.get("amount")
    description = data.get("description", f"Chuyen khoan tu {current_user}")
    
    # Kiểm tra dữ liệu đầu vào cơ bản trước khi gọi DB
    if not dest_acc or not amount:
        return jsonify({"status": "error", "message": "Vui lòng nhập tài khoản đích và số tiền!"}), 400
        
    try:
        amount_numeric = float(amount)
    except ValueError:
        return jsonify({"status": "error", "message": "Số tiền không hợp lệ!"}), 400

    # Gọi Stored Function từ DB thô lên xử lý trực tiếp
    result_code = transfer_db.in_bank_transfer(current_user, dest_acc, amount_numeric, description)
    message = transfer_db.get_result_message(result_code)
    
    # Nếu kết quả trả về từ DB là 1 tức là thành công
    if result_code == 1:
        return jsonify({
            "status": "success",
            "result_code": result_code,
            "message": message,
            "detail": f"Tài khoản {current_user} đã chuyển thành công {amount_numeric} VNĐ đến {dest_acc}."
        }), 200
    else:
        # Trả về lỗi cụ thể do Database quy định (Ví dụ: Không đủ số dư, tài khoản đích đóng,...)
        return jsonify({
            "status": "error",
            "result_code": result_code,
            "message": message
        }), 400

# API LẤY DANH SÁCH NGÂN HÀNG HỖ TRỢ (GET)
@transfers_bp.route('/api/customer/supported-banks', methods=['GET'])
@token_required
def get_banks(current_user):
    banks = transfer_db.get_supported_bank()
    return jsonify({"status": "success", "banks": banks}), 200


# transfer_db.py (Dán thêm vào cuối file)

def get_bill_provider_id_from_name(provider_name):
    """Lấy bill_provider_id từ tên nhà cung cấp (ví dụ: 'EVN Hà Nội')"""
    conn = db.get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            query = "SELECT bill_provider_id FROM bill_provider_supported WHERE bill_provider_name = %s"
            cur.execute(query, (provider_name,))
            row = cur.fetchone()
            return row[0] if row else None
    except Exception as e:
        print(f"Error fetching bill provider ID for name {provider_name}: {e}")
        return None
    finally:
        conn.close()


def get_supported_bill_provider(bill_type_name):
    """Lấy danh sách tên nhà cung cấp theo loại hóa đơn (Ví dụ: 'Điện', 'Nước')"""
    conn = db.get_db_connection()
    result = []
    if not conn:
        return result
    try:
        with conn.cursor() as cur:
            # Bước 1: Tìm bill_id từ tên loại hóa đơn
            type_query = "SELECT bill_id FROM bill_type_supported WHERE bill_type_name = %s"
            cur.execute(type_query, (bill_type_name,))
            row = cur.fetchone()
            
            # Bước 2: Nếu tìm thấy bill_id, đi lấy danh sách nhà cung cấp
            if row:
                bill_id = row[0]
                provider_query = "SELECT bill_provider_name FROM bill_provider_supported WHERE bill_id = %s"
                cur.execute(provider_query, (bill_id,))
                rows = cur.fetchall()
                result = [r[0] for r in rows] # Chuyển mảng tuple thành mảng string đơn giản
    except Exception as e:
        print(f"Error fetching bill providers for type {bill_type_name}: {e}")
    finally:
        conn.close()
    return result