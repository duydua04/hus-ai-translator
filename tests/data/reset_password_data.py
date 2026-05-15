# tests/data/reset_password_data.py

EXISTING_EMAIL = {
    "email": "testuser@gmail.com"
}

NON_EXISTING_EMAIL = {
    "email": "notfound@gmail.com"
}

INVALID_EMAIL_FORMAT = {
    "email": "abc@@gmail"
}

OTP_CORRECT = {
    "otp": "123456"
}

OTP_WRONG = {
    "otp": "000000"
}

OTP_EXPIRED = {
    "otp": "111111"
}

OTP_INCOMPLETE = {
    "otp": "123"
}

NEW_PASSWORD = {
    "password": "NewPassword123!"
}

WRONG_CONFIRM_PASSWORD = {
    "password": "NewPassword123!",
    "confirm_password": "WrongPassword123!"
}