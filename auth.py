# auth.py
from functools import wraps
from flask import request, jsonify
import jwt

import redis
import os

# Nếu chạy trong Docker, host sẽ là 'redis_cache'. Nếu chạy ở ngoài, sẽ fallback về 'localhost'
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis_cache')

redis_client = redis.Redis(
    host=REDIS_HOST, 
    port=6379, 
    db=0, 
    decode_responses=True
)


# Chìa khóa bí mật của bạn (giữ nguyên cái cũ của bạn nhé)
JWT_SECRET = "ubuntu8s9reat_secret_key" 
# auth.py (Đoạn cập nhật hàm token_required)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"status": "error", "message": "Sai định dạng Token!"}), 401
                
        if not token:
            token = request.args.get('token')

        if not token:
            return jsonify({"status": "error", "message": "Không tìm thấy Token! Vui lòng đăng nhập trước."}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user_account = data['customer_id']
            
            # ✅ Check if this token is still the active one in Redis
            active_token = redis_client.get(f"active_token:{current_user_account}")
            
            if active_token is None:
                return jsonify({
                    "status": "error",
                    "message": "Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại!"
                }), 401
                
            if active_token != token:
                return jsonify({
                    "status": "error",
                    "message": "Token không hợp lệ!"
                }), 401
                
        except jwt.ExpiredSignatureError:
            # ✅ Clean up Redis when JWT naturally expires
            try:
                data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"],
                                  options={"verify_exp": False})
                redis_client.delete(f"active_token:{data['customer_id']}")
            except Exception:
                pass
            return jsonify({"status": "error", "message": "Token đã hết hạn!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "error", "message": "Token không hợp lệ!"}), 401
            
        return f(current_user_account, *args, **kwargs)
        
    return decorated
