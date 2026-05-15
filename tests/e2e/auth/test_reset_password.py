# tests/e2e/auth/test_reset_password.py

import pytest
import allure

from tests.data.reset_password_data import *
from tests.pages.user.reset_password_page import ResetPasswordPage


@allure.feature("Authentication")
@allure.story("Reset Password")
class TestResetPassword:

    def test_reset_with_non_existing_email(self, page):
        reset = ResetPasswordPage(page)
        reset.open()

        reset.request_reset(NON_EXISTING_EMAIL["email"])

        assert reset.is_email_not_found_error()

    def test_invalid_email_format(self, page):
        reset = ResetPasswordPage(page)
        reset.open()

        reset.request_reset(INVALID_EMAIL_FORMAT["email"])

        assert reset.is_invalid_email_format_error()

    def test_reset_password_mismatch(self, page):
        reset = ResetPasswordPage(page)
        reset.open()

        reset.request_reset(EXISTING_EMAIL["email"])
        reset.set_new_password(
            NEW_PASSWORD["password"],
            WRONG_CONFIRM_PASSWORD["confirm_password"]
        )

        assert reset.is_password_mismatch_error()

    def test_verify_correct_otp(self, page):
        reset = ResetPasswordPage(page)
        reset.open()

        reset.request_reset(EXISTING_EMAIL["email"])
        reset.enter_otp(OTP_CORRECT["otp"])

        assert reset.is_otp_verified()

    def test_verify_wrong_otp(self, page):
        reset = ResetPasswordPage(page)
        reset.open()

        reset.request_reset(EXISTING_EMAIL["email"])
        reset.enter_otp(OTP_WRONG["otp"])

        assert reset.is_otp_invalid_error()

    def test_expired_otp(self, page):
        reset = ResetPasswordPage(page)
        reset.open()

        reset.request_reset(EXISTING_EMAIL["email"])
        reset.enter_otp(OTP_EXPIRED["otp"])

        assert reset.is_otp_expired_error()

    def test_incomplete_otp(self, page):
        reset = ResetPasswordPage(page)
        reset.open()

        reset.request_reset(EXISTING_EMAIL["email"])
        reset.enter_otp(OTP_INCOMPLETE["otp"])

        assert reset.is_otp_format_error()

    def test_resend_otp(self, page):
        reset = ResetPasswordPage(page)
        reset.open()

        reset.request_reset(EXISTING_EMAIL["email"])
        reset.click_resend_otp()

        assert reset.is_otp_resent_success()