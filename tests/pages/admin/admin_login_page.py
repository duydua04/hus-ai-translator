"""
AdminLoginPage
──────────────
Page Object cho trang đăng nhập của quản trị viên.
KHÔNG kế thừa BaseLoginPage vì form admin dùng class CSS
hoàn toàn khác với form user:

  User form  : .auth-form__input  / .auth-form__submit  / .auth-form__toggle-pw
  Admin form : .login-input       / .login-btn           / .login-eye-btn

HTML tham chiếu:
  <input  class="login-input"        id="email"    type="email"    required>
  <input  class="login-input login-input--pw" id="password" type="password" required>
  <button class="login-eye-btn"      type="button" aria-label="Hiện mật khẩu">
  <button class="login-btn"          type="submit">Đăng nhập</button>
"""

from __future__ import annotations

from playwright.sync_api import Page, Locator, expect


class AdminLoginPage:

    # Admin chạy trên cổng riêng (3001), khác với user app (3000)
    PORT = 3001
    URL  = "/login"

    # ── Locators (ánh xạ đúng HTML admin form) ───────────────────────────────
    _EMAIL_INPUT    = '#email'
    _PASSWORD_INPUT = '#password'
    _SUBMIT_BTN     = 'button.login-btn[type="submit"]'
    _TOGGLE_PW_BTN  = 'button.login-eye-btn'
    _SHOW_ICON      = 'button.login-eye-btn i.bx-show'
    _HIDE_ICON      = 'button.login-eye-btn i.bx-hide'

    # thông báo lỗi – điều chỉnh selector theo UI thực tế
    _ERROR_MSG      = '.login-error, .alert--error, [role="alert"]'

    # chỉ có ở Dashboard sau khi đăng nhập thành công
    _DASHBOARD_INDICATOR = '.dashboard, [data-page="dashboard"], .admin-dashboard'

    def __init__(self, page: Page, base_url: str = "") -> None:
        self.page = page
        # Thay port trong base_url thành 3001 cho admin app.
        # VD: "http://localhost:3000" → "http://localhost:3001"
        if base_url:
            import re
            self.base_url = re.sub(r':\d+$', f':{self.PORT}', base_url.rstrip("/"))
        else:
            self.base_url = f"http://localhost:{self.PORT}"

    # ── helpers ───────────────────────────────────────────────────────────────
    def _full_url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    # ── navigation ────────────────────────────────────────────────────────────
    def navigate(self) -> None:
        self.page.goto(self._full_url(self.URL))
        self.page.wait_for_load_state("networkidle")

    # ── element accessors ─────────────────────────────────────────────────────
    @property
    def email_input(self) -> Locator:
        return self.page.locator(self._EMAIL_INPUT)

    @property
    def password_input(self) -> Locator:
        return self.page.locator(self._PASSWORD_INPUT)

    @property
    def submit_button(self) -> Locator:
        return self.page.locator(self._SUBMIT_BTN)

    @property
    def toggle_pw_button(self) -> Locator:
        return self.page.locator(self._TOGGLE_PW_BTN)

    @property
    def error_message(self) -> Locator:
        return self.page.locator(self._ERROR_MSG)

    # ── low-level actions ─────────────────────────────────────────────────────
    def fill_email(self, email: str) -> None:
        self.email_input.clear()
        self.email_input.fill(email)

    def fill_password(self, password: str) -> None:
        self.password_input.clear()
        self.password_input.fill(password)

    def click_submit(self) -> None:
        self.submit_button.click()

    def toggle_password_visibility(self) -> None:
        self.toggle_pw_button.click()

    def fill_login_form(self, email: str, password: str) -> None:
        self.fill_email(email)
        self.fill_password(password)

    # ── high-level ────────────────────────────────────────────────────────────
    def login(self, email: str, password: str) -> None:
        """Happy-path: điền form → submit → chờ redirect Dashboard."""
        self.fill_login_form(email, password)
        with self.page.expect_navigation(wait_until="networkidle"):
            self.click_submit()

    def login_expect_failure(self, email: str, password: str) -> None:
        """Negative-path: submit và chờ thông báo lỗi, không redirect."""
        self.fill_login_form(email, password)
        self.click_submit()
        self.page.wait_for_timeout(800)

    # ── assertions ────────────────────────────────────────────────────────────
    def expect_on_login_page(self) -> None:
        expect(self.page).to_have_url(self._full_url(self.URL))

    def expect_redirect_to_dashboard(self) -> None:
        expect(
            self.page.locator(self._DASHBOARD_INDICATOR)
        ).to_be_visible(timeout=8_000)

    def expect_error_message(self, text: str) -> None:
        expect(self.error_message).to_be_visible()
        expect(self.error_message).to_contain_text(text)

    def expect_submit_enabled(self) -> None:
        expect(self.submit_button).to_be_enabled()

    def expect_password_type(self, visible: bool) -> None:
        expected = "text" if visible else "password"
        expect(self.password_input).to_have_attribute("type", expected)

    def is_submit_enabled(self) -> bool:
        return self.submit_button.is_enabled()