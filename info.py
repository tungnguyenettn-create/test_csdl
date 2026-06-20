from flask import Blueprint, jsonify
import db 
info_bp = Blueprint('info', __name__)

def get_supported_branch(): 
    conn = db.get_db_connection() 
    supported_branchs = [] 
    if not conn: 
        return supported_branchs 
    try: 
        with conn.cursor() as cur: 
            cur.execute("SELECT * FROM branch") 
            rows = cur.fetchall() 
            for r in rows: 
                supported_branchs.append(
                    {
                        "index": r[0],
                        "address": r[1], 
                        "branch name": r[2] 
                    }
                )
    except Exception as e: 
        print(f"Error fetching supported banks: {e}") 
    finally: 
        conn.close()
    return supported_branchs 


@info_bp.route('/api/info/branches', methods=['GET'])
def get_branches():
    # Gọi hàm lấy dữ liệu từ database
    db_branches = get_supported_branch()
    
    # Nếu không lấy được dữ liệu hoặc có lỗi (mảng rỗng)
    if not db_branches:
        return jsonify({
            "status": "error", 
            "message": "Không thể lấy danh sách chi nhánh hoặc không có dữ liệu"
        }), 500

    # Map lại key để chuẩn hóa dữ liệu trả về cho client (Optional)
    # Nếu bạn muốn giữ nguyên key từ hàm get_supported_branch thì bỏ qua bước map này nhé.
    formatted_branches = [
        {
            "id": branch["index"],
            "name": branch["branch name"],
            "address": branch["address"]
        }
        for branch in db_branches
    ]
    
    return jsonify({
        "status": "success", 
        "branches": formatted_branches  # Hoặc dùng trực tiếp db_branches nếu không cần đổi key
    })


@info_bp.route('/api/info/news', methods=['GET'])
def get_news():
    mock_news = [
        {"title": "Lãi suất gửi tiết kiệm tháng 6 cực khủng lên tới 10%", "date": "18/06/2026"},
        {"title": "Bảo trì hệ thống từ 2h - 4h sáng chủ nhật", "date": "17/06/2026"}
    ]
    return jsonify({"status": "success", "news": mock_news})