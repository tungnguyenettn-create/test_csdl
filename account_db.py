# account_db.py
import db

def login_db(account, password):
    """Dịch từ login() của Java: Trả về 2 (thành công), 1 (sai pass), 0 (không có acc), -1 (lỗi)"""
    conn = db.get_db_connection()
    if not conn:
        return -1
    try:
        with conn.cursor() as cur:
            query = "SELECT account_password FROM account WHERE account_id = %s AND account_status = 'open'"
            cur.execute(query, (account,))
            row = cur.fetchone()
            
            if not row:
                return 0 # Tài khoản không tồn tại
                
            corrected_password = row[0]
            if corrected_password != password:
                return 1 # Sai mật khẩu
                
            return 2 # Thành công
    except Exception as e:
        print(f"Login system error: {e}")
        return -1
    finally:
        conn.close()

def get_balance(account):
    """Dịch từ getBalance() của Java"""
    conn = db.get_db_connection()
    if not conn:
        return 0.0
    try:
        with conn.cursor() as cur:
            query = "SELECT balance FROM account WHERE account_id = %s AND account_status='open'"
            cur.execute(query, (account,))
            row = cur.fetchone()
            # row[0] trả về kiểu Decimal, ta ép về float để Flask dễ xử lý JSON
            return float(row[0]) if row else 0.0
    except Exception as e:
        print(f"Database error while fetching balance: {e}")
        return 0.0
    finally:
        conn.close()

def get_account_from_user(identity_card):
    """Dịch từ getAccountFromUser() của Java"""
    conn = db.get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            # Query 1: Lấy customer_id
            query1 = "SELECT customer_id FROM customer WHERE identity_card = %s"
            cur.execute(query1, (identity_card,))
            row1 = cur.fetchone()
            if not row1:
                return []
            
            customer_id = row1[0]
            
            # Query 2: Lấy danh sách account_id
            query2 = "SELECT account_id FROM account WHERE customer_id = %s AND account_status = 'open'"
            cur.execute(query2, (customer_id,))
            rows = cur.fetchall()
            
            return [r[0] for r in rows] # Chuyển tuple thành list các string
    except Exception as e:
        print(f"Database error occurred: {e}")
        return []
    finally:
        conn.close()

def get_user_from_account(account_id):
    """Dịch từ getUserFromAccount() của Java. Trả về dict (Map trong Java)"""
    conn = db.get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            query1 = "SELECT customer_id FROM account WHERE account_status = 'open' AND account_id = %s"
            cur.execute(query1, (account_id,))
            row1 = cur.fetchone()
            if not row1:
                return None
                
            customer_id = row1[0]
            
            query2 = """
                SELECT customer_id, branch_id, full_name, identity_card, nationality, dob, city, address, phone 
                FROM customer WHERE customer_id = %s
            """
            cur.execute(query2, (customer_id,))
            
            # Lấy tên các cột để map thành dictionary tự động
            columns = [desc[0] for desc in cur.description]
            row2 = cur.fetchone()
            
            if row2:
                customer_data = dict(zip(columns, row2))
                # Định dạng lại ngày sinh (date) thành chuỗi YYYY-MM-DD để không bị lỗi JSON
                if customer_data.get('dob'):
                    customer_data['dob'] = customer_data['dob'].isoformat()
                return customer_data
    except Exception as e:
        print(f"Database error while fetching user: {e}")
    finally:
        conn.close()
    return None

def get_metadata(account):
    """Dịch từ getMetadata() của Java"""
    conn = db.get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            query = "SELECT balance, open_date FROM account WHERE account_id = %s AND account_status='open'"
            cur.execute(query, (account,))
            
            columns = [desc[0] for desc in cur.description]
            row = cur.fetchone()
            if row:
                metadata = dict(zip(columns, row))
                if metadata.get('balance'):
                    metadata['balance'] = float(metadata['balance'])
                if metadata.get('open_date'):
                    metadata['open_date'] = metadata['open_date'].isoformat()
                return metadata
    except Exception as e:
        print(f"Database error while fetching metadata: {e}")
    finally:
        conn.close()
    return None
def update_password(account, new_password):
    """Dịch từ updatePassword() của Java. Lưu ý phải có conn.commit() khi UPDATE/INSERT"""
    conn = db.get_db_connection()
    if not conn:
        return -1
    try:
        with conn.cursor() as cur:
            query = "UPDATE account SET account_password = %s WHERE account_id = %s AND account_status = 'open'"
            cur.execute(query, (new_password, account))
            
            conn.commit() # Xác nhận thay đổi dữ liệu vào Postgres
            
            # Kiểm tra xem có dòng nào được cập nhật không
            if cur.rowcount > 0:
                # ĐÃ XÓA dòng cur.fetchall() gây lỗi ở đây
                return 1 # Thành công
            else:
                return 0 # Không tìm thấy account thích hợp hoặc tài khoản đã bị đóng
    except Exception as e:
        print(f"Database error while updating password: {e}")
        conn.rollback() # Hoàn tác nếu lỗi
        return -1
    finally:
        conn.close()
