from flask import request
import jwt

# Chìa khóa bí mật để ký Token (Chỉ nằm trên Server)
JWT_SECRET = "SieuBaoMatBachKhoa@2026"

def verify_customer_token():
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        return None
    try:
        actual_token = token.split(" ")[1]
        # Giải mã token bằng chìa khóa bí mật
        payload = jwt.decode(actual_token, JWT_SECRET, algorithms=["HS256"])
        return payload  # Trả về thông tin user nếu hợp lệ
    except:
        return None  # Trả về None nếu token fake hoặc hết hạn