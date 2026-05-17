"""
Test data cho chức năng đăng nhập User.
Bao gồm: happy path, negative path, boundary value.
"""

# ── tài khoản hợp lệ (lấy từ fixture users.json) ───────────────────────────
VALID_USER = {
    "email":    "user_test@hus.edu.vn",
    "password": "Test@12345",
}

# ── parametrize: đăng nhập thành công ───────────────────────────────────────
LOGIN_SUCCESS_CASES = [
    pytest_param := {
        "id":       "valid_user",
        "email":    "user_test@hus.edu.vn",
        "password": "Test@12345",
        "desc":     "Email và mật khẩu hợp lệ → đăng nhập thành công",
    },
]

# ── parametrize: đăng nhập thất bại ─────────────────────────────────────────
LOGIN_FAILURE_CASES = [
    {
        "id":       "wrong_password",
        "email":    "user_test@hus.edu.vn",
        "password": "WrongPass!99",
        "desc":     "Đúng email, sai mật khẩu → báo lỗi xác thực",
    },
    {
        "id":       "wrong_email",
        "email":    "notexist@hus.edu.vn",
        "password": "Test@12345",
        "desc":     "Email không tồn tại → báo lỗi xác thực",
    },
    {
        "id":       "empty_email",
        "email":    "",
        "password": "Test@12345",
        "desc":     "Email rỗng → nút submit bị disabled, không thể gửi form",
    },
    {
        "id":       "empty_password",
        "email":    "user_test@hus.edu.vn",
        "password": "",
        "desc":     "Mật khẩu rỗng → nút submit bị disabled, không thể gửi form",
    },
    {
        "id":       "both_empty",
        "email":    "",
        "password": "",
        "desc":     "Cả hai trường rỗng → nút submit bị disabled",
    },
    {
        "id":       "invalid_email_format",
        "email":    "not-an-email",
        "password": "Test@12345",
        "desc":     "Sai định dạng email → browser validation chặn submit",
    },
    {
        "id":       "locked_account",
        "email":    "locked@hus.edu.vn",
        "password": "Test@12345",
        "desc":     "Tài khoản bị khóa → hiển thị thông báo tài khoản bị khóa",
    },
    {
        "id":       "unverified_account",
        "email":    "unverified@hus.edu.vn",
        "password": "Test@12345",
        "desc":     "Chưa xác thực email → hiển thị thông báo yêu cầu xác thực",
    },
]

# ── boundary: mật khẩu cực ngắn / cực dài ───────────────────────────────────
LOGIN_BOUNDARY_CASES = [
    {
        "id":       "password_1_char",
        "email":    "user_test@hus.edu.vn",
        "password": "A",
        "desc":     "Mật khẩu 1 ký tự → xác thực thất bại",
    },
    {
        "id":       "password_255_chars",
        "email":    "user_test@hus.edu.vn",
        "password": "A" * 255,
        "desc":     "Mật khẩu 255 ký tự → xác thực thất bại (không khớp)",
    },
]

# ── thông báo lỗi mong đợi trên UI ──────────────────────────────────────────
ERROR_MESSAGES = {
    "invalid_credentials": "Email hoặc mật khẩu không chính xác",
    "account_locked":      "Tài khoản của bạn đã bị khóa tạm thời",
    "unverified_email":    "Vui lòng xác thực email trước khi đăng nhập",
}