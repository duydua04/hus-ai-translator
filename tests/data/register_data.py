# tests/data/register_data.py


# =========================================================
# COMMON DATA
# =========================================================

VALID_USER = {
    "full_name": "Test User",
    "email": "test@gmail.com",
    "password": "StrongPass123!",
    "confirm_password": "StrongPass123!"
}


# =========================================================
# SUCCESS CASE
# =========================================================

REGISTER_SUCCESS_CASE = {
    "name": "register_success",
    "data": VALID_USER
}


# =========================================================
# DUPLICATE EMAIL
# =========================================================

REGISTER_DUPLICATE_EMAIL_CASE = {
    "name": "duplicate_email",

    "data": {
        "full_name": "Duplicate User",
        "password": "StrongPass123!"
    },

    "expected_error": "Email này đã được đăng ký"
}


# =========================================================
# VALIDATION CASES
# =========================================================

REGISTER_VALIDATION_CASES = [

    # -----------------------------------------------------
    # Confirm password mismatch
    # -----------------------------------------------------

    {
        "name": "confirm_password_not_match",

        "override": {
            "confirm_password": "WrongPassword123!"
        },

        "expected_error": "Mật khẩu xác nhận không khớp"
    },

    # -----------------------------------------------------
    # Invalid email
    # -----------------------------------------------------

    {
        "name": "invalid_email_format",

        "override": {
            "email": "invalid-email"
        },

        "expected_error": "Vui lòng nhập email"
    },

    # -----------------------------------------------------
    # Password too short
    # -----------------------------------------------------

    {
        "name": "short_password",

        "override": {
            "password": "123",
            "confirm_password": "123"
        },

        "expected_error": "Mật khẩu tối thiểu 8 ký tự"
    },

    # -----------------------------------------------------
    # Password lowercase only
    # -----------------------------------------------------

    {
        "name": "password_lowercase_only",

        "override": {
            "password": "onlylowercase",
            "confirm_password": "onlylowercase"
        },

        "expected_error": "Mật khẩu phải chứa chữ hoa"
    },

    # -----------------------------------------------------
    # Password no number
    # -----------------------------------------------------

    {
        "name": "password_no_number",

        "override": {
            "password": "OnlyLetters!",
            "confirm_password": "OnlyLetters!"
        },

        "expected_error": "Mật khẩu phải chứa số"
    },

    # -----------------------------------------------------
    # Password no special character
    # -----------------------------------------------------

    {
        "name": "password_no_special_character",

        "override": {
            "password": "StrongPass123",
            "confirm_password": "StrongPass123"
        },

        "expected_error": "Mật khẩu phải chứa ký tự đặc biệt"
    },

    # -----------------------------------------------------
    # Password contains whitespace
    # -----------------------------------------------------

    {
        "name": "password_contains_whitespace",

        "override": {
            "password": "Strong Pass123!",
            "confirm_password": "Strong Pass123!"
        },

        "expected_error": "Mật khẩu không được chứa khoảng trắng"
    },

    # -----------------------------------------------------
    # Password same as email
    # -----------------------------------------------------

    {
        "name": "password_same_as_email",

        "override": {
            "password": "test@gmail.com",
            "confirm_password": "test@gmail.com"
        },

        "expected_error": "Mật khẩu không được trùng Email"
    },

    # -----------------------------------------------------
    # Password too long
    # -----------------------------------------------------

    {
        "name": "password_too_long",

        "override": {
            "password": "A" * 300,
            "confirm_password": "A" * 300
        },

        "expected_error": "Mật khẩu vượt quá độ dài cho phép"
    },

    # -----------------------------------------------------
    # Empty required fields
    # -----------------------------------------------------

    {
        "name": "empty_required_fields",

        "override": {
            "full_name": "",
            "email": "",
            "password": "",
            "confirm_password": ""
        },

        "expected_error": "Vui lòng nhập họ tên"
    },

    {
        "name": "password_valid",

        "override": {
            "password": "StrongPass123!",
            "confirm_password": "StrongPass123!"
        },


        "expected_error": "Đăng ký thành công"
    },
    {
    "name": "firstname_xss_injection_escape",

    "override": {
        "full_name": "<script>alert(1)</script>",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!"
    },

    "expected_error": "Đăng ký thành công"
}
]