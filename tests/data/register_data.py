"""
Dữ liệu tĩnh cho kiểm thử chức năng đăng ký.
Các trường: full_name, email, password, confirm_password
"""

# ── Tài khoản đã tồn tại (seed sẵn trong DB test) ────────────────────────────
EXISTING_USER = {
    "full_name": "Nguyen Van A",
    "email": "existing@example.com",
    "password": "Test@1234",
    "confirm_password": "Test@1234",
    "expected_error": "Email này đã được đăng ký",
}

# ── Các trường hợp mật khẩu không hợp lệ ─────────────────────────────────────
INVALID_PASSWORDS = [
    {
        "id": "too_short",
        "description": "Mật khẩu quá ngắn (< 8 ký tự)",
        "password": "Ab1@",
        "confirm_password": "Ab1@",
        "expected_error": "Mật khẩu tối thiểu 8 ký tự",
    },
    {
        "id": "no_uppercase",
        "description": "Mật khẩu không có chữ hoa",
        "password": "test@1234",
        "confirm_password": "test@1234",
        "expected_error": "Mật khẩu phải có ít nhất 1 chữ hoa",
    },
    {
        "id": "no_special_char",
        "description": "Mật khẩu không có ký tự đặc biệt",
        "password": "Test1234",
        "confirm_password": "Test1234",
        "expected_error": "Mật khẩu phải có ít nhất 1 ký tự đặc biệt",
    },
    {
        "id": "no_number",
        "description": "Mật khẩu không có chữ số",
        "password": "Test@abcd",
        "confirm_password": "Test@abcd",
        "expected_error": "Mật khẩu phải có ít nhất 1 chữ số",
    },
]

# ── Các trường hợp email không hợp lệ ────────────────────────────────────────
INVALID_EMAILS = [
    {
        "id": "missing_at",
        "description": "Email thiếu ký tự @",
        "email": "invalidemail.com",
        "expected_error": "Email không đúng định dạng",
    },
    {
        "id": "missing_domain",
        "description": "Email thiếu phần domain",
        "email": "user@",
        "expected_error": "Email không đúng định dạng",
    },
    {
        "id": "has_space",
        "description": "Email chứa khoảng trắng",
        "email": "user name@example.com",
        "expected_error": "Email không đúng định dạng",
    },
]

# ── Confirm password không khớp ───────────────────────────────────────────────
PASSWORD_MISMATCH = {
    "password": "Test@1234",
    "confirm_password": "Test@5678",
    "expected_error": "Mật khẩu xác nhận không khớp",
}

# ── Trường bắt buộc bị bỏ trống ──────────────────────────────────────────────
REQUIRED_FIELDS = [
    {"field": "full_name", "expected_error": "Vui lòng nhập họ tên"},
    {"field": "email",     "expected_error": "Vui lòng nhập email"},
    {"field": "password",  "expected_error": "Mật khẩu tối thiểu 8 ký tự"},
]