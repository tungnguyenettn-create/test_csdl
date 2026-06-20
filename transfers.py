from flask import Blueprint, request, jsonify
from auth import token_required  # Tái sử dụng tấm khiên bảo mật từ file auth.py của bạn
import transfer_db
from decimal import Decimal

transfers_bp = Blueprint('transfers', __name__)

# 1. API CHUYỂN TIỀN NỘI BỘ (Đã hoàn thiện)
@transfers_bp.route('/api/transfers/in_bank_transfer', methods=['POST'])
@token_required
def in_bank_transfer(current_user): # current_user chính là tài khoản nguồn lấy tự động từ Token
    data = request.get_json()
    dest_acc = data.get("dest_account")
    amount = data.get("amount")
    description = data.get("description", f"Chuyen khoan tu {current_user}")
    
    # Kiểm tra dữ liệu đầu vào cơ bản trước khi gọi DB
    if not dest_acc or not amount:
        return jsonify({"status": "error", "message": "Vui lòng nhập tài khoản đích và số tiền!"}), 400
        
    try:
        amount_numeric = Decimal(amount)
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


# 2. API CHUYỂN TIỀN LIÊN NGÂN HÀNG (Sửa lỗi & Hoàn thiện)
@transfers_bp.route('/api/transfers/out_bank_transfer', methods=['POST']) # Thêm dấu / ở đầu route
@token_required 
def out_bank_transfer(current_user): 
    data = request.get_json() 
    desc_bank = data.get("desc_bank") 
    desc_acc = data.get("desc_acc") 
    amount = data.get("amount") 
    description = data.get("description", f"Chuyen khoan lien ngan hang tu {current_user}") 

    if not desc_acc or not amount or not desc_bank: 
        return jsonify({"status": "error", "message": "Vui lòng nhập tài khoản đích, ngân hàng và số tiền!"}), 400
    
    try: 
        amount_numeric = Decimal(amount) 
    except ValueError: 
        return jsonify({"status": "error", "message": "Số tiền không hợp lệ!"}), 400

    # Lấy ID ngân hàng từ tên ngân hàng người dùng truyền lên
    bank_id = transfer_db.get_bank_id_from_bank_name(desc_bank) 
    if bank_id is None:
        return jsonify({"status": "error", "message": "Ngân hàng đích không được hỗ trợ!"}), 400

    # Gọi hàm xử lý từ transfer_db (đã sửa lỗi gọi sai transfer.db) và truyền amount_numeric
    result_code = transfer_db.out_bank_transfer(current_user, bank_id, amount_numeric, description) 
    message = transfer_db.get_result_message(result_code)

    if result_code == 1:
        return jsonify({
            "status": "success",
            "result_code": result_code,
            "message": message,
            "detail": f"Tài khoản {current_user} đã chuyển thành công {amount_numeric} VNĐ đến STK {desc_acc} tại ngân hàng {desc_bank}."
        }), 200
    else:
        return jsonify({
            "status": "error",
            "result_code": result_code,
            "message": message
        }), 400


# 3. API LẤY DANH SÁCH NGÂN HÀNG HỖ TRỢ (Đã hoàn thiện)
@transfers_bp.route('/api/transfers/supported-banks', methods=['GET'])
@token_required
def get_banks(current_user):
    banks = transfer_db.get_supported_bank()
    return jsonify({"status": "success", "banks": banks}), 200


# 4. API THANH TOÁN HÓA ĐƠN (Viết mới hoàn thiện)
@transfers_bp.route('/api/transfers/pay-bill', methods=['POST'])
@token_required
def pay_bill(current_user):
    data = request.get_json()
    provider_name = data.get("provider_name") # Ví dụ: 'EVN Hà Nội'
    amount = data.get("amount")

    if not provider_name or not amount:
        return jsonify({"status": "error", "message": "Vui lòng cung cấp tên nhà cung cấp và số tiền thanh toán!"}), 400

    try:
        amount_numeric = Decimal(amount)
    except ValueError:
        return jsonify({"status": "error", "message": "Số tiền không hợp lệ!"}), 400

    # Tìm ID của nhà cung cấp từ tên nhà cung cấp dịch vụ
    bill_provider_id = transfer_db.get_bill_provider_id_from_name(provider_name)
    if bill_provider_id is None:
        return jsonify({"status": "error", "message": "Nhà cung cấp dịch vụ không tồn tại hoặc không được hỗ trợ!"}), 400

    # Tiến hành gọi hàm thanh toán hóa đơn trong DB
    result_code = transfer_db.pay_bill(current_user, bill_provider_id, amount_numeric)
    message = transfer_db.get_result_message(result_code)

    if result_code == 1:
        return jsonify({
            "status": "success",
            "result_code": result_code,
            "message": message,
            "detail": f"Tài khoản {current_user} đã thanh toán hóa đơn thành công số tiền {amount_numeric} VNĐ cho {provider_name}."
        }), 200
    else:
        return jsonify({
            "status": "error",
            "result_code": result_code,
            "message": message
        }), 400


# 5. API BỔ SUNG: LẤY DANH SÁCH NHÀ CUNG CẤP THEO LOẠI HÓA ĐƠN (GET)
@transfers_bp.route('/api/transfers/supported-bill-providers', methods=['GET'])
@token_required
def get_bill_providers(current_user):
    # Lấy thông tin loại hóa đơn từ Query Parameter (Ví dụ: /api/transfers/supported-bill-providers?bill_type=Điện)
    bill_type_name = request.args.get("bill_type")
    if not bill_type_name:
        return jsonify({"status": "error", "message": "Vui lòng truyền tham số loại hóa đơn (bill_type)!"}), 400

    providers = transfer_db.get_supported_bill_provider(bill_type_name)
    return jsonify({"status": "success", "bill_type": bill_type_name, "providers": providers}), 200