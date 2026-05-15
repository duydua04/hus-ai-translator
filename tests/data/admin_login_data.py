VALID_ADMIN_LOGIN = {
    "email": "admin123@example.com",
    "password": "admin123",
    "expected_error": False
}

INVALID_ADMIN_PASSWORD = {
    "email": "admin123@example.com",
    "password": "wrong_password",
    "expected_error": True
}

LOCKED_ADMIN_ACCOUNT = {
    "email": "locked_admin@example.com",
    "password": "admin123",
    "expected_error": True
}