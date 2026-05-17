"""
Test data cho chức năng Đăng nhập – Admin.
"""

# ── tài khoản admin có sẵn ───────────────────────────────────────────────────
VALID_ADMIN = {
    "email":    "admin123@gmail.com",
    "password": "admin123",
}

# ── thông báo lỗi mong đợi trên UI ──────────────────────────────────────────
ERROR_MESSAGES = {
    "invalid_credentials": "Email hoặc mật khẩu không chính xác",
    "account_locked":      "Tài khoản của bạn đã bị khóa tạm thời",
}

# ── negative cases ────────────────────────────────────────────────────────────
LOGIN_FAILURE_CASES = [
    {
        "id":       "wrong_password",
        "email":    "admin123@gmail.com",
        "password": "wrongpass",
        "desc":     "Đúng email, sai mật khẩu → báo lỗi xác thực",
    },
    {
        "id":       "wrong_email",
        "email":    "notadmin@gmail.com",
        "password": "admin123",
        "desc":     "Email không tồn tại → báo lỗi xác thực",
    },
    {
        "id":       "user_account_on_admin_form",
        "email":    "user_test@hus.edu.vn",
        "password": "Test@12345",
        "desc":     "Dùng tài khoản user thường đăng nhập vào trang admin → bị từ chối",
    },
    {
        "id":       "empty_email",
        "email":    "",
        "password": "admin123",
        "desc":     "Email rỗng → HTML5 required chặn submit",
    },
    {
        "id":       "empty_password",
        "email":    "admin123@gmail.com",
        "password": "",
        "desc":     "Mật khẩu rỗng → HTML5 required chặn submit",
    },
    {
        "id":       "invalid_email_format",
        "email":    "not-an-email",
        "password": "admin123",
        "desc":     "Sai định dạng email → HTML5 type=email chặn submit",
    },
]