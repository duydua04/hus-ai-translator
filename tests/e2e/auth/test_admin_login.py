"""
e2e/auth/test_admin_login.py
─────────────────────────────
Test suite cho chức năng Đăng nhập – Quản trị viên (Admin).

Lưu ý HTML form admin dùng class khác hoàn toàn so với user:
  .login-input / .login-btn / .login-eye-btn   (admin)
  .auth-form__input / .auth-form__submit        (user)

Tài khoản admin có sẵn:
  email    : admin123@gmail.com
  password : admin123

Test cases:
  TC-ADMIN-LOGIN-001  Đăng nhập thành công → redirect Dashboard
  TC-ADMIN-LOGIN-002  Nút submit enabled khi điền đủ (form dùng required, không disabled)
  TC-ADMIN-LOGIN-003  Sai mật khẩu → thông báo lỗi
  TC-ADMIN-LOGIN-004  Email không tồn tại → thông báo lỗi
  TC-ADMIN-LOGIN-005  Tài khoản user thường đăng nhập vào trang admin → bị từ chối
  TC-ADMIN-LOGIN-006  Toggle hiển thị / ẩn mật khẩu
  TC-ADMIN-LOGIN-007  Nhấn Enter trong ô password thay thế click submit
  TC-ADMIN-LOGIN-008  Email rỗng → HTML5 required chặn (không gửi request)
  TC-ADMIN-LOGIN-009  Password rỗng → HTML5 required chặn
  TC-ADMIN-LOGIN-010  Sai định dạng email → HTML5 type=email chặn
"""

from __future__ import annotations

import pytest

from data.admin_login_data import ERROR_MESSAGES, LOGIN_FAILURE_CASES, VALID_ADMIN
from pages.admin.admin_login_page import AdminLoginPage


# ══════════════════════════════════════════════════════════════════════════════
# HAPPY PATH
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminLoginSuccess:

    def test_login_valid_admin_redirects_to_dashboard(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """
        TC-ADMIN-LOGIN-001
        GIVEN  tài khoản admin hợp lệ (admin123@gmail.com / admin123)
        WHEN   điền đúng email và password rồi submit
        THEN   redirect về trang Admin Dashboard
        """
        admin_login_page.login(VALID_ADMIN["email"], VALID_ADMIN["password"])
        admin_login_page.expect_redirect_to_dashboard()

    def test_submit_button_enabled_when_form_filled(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """
        TC-ADMIN-LOGIN-002
        Form admin dùng thuộc tính HTML 'required' thay vì disabled JS,
        nên nút submit LUÔN enabled — browser chặn tại tầng HTML5 validation.
        """
        # ban đầu: nút vẫn enabled (khác với user form)
        admin_login_page.expect_submit_enabled()

        # sau khi điền: vẫn enabled, không thay đổi trạng thái
        admin_login_page.fill_login_form(
            VALID_ADMIN["email"], VALID_ADMIN["password"]
        )
        admin_login_page.expect_submit_enabled()


# ══════════════════════════════════════════════════════════════════════════════
# NEGATIVE PATH  – sai thông tin xác thực
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminLoginFailure:

    def test_wrong_password_shows_error(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """
        TC-ADMIN-LOGIN-003
        GIVEN  đúng email admin, sai mật khẩu
        WHEN   submit form
        THEN   hiển thị thông báo lỗi xác thực, ở lại trang login
        """
        admin_login_page.login_expect_failure(
            VALID_ADMIN["email"], "wrongpassword"
        )
        admin_login_page.expect_error_message(ERROR_MESSAGES["invalid_credentials"])
        admin_login_page.expect_on_login_page()

    def test_nonexistent_email_shows_error(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """
        TC-ADMIN-LOGIN-004
        GIVEN  email không tồn tại trong hệ thống
        WHEN   submit form
        THEN   hiển thị thông báo lỗi xác thực, ở lại trang login
        """
        admin_login_page.login_expect_failure(
            "ghost_admin@gmail.com", VALID_ADMIN["password"]
        )
        admin_login_page.expect_error_message(ERROR_MESSAGES["invalid_credentials"])
        admin_login_page.expect_on_login_page()

    def test_regular_user_account_rejected_on_admin_form(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """
        TC-ADMIN-LOGIN-005
        GIVEN  tài khoản user thường (không phải admin)
        WHEN   đăng nhập vào trang /admin/login
        THEN   bị từ chối, ở lại trang login (không redirect Dashboard)
        """
        admin_login_page.login_expect_failure(
            "user_test@hus.edu.vn", "Test@12345"
        )
        admin_login_page.expect_on_login_page()


# ══════════════════════════════════════════════════════════════════════════════
# HTML5 VALIDATION  – browser chặn trước khi gửi request
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminLoginHTML5Validation:
    """
    Form admin dùng thuộc tính 'required' và type='email' của HTML5.
    Các trường hợp này bị browser chặn — không gửi request lên server,
    không có toast lỗi từ backend — chỉ xác nhận không có navigation.
    """

    def test_empty_email_blocked_by_required(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """TC-ADMIN-LOGIN-008 — Email rỗng + required → form không submit."""
        admin_login_page.fill_password(VALID_ADMIN["password"])
        # click submit nhưng browser chặn vì email rỗng + required
        admin_login_page.submit_button.click()
        admin_login_page.page.wait_for_timeout(500)
        admin_login_page.expect_on_login_page()

    def test_empty_password_blocked_by_required(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """TC-ADMIN-LOGIN-009 — Password rỗng + required → form không submit."""
        admin_login_page.fill_email(VALID_ADMIN["email"])
        admin_login_page.submit_button.click()
        admin_login_page.page.wait_for_timeout(500)
        admin_login_page.expect_on_login_page()

    def test_invalid_email_format_blocked_by_type_validation(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """TC-ADMIN-LOGIN-010 — Sai định dạng email → type=email chặn submit."""
        admin_login_page.fill_email("not-valid-email")
        admin_login_page.fill_password(VALID_ADMIN["password"])
        admin_login_page.submit_button.click()
        admin_login_page.page.wait_for_timeout(500)

        # Xác nhận form không hợp lệ qua checkValidity()
        is_valid = admin_login_page.page.evaluate(
            "document.querySelector('form').checkValidity()"
        )
        assert not is_valid, "Form phải invalid khi email sai định dạng"
        admin_login_page.expect_on_login_page()


# ══════════════════════════════════════════════════════════════════════════════
# UI / UX
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminLoginUI:

    def test_password_toggle_show_and_hide(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """
        TC-ADMIN-LOGIN-006
        Nhấn icon .login-eye-btn:
          Lần 1 → type="text"     (hiện mật khẩu)
          Lần 2 → type="password" (ẩn mật khẩu)
        """
        admin_login_page.fill_password(VALID_ADMIN["password"])

        # mặc định: ẩn
        admin_login_page.expect_password_type(visible=False)

        # nhấn toggle → hiện
        admin_login_page.toggle_password_visibility()
        admin_login_page.expect_password_type(visible=True)

        # nhấn lại → ẩn
        admin_login_page.toggle_password_visibility()
        admin_login_page.expect_password_type(visible=False)

    def test_press_enter_in_password_submits_form(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """
        TC-ADMIN-LOGIN-007
        Sau khi điền đủ form, nhấn Enter trong ô password
        có tác dụng tương đương nhấn nút Đăng nhập.
        """
        admin_login_page.fill_email(VALID_ADMIN["email"])
        admin_login_page.fill_password(VALID_ADMIN["password"])

        with admin_login_page.page.expect_navigation(wait_until="networkidle"):
            admin_login_page.password_input.press("Enter")

        admin_login_page.expect_redirect_to_dashboard()

    def test_email_input_has_correct_placeholder(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """Input email phải có placeholder 'admin@example.com'."""
        expect_placeholder = "admin@example.com"
        expect(admin_login_page.email_input).to_have_attribute(
            "placeholder", expect_placeholder
        )

    def test_password_input_has_password_type_by_default(
        self, admin_login_page: AdminLoginPage
    ) -> None:
        """Input password mặc định phải là type='password' (ẩn ký tự)."""
        admin_login_page.expect_password_type(visible=False)


# ══════════════════════════════════════════════════════════════════════════════
# PARAMETRIZE  – chạy các negative case từ data module
# ══════════════════════════════════════════════════════════════════════════════

# Loại bỏ các case đã có class test riêng
_SKIP_IDS = {
    "wrong_password",
    "wrong_email",
    "user_account_on_admin_form",
    "empty_email",
    "empty_password",
    "invalid_email_format",
}

_PARAM_CASES = [c for c in LOGIN_FAILURE_CASES if c["id"] not in _SKIP_IDS]


@pytest.mark.parametrize(
    "case", _PARAM_CASES, ids=[c["id"] for c in _PARAM_CASES]
)
def test_admin_login_failure_parametrized(
    admin_login_page: AdminLoginPage, case: dict
) -> None:
    """Chạy các negative case bổ sung chưa có test class riêng."""
    admin_login_page.login_expect_failure(case["email"], case["password"])
    admin_login_page.expect_on_login_page()