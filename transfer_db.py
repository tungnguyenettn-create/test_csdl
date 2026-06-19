# transfer_db.py
import db

def get_result_message(code):
    """Hàm helper dịch mã kết quả từ Database thành thông báo tiếng Việt"""
    messages = {
        1: "Giao dịch hoàn tất thành công!",
        0: "Thất bại: Tài khoản nguồn và đích không được trùng nhau.",
        -1: "Thất bại: Số tiền giao dịch phải lớn hơn 0.",
        2: "Thất bại: Tài khoản nguồn không tồn tại hoặc đã bị đóng.",
        3: "Thất bại: Tài khoản đích không tồn tại hoặc đã bị đóng.",
        4: "Thất bại: Tài khoản không đủ số dư.",
        5: "Thất bại: Ngân hàng đích liên kết không được hỗ trợ.",
        6: "Thất bại: Nhà cung cấp dịch vụ hóa đơn không tồn tại.",
        7: "Thất bại: Nhân viên thực hiện không tồn tại hoặc đã dừng hoạt động.",
        -99: "Thất bại: Lỗi kết nối hệ thống dữ liệu đột xuất."
    }
    return messages.get(code, f"Thất bại: Mã lỗi không xác định ({code}).")

def get_supported_bank():
    conn = db.get_db_connection()
    supported_banks = ["36 BANK"]
    if not conn:
        return supported_banks
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT out_bank_branch FROM out_bank_supported;")
            rows = cur.fetchall()
            for r in rows:
                supported_banks.append(r[0])
    except Exception as e:
        print(f"Error fetching supported banks: {e}")
    finally:
        conn.close()
    return supported_banks

def in_bank_transfer(source_account, dest_account, amount, description):
    """1. Chuyển khoản nội bộ"""
    conn = db.get_db_connection()
    if not conn:
        return -99
    try:
        with conn.cursor() as cur:
            query = "SELECT fn_in_bank_transfer(%s, %s, %s, %s);"
            cur.execute(query, (source_account, dest_account, amount, description))
            result = cur.fetchone()[0]
            conn.commit()  # Xác nhận trừ tiền/cộng tiền trong DB
            return result
    except Exception as e:
        print(f"Error executing in_bank_transfer: {e}")
        conn.rollback()
        return -99
    finally:
        conn.close()

def out_bank_transfer(source_account, dest_bank_id, amount, description):
    """2. Chuyển khoản liên ngân hàng"""
    conn = db.get_db_connection()
    if not conn:
        return -99
    try:
        with conn.cursor() as cur:
            query = "SELECT fn_out_bank_transaction(%s, %s, %s, %s);"
            cur.execute(query, (source_account, dest_bank_id, amount, description))
            result = cur.fetchone()[0]
            conn.commit()
            return result
    except Exception as e:
        print(f"Error executing out_bank_transfer: {e}")
        conn.rollback()
        return -99
    finally:
        conn.close()

def pay_bill(source_account, bill_provider_id, amount):
    """3. Thanh toán hóa đơn"""
    conn = db.get_db_connection()
    if not conn:
        return -99
    try:
        with conn.cursor() as cur:
            query = "SELECT fn_pay_bill(%s, %s, %s);"
            cur.execute(query, (source_account, bill_provider_id, amount))
            result = cur.fetchone()[0]
            conn.commit()
            return result
    except Exception as e:
        print(f"Error executing pay_bill: {e}")
        conn.rollback()
        return -99
    finally:
        conn.close()

def get_bank_id_from_bank_name(bank_name):
    conn = db.get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            query = "SELECT out_bank_id FROM out_bank_supported WHERE out_bank_branch = %s"
            cur.execute(query, (bank_name,))
            row = cur.fetchone()
            return row[0] if row else None
    except Exception as e:
        print(f"Error fetching bank ID: {e}")
        return None
    finally:
        conn.close()


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