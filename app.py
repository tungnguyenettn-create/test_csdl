from flask import Flask, jsonify
from customer import customer_bp
from transfers import transfers_bp
from history import history_bp
#from info import info_bp

app = Flask(__name__)

# Đăng ký các Blueprint (Gộp các module route vào app chính)
app.register_blueprint(customer_bp)
app.register_blueprint(transfers_bp)
app.register_blueprint(history_bp)
#app.register_blueprint(info_bp)

@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Hệ thống API Ngân hàng chạy mô hình Blueprint thành công, không còn lỗi import!"
    })

if __name__ == '__main__':
    # Chạy ở cổng 5000, bật debug=True để tự động reload khi sửa code
    app.run(host='0.0.0.0', port=5000, debug=True)