# history_db.py
import db

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