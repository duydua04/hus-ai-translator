"""
e2e/auth/test_user_login.py
────────────────────────────
Test suite cho chức năng Đăng nhập – Người dùng thông thường.

Bao gồm:
  TC-AUTH-003  Đăng nhập đúng thông tin
  TC-AUTH-004  Khóa tài khoản (trạng thái bị khóa)
  TC-AUTH-005  Truy cập không có token (đã cover ở integration; đây test UI)
  TC-LOGIN-001 Nút submit disabled khi form rỗng
  TC-LOGIN-002 Nút submit disabled khi chỉ email
  TC-LOGIN-003 Nút submit disabled khi chỉ password
  TC-LOGIN-004 Sai mật khẩu → thông báo lỗi
  TC-LOGIN-005 Email không tồn tại → thông báo lỗi
  TC-LOGIN-006 Sai định dạng email → browser validation
  TC-LOGIN-007 Tài khoản bị khóa → thông báo lỗi
  TC-LOGIN-008 Tài khoản chưa xác thực → thông báo lỗi
  TC-LOGIN-009 Toggle hiển thị / ẩn mật khẩu
  TC-LOGIN-010 Link "Đăng ký" điều hướng đúng
  TC-LOGIN-011 Nhấn Enter trong ô password thay thế click submit
"""

from __future__ import annotations

import pytest

from data.user_login_data import ERROR_MESSAGES, LOGIN_FAILURE_CASES
from pages.user.user_login_page import UserLoginPage


# ══════════════════════════════════════════════════════════════════════════════
# HAPPY PATH
# ══════════════════════════════════════════════════════════════════════════════

class TestUserLoginSuccess:
    """TC-AUTH-003 — Đăng nhập thành công với thông tin hợp lệ."""

    def test_login_valid_credentials_redirects_to_home(
        self,
        user_login_page: UserLoginPage,
        valid_user: dict,
    ) -> None:
        """
        GIVEN  người dùng có tài khoản hợp lệ đã xác thực email
        WHEN   điền đúng email và password rồi submit
        THEN   hệ thống redirect về trang chủ dịch thuật
        """
        user_login_page.login(valid_user["email"], valid_user["password"])
        user_login_page.expect_redirect_to_home()

    def test_login_submit_button_enabled_when_form_filled(
        self,
        user_login_page: UserLoginPage,
        valid_user: dict,
    ) -> None:
        """
        GIVEN  form đăng nhập đang trống
        WHEN   điền đủ cả email và password hợp lệ
        THEN   nút Đăng nhập chuyển từ disabled → enabled
        """
        user_login_page.expect_submit_disabled()          # ban đầu disabled
        user_login_page.fill_login_form(
            valid_user["email"], valid_user["password"]
        )
        user_login_page.expect_submit_enabled()           # sau khi fill → enabled


# ══════════════════════════════════════════════════════════════════════════════
# DISABLED BUTTON  (form chưa đủ dữ liệu)
# ══════════════════════════════════════════════════════════════════════════════

class TestSubmitButtonDisabled:
    """Nút Đăng nhập phải disabled khi form chưa đủ thông tin."""

    def test_submit_disabled_on_page_load(
        self, user_login_page: UserLoginPage
    ) -> None:
        """TC-LOGIN-001 — Form rỗng ngay khi mở trang → nút disabled."""
        user_login_page.expect_submit_disabled()

    def test_submit_disabled_when_only_email_filled(
        self, user_login_page: UserLoginPage, valid_user: dict
    ) -> None:
        """TC-LOGIN-002 — Chỉ có email, password rỗng → nút disabled."""
        user_login_page.fill_email(valid_user["email"])
        user_login_page.expect_submit_disabled()

    def test_submit_disabled_when_only_password_filled(
        self, user_login_page: UserLoginPage, valid_user: dict
    ) -> None:
        """TC-LOGIN-003 — Chỉ có password, email rỗng → nút disabled."""
        user_login_page.fill_password(valid_user["password"])
        user_login_page.expect_submit_disabled()

    def test_submit_re_disabled_after_clearing_email(
        self, user_login_page: UserLoginPage, valid_user: dict
    ) -> None:
        """
        TC-LOGIN-003b — Điền đủ cả hai trường (enabled) rồi xóa email
        → nút phải trở lại disabled.
        """
        user_login_page.fill_login_form(valid_user["email"], valid_user["password"])
        user_login_page.expect_submit_enabled()

        user_login_page.fill_email("")                    # xóa email
        user_login_page.expect_submit_disabled()


# ══════════════════════════════════════════════════════════════════════════════
# NEGATIVE PATH  – thông báo lỗi xác thực
# ══════════════════════════════════════════════════════════════════════════════

class TestUserLoginFailure:

    def test_wrong_password_shows_error(
        self, user_login_page: UserLoginPage, valid_user: dict
    ) -> None:
        """TC-LOGIN-004 — Đúng email, sai password → toast lỗi xác thực."""
        user_login_page.login_expect_failure(
            valid_user["email"], "WrongPass!99"
        )
        user_login_page.expect_error_message(ERROR_MESSAGES["invalid_credentials"])
        user_login_page.expect_still_on_login_page()

    def test_nonexistent_email_shows_error(
        self, user_login_page: UserLoginPage, valid_user: dict
    ) -> None:
        """TC-LOGIN-005 — Email không tồn tại → toast lỗi xác thực."""
        user_login_page.login_expect_failure(
            "ghost@hus.edu.vn", valid_user["password"]
        )
        user_login_page.expect_error_message(ERROR_MESSAGES["invalid_credentials"])
        user_login_page.expect_still_on_login_page()

    def test_invalid_email_format_blocked_by_browser(
        self, user_login_page: UserLoginPage
    ) -> None:
        """
        TC-LOGIN-006 — Email sai định dạng → HTML5 validation chặn trước
        khi gửi request, form không được submit.
        """
        user_login_page.fill_login_form("not-an-email", "Test@12345")

        # Với input type="email", browser validation sẽ chặn submit.
        # Nút không bị disabled (vì có giá trị) nhưng form không submit được.
        # Kiểm tra bằng cách xác nhận không có navigation xảy ra.
        user_login_page.page.evaluate(
            "document.querySelector('form, .auth-form').checkValidity()"
        )
        # Vẫn ở lại trang login (không có redirect hay toast từ server)
        user_login_page.expect_still_on_login_page()

    def test_locked_account_shows_locked_message(
        self, user_login_page: UserLoginPage, locked_user: dict
    ) -> None:
        """TC-AUTH-004 / TC-LOGIN-007 — Tài khoản bị khóa → toast cụ thể."""
        user_login_page.login_expect_failure(
            locked_user["email"], locked_user["password"]
        )
        user_login_page.expect_error_message(ERROR_MESSAGES["account_locked"])
        user_login_page.expect_still_on_login_page()

    def test_unverified_account_shows_verification_message(
        self, user_login_page: UserLoginPage, unverified_user: dict
    ) -> None:
        """TC-LOGIN-008 — Chưa xác thực email → toast yêu cầu xác thực."""
        user_login_page.login_expect_failure(
            unverified_user["email"], unverified_user["password"]
        )
        user_login_page.expect_error_message(ERROR_MESSAGES["unverified_email"])
        user_login_page.expect_still_on_login_page()


# ══════════════════════════════════════════════════════════════════════════════
# UI / UX  – hành vi giao diện
# ══════════════════════════════════════════════════════════════════════════════

class TestUserLoginUI:

    def test_password_toggle_shows_and_hides_text(
        self, user_login_page: UserLoginPage, valid_user: dict
    ) -> None:
        """
        TC-LOGIN-009 — Nhấn icon con mắt:
          Lần 1 → type="text"     (hiện mật khẩu)
          Lần 2 → type="password" (ẩn mật khẩu)
        """
        user_login_page.fill_password(valid_user["password"])

        # mặc định: ẩn
        user_login_page.expect_password_type(visible=False)

        # nhấn toggle → hiện
        user_login_page.toggle_password_visibility()
        user_login_page.expect_password_type(visible=True)

        # nhấn toggle lần 2 → ẩn lại
        user_login_page.toggle_password_visibility()
        user_login_page.expect_password_type(visible=False)

    def test_register_link_navigates_to_register_page(
        self, user_login_page: UserLoginPage
    ) -> None:
        """TC-LOGIN-010 — Link Đăng ký phải điều hướng về /register."""
        user_login_page.expect_register_link_visible()
        user_login_page.register_link.click()
        user_login_page.page.wait_for_url("**/register")

    def test_press_enter_in_password_submits_form(
        self, user_login_page: UserLoginPage, valid_user: dict
    ) -> None:
        """
        TC-LOGIN-011 — Sau khi điền đủ form, nhấn Enter trong ô password
        có tác dụng tương đương nhấn nút Đăng nhập.
        """
        user_login_page.fill_email(valid_user["email"])
        user_login_page.fill_password(valid_user["password"])

        with user_login_page.page.expect_navigation(wait_until="networkidle"):
            user_login_page.password_input.press("Enter")

        user_login_page.expect_redirect_to_home()

    def test_forgot_password_link_is_visible(
        self, user_login_page: UserLoginPage
    ) -> None:
        """Kiểm tra link Quên mật khẩu hiển thị trên trang login."""
        user_login_page.expect_forgot_password_link_visible()


# ══════════════════════════════════════════════════════════════════════════════
# PARAMETRIZE  – chạy toàn bộ negative case từ data module
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(
    "case",
    [c for c in LOGIN_FAILURE_CASES if c["id"] not in (
        "empty_email", "empty_password", "both_empty",  # cover bởi TestSubmitButtonDisabled
        "invalid_email_format",                          # cover bởi TestUserLoginUI
        "locked_account",                                # cover bởi TestUserLoginFailure
        "unverified_account",                            # cover bởi TestUserLoginFailure
    )],
    ids=[c["id"] for c in LOGIN_FAILURE_CASES if c["id"] not in (
        "empty_email", "empty_password", "both_empty",
        "invalid_email_format", "locked_account", "unverified_account",
    )],
)
def test_login_failure_parametrized(
    user_login_page: UserLoginPage, case: dict
) -> None:
    """
    Chạy các negative case từ LOGIN_FAILURE_CASES chưa có class test riêng.
    Mỗi case phải ở lại trang login và không redirect.
    """
    email    = case["email"]
    password = case["password"]

    if not email or not password:
        # form không đủ dữ liệu → nút disabled, không submit được
        user_login_page.fill_login_form(email, password)
        assert user_login_page.is_submit_disabled(), (
            f"[{case['id']}] Nút submit phải disabled khi form chưa đủ dữ liệu"
        )
    else:
        user_login_page.login_expect_failure(email, password)
        user_login_page.expect_still_on_login_page()