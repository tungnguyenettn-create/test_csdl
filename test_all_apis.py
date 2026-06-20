import requests
import json

# Thay đổi URL này nếu bạn chạy Flask ở cổng (port) khác
BASE_URL = "http://127.0.0.1:5000" 

# Biến toàn cục để lưu Token sau khi đăng nhập thành công
TOKEN = ""
HEADERS = {}

def print_result(api_name, response):
    """Hàm helper để in kết quả test cho đẹp và dễ nhìn"""
    print(f"=== TEST: {api_name} ===")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(f"Response Text: {response.text}")
    print("-" * 50 + "\n")

def test_public_apis():
    """1. Test các API công cộng (Không cần đăng nhập)"""
    print("🚀 BẮT ĐẦU TEST CÁC API KHÔNG CẦN TOKEN...\n")
    
    # Chi nhánh
    res_branches = requests.get(f"{BASE_URL}/api/info/branches")
    print_result("Lấy danh sách chi nhánh", res_branches)
    
    # Tin tức
    res_news = requests.get(f"{BASE_URL}/api/info/news")
    print_result("Lấy tin tức", res_news)
    
    # Quên tài khoản (API GET nhưng truyền body theo code của bạn)
    forget_data = {"identiy-card": "CUST-ID-1"}
    res_forget = requests.get(f"{BASE_URL}/api/customer/forget-account", json=forget_data)
    print_result("Quên tài khoản (Tìm bằng CCCD)", res_forget)


def test_login():
    """2. Test API Đăng nhập và lấy Token"""
    global TOKEN, HEADERS
    print("🔑 TIẾN HÀNH ĐĂNG NHẬP...")
    
    login_data = {
        "username": "ACC-00024",
        "password": "pin_hash"
    }
    res = requests.post(f"{BASE_URL}/api/customer/login", json=login_data)
    print_result("Đăng nhập hệ thống", res)
    
    if res.status_code == 200:
        TOKEN = res.json().get("token")
        # Cấu hình Header chứa Token cho các API phía sau
        HEADERS = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
        print(f"✅ Lấy Token thành công! Tiếp tục test các API bảo mật...\n" + "="*50 + "\n")
        return True
    else:
        print("❌ Đăng nhập thất bại. Dừng các bài test cần Token!")
        return False


def test_customer_apis():
    """3. Test nhóm API thông tin tài khoản (Cần Token)"""
    print("👤 TEST CÁC API THÔNG TIN KHÁCH HÀNG...\n")
    
    # Xem số dư
    res_balance = requests.get(f"{BASE_URL}/api/customer/balance", headers=HEADERS)
    print_result("Xem số dư tài khoản", res_balance)
    
    # Xem thông tin cá nhân
    res_info = requests.get(f"{BASE_URL}/api/customer/my-info", headers=HEADERS)
    print_result("Xem thông tin cá nhân", res_info)
    
    # Đổi mật khẩu (Hãy cẩn thận vì đổi xong lần sau phải dùng mật khẩu mới để login)
    # Ở đây tôi ví dụ đổi sang 'new_pin_hash'
    change_pwd_data = {"new_password": "abcdefghijk"}
    res_pwd = requests.put(f"{BASE_URL}/api/customer/change-password", headers=HEADERS, json=change_pwd_data)
    print_result("Đổi mật khẩu tài khoản", res_pwd)
    
    # Đổi ngược lại về 'pin_hash' để tránh ảnh hưởng lần test sau
    #requests.put(f"{BASE_URL}/api/customer/change-password", headers=HEADERS, json={"new_password": "pin_hash"})


def test_transfer_apis():
    """4. Test nhóm API giao dịch / chuyển tiền (Cần Token)"""
    print("💸 TEST CÁC API GIAO DỊCH CHUYỂN TIỀN...\n")
    
    # Chuyển khoản nội bộ (đến ACC-00015)
    in_bank_data = {
        "dest_account": "ACC-00015",
        "amount": "500",
        "description": "Script test: Chuyen tien noi bo"
    }
    res_in = requests.post(f"{BASE_URL}/api/transfers/in_bank_transfer", headers=HEADERS, json=in_bank_data)
    print_result("Chuyển tiền nội bộ", res_in)
    
    # Lấy danh sách ngân hàng hỗ trợ
    res_supported_banks = requests.get(f"{BASE_URL}/api/transfers/supported-banks", headers=HEADERS)
    print_result("Lấy danh sách ngân hàng liên kết", res_supported_banks)
    
    # Chuyển tiền liên ngân hàng
    out_bank_data = {
        "desc_bank": "External Bank Branch 1",  # Tên ngân hàng có sẵn trong dữ liệu mặc định get_supported_bank của bạn
        "desc_acc": "9999999999",
        "amount": "2000",
        "description": "Script test: Chuyen tien lien ngan hang"
    }
    res_out = requests.post(f"{BASE_URL}/api/transfers/out_bank_transfer", headers=HEADERS, json=out_bank_data)
    print_result("Chuyển tiền liên ngân hàng", res_out)
    
    # Lấy nhà cung cấp hóa đơn (Ví dụ loại hóa đơn: Điện)
    res_providers = requests.get(f"{BASE_URL}/api/transfers/supported-bill-providers", headers=HEADERS, params={"bill_type": "Điện"})
    print_result("Lấy nhà cung cấp hóa đơn theo loại", res_providers)
    
    # Thanh toán hóa đơn
    pay_bill_data = {
        "provider_name": "EVN Power Co 1", # Nhớ thêm nhà cung cấp này vào DB của bạn trước nhé
        "amount": "1500"
    }
    res_bill = requests.post(f"{BASE_URL}/api/transfers/pay-bill", headers=HEADERS, json=pay_bill_data)
    print_result("Thanh toán hóa đơn", res_bill)


def test_history_apis():
    """5. Test nhóm API xem lịch sử biến động số dư (Cần Token)"""
    print("📜 TEST CÁC API LỊCH SỬ BIẾN ĐỘNG SỐ DƯ...\n")
    
    # Xem lịch sử theo ngày
    res_daily = requests.get(f"{BASE_URL}/api/customer/history", headers=HEADERS, params={"type": "daily"})
    print_result("Lịch sử biến động số dư theo ngày (7 ngày qua)", res_daily)
    
    # Xem lịch sử theo tháng
    res_monthly = requests.get(f"{BASE_URL}/api/customer/history", headers=HEADERS, params={"type": "monthly"})
    print_result("Lịch sử biến động số dư theo tháng (1 năm qua)", res_monthly)


if __name__ == "__main__":
    print("============== CHƯƠNG TRÌNH TEST API TỰ ĐỘNG ==============\n")
    
    # Bước 1: Chạy các API công cộng
    test_public_apis()
    
    # Bước 2: Đăng nhập để lấy Token chuẩn bị cho các bước sau
    is_logged_in = test_login()
    
    # Bước 3: Nếu đăng nhập thành công thì quét các API dùng Token
    if is_logged_in:
        test_customer_apis()
        test_transfer_apis()
        test_history_apis()
        
    print("================== HOÀN THÀNH BÀI TEST ==================")