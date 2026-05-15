EMPTY_FIELDS = {
    "email": "",
    "password": "",
    "expected_error": None
}

EMPTY_EMAIL = {
    "email": "",
    "password": "StrongPass123!",
    "expected_error": None
}

EMPTY_PASSWORD = {
    "email": "test@example.com",
    "password": "",
    "expected_error": None
}

INVALID_EMAIL = {
    "email": "wronguser@example.com",
    "password": "StrongPass123!",
    "expected_error": "Email hoặc mật khẩu không chính xác"
}
INVALID_PASSWORD = {
    "email": "testuser@example.com",
    "password": "wrong_password",
    "expected_error": "Email hoặc mật khẩu không chính xác"
}   

INVALID_EMAIL_FORMAT = {
    "email": "invalid-email-format",
    "password": "StrongPass123!",
    "expected_error": "Email không hợp lệ"
}

