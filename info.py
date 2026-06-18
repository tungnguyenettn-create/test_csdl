from flask import Blueprint, jsonify

info_bp = Blueprint('info', __name__)

@info_bp.route('/api/info/branches', methods=['GET'])
def get_branches():
    # Data rác về các chi nhánh
    mock_branches = [
        {"id": 1, "name": "Chi nhánh Bách Khoa - Hà Nội", "address": "Số 1 Đại Cồ Việt"},
        {"id": 2, "name": "Chi nhánh Cầu Giấy", "address": "234 Đường Xuân Thủy"}
    ]
    return jsonify({"status": "success", "branches": mock_branches})

@info_bp.route('/api/info/news', methods=['GET'])
def get_news():
    mock_news = [
        {"title": "Lãi suất gửi tiết kiệm tháng 6 cực khủng lên tới 10%", "date": "18/06/2026"},
        {"title": "Bảo trì hệ thống từ 2h - 4h sáng chủ nhật", "date": "17/06/2026"}
    ]
    return jsonify({"status": "success", "news": mock_news})