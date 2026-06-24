# history_db.py
import db
def get_all_history(account_id):
    """Gọi hàm fn_get_account_history để lấy toàn bộ lịch sử giao dịch chi tiết"""
    conn = db.get_db_connection()
    result = []
    if not conn:
        return result
    try:
        with conn.cursor() as cur:
            # Câu truy vấn lấy đầy đủ 7 cột tương ứng với kết quả trả về của hàm SQL
            query = """
                SELECT 
                    transaction_id, 
                    transaction_time, 
                    transaction_type, 
                    amount_change, 
                    description, 
                    status, 
                    related_party 
                FROM fn_get_account_history(%s);
            """
            cur.execute(query, (account_id,))
            rows = cur.fetchall()
            for r in rows:
                result.append({
                    "transaction_id": int(r[0]),
                    # Chuyển đổi timestamp thành chuỗi định dạng YYYY-MM-DD HH:MM:SS để dễ hiển thị ở giao diện
                    "transaction_time": r[1].strftime("%Y-%m-%d %H:%M:%S") if r[1] else None,
                    "transaction_type": r[2],
                    "amount_change": float(r[3]) if r[3] is not None else 0.0,
                    "description": r[4],
                    "status": r[5],
                    "related_party": r[6]  # Đối tác/Bên liên quan (mới thêm)
                })
    except Exception as e:
        print(f"Error in get_all_history: {e}")
    finally:
        conn.close()
    return result

def get_daily_history(account_id):
    """Gọi hàm fn_get_account_history_daily (7 ngày gần nhất)"""
    conn = db.get_db_connection()
    result = []
    if not conn:
        return result
    try:
        with conn.cursor() as cur:
            query = "SELECT period_label, total_inflow, total_outflow, net_change, transaction_count FROM fn_get_account_history_daily(%s);"
            cur.execute(query, (account_id,))
            rows = cur.fetchall()
            for r in rows:
                result.append({
                    "period_label": r[0],
                    "total_inflow": float(r[1]),
                    "total_outflow": float(r[2]),
                    "net_change": float(r[3]),
                    "transaction_count": int(r[4])
                })
    except Exception as e:
        print(f"Error in get_daily_history: {e}")
    finally:
        conn.close()
    return result

def get_monthly_history(account_id):
    """Gọi hàm fn_get_account_history_monthly (1 năm qua theo tháng)"""
    conn = db.get_db_connection()
    result = []
    if not conn:
        return result
    try:
        with conn.cursor() as cur:
            query = "SELECT period_label, total_inflow, total_outflow, net_change, transaction_count FROM fn_get_account_history_monthly(%s);"
            cur.execute(query, (account_id,))
            rows = cur.fetchall()
            for r in rows:
                result.append({
                    "period_label": r[0],
                    "total_inflow": float(r[1]),
                    "total_outflow": float(r[2]),
                    "net_change": float(r[3]),
                    "transaction_count": int(r[4])
                })
    except Exception as e:
        print(f"Error in get_monthly_history: {e}")
    finally:
        conn.close()
    return result
