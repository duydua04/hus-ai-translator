"""
BaseLoginPage
─────────────
Lớp cha trừu tượng cho tất cả các trang đăng nhập trong hệ thống.
Đóng gói toàn bộ locator và thao tác tương tác với form .auth-form,
giúp các lớp con (UserLoginPage, AdminLoginPage) tái sử dụng mà không
cần khai báo lại selector.
"""

from __future__ import annotations

from playwright.sync_api import Page, Locator, expect


class BaseLoginPage:
    """
    Ánh xạ đến form HTML:
        <div class="auth-form">
            <input name="email"    type="email"    class="auth-form__input">
            <input name="password" type="password" class="auth-form__input">
            <button class="auth-form__submit btn btn--primary">Đăng nhập</button>
        </div>
    """

    # ── URL phải được override ở lớp con ────────────────────────────────────
    URL: str = ""

    # ── Locators ─────────────────────────────────────────────────────────────
    _EMAIL_INPUT    = 'input[name="email"]'
    _PASSWORD_INPUT = 'input[name="password"]'
    _SUBMIT_BTN     = 'button.auth-form__submit'
    _TOGGLE_PW_BTN  = 'button.auth-form__toggle-pw'
    _PW_SHOW_ICON   = 'button.auth-form__toggle-pw i.bx-show'
    _PW_HIDE_ICON   = 'button.auth-form__toggle-pw i.bx-hide'

    # toast / alert thông báo lỗi – điều chỉnh selector nếu UI thay đổi
    _ERROR_TOAST    = '.toast--error, .alert--error, [role="alert"]'

    def __init__(self, page: Page, base_url: str = "") -> None:
        self.page     = page
        self.base_url = base_url.rstrip("/")   # bỏ trailing slash nếu có

    # ── navigation ───────────────────────────────────────────────────────────
    def navigate(self) -> None:
        """Mở trang đăng nhập tương ứng."""
        assert self.URL, f"{self.__class__.__name__}.URL chưa được khai báo"
        full_url = f"{self.base_url}{self.URL}" if self.base_url else self.URL
        self.page.goto(full_url)
        self.page.wait_for_load_state("networkidle")

    def _full_url(self, path: str) -> str:
        """Trả về URL tuyệt đối từ path tương đối."""
        return f"{self.base_url}{path}" if self.base_url else path

    # ── element accessors ────────────────────────────────────────────────────
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
    def error_toast(self) -> Locator:
        return self.page.locator(self._ERROR_TOAST)

    # ── low-level actions ────────────────────────────────────────────────────
    def fill_email(self, email: str) -> None:
        self.email_input.clear()
        self.email_input.fill(email)

    def fill_password(self, password: str) -> None:
        self.password_input.clear()
        self.password_input.fill(password)

    def click_submit(self) -> None:
        self.submit_button.click()

    def toggle_password_visibility(self) -> None:
        """Nhấn nút con mắt để ẩn/hiện mật khẩu."""
        self.toggle_pw_button.click()

    # ── high-level actions ───────────────────────────────────────────────────
    def fill_login_form(self, email: str, password: str) -> None:
        """Điền đầy đủ email và password vào form."""
        self.fill_email(email)
        self.fill_password(password)

    def submit_login(self, email: str, password: str) -> None:
        """Điền form và nhấn nút Đăng nhập."""
        self.fill_login_form(email, password)
        self.click_submit()

    # ── assertions ───────────────────────────────────────────────────────────
    def expect_submit_disabled(self) -> None:
        """Xác nhận nút Đăng nhập đang bị disabled (khi form chưa hợp lệ)."""
        expect(self.submit_button).to_be_disabled()

    def expect_submit_enabled(self) -> None:
        """Xác nhận nút Đăng nhập có thể bấm được."""
        expect(self.submit_button).to_be_enabled()

    def expect_error_message(self, text: str) -> None:
        """Xác nhận thông báo lỗi chứa nội dung mong đợi."""
        expect(self.error_toast).to_be_visible()
        expect(self.error_toast).to_contain_text(text)

    def expect_password_type(self, visible: bool) -> None:
        """
        Xác nhận trạng thái hiển thị mật khẩu.
        visible=True  → input type="text"  (đang hiện mật khẩu)
        visible=False → input type="password" (đang ẩn mật khẩu)
        """
        expected_type = "text" if visible else "password"
        expect(self.password_input).to_have_attribute("type", expected_type)

    def expect_on_login_page(self) -> None:
        """Xác nhận đang ở trang đăng nhập (chưa redirect)."""
        expect(self.page).to_have_url(self._full_url(self.URL))

    def is_submit_disabled(self) -> bool:
        return self.submit_button.is_disabled()