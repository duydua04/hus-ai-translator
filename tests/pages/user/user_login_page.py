"""
UserLoginPage
─────────────
Page Object cho trang đăng nhập của người dùng thông thường.
Kế thừa BaseLoginPage, bổ sung:
  • URL cụ thể
  • Locator chỉ xuất hiện trên trang user (link đăng ký, quên mật khẩu)
  • Assertion sau đăng nhập thành công (redirect về trang chủ dịch thuật)
"""

from __future__ import annotations

from playwright.sync_api import Page, Locator, expect

from pages.base_login_page import BaseLoginPage


class UserLoginPage(BaseLoginPage):

    URL = "/login"

    # ── locator bổ sung (chỉ có ở trang user login) ──────────────────────────
    _REGISTER_PATH   = "/register"
    _REGISTER_LINK   = 'a[href="/register"]'
    _FORGOT_PW_LINK  = 'a[href*="forgot"]'
    _PAGE_HEADING    = '.auth-form__heading, h1, h2'

    # redirect sau login thành công
    _HOME_INDICATOR  = '.home-page, [data-page="home"], .translate-section'

    def __init__(self, page: Page, base_url: str = "") -> None:
        super().__init__(page, base_url)

    # ── element accessors bổ sung ────────────────────────────────────────────
    @property
    def register_link(self) -> Locator:
        return self.page.locator(self._REGISTER_LINK)

    @property
    def forgot_password_link(self) -> Locator:
        return self.page.locator(self._FORGOT_PW_LINK)

    # ── high-level: đăng nhập hoàn chỉnh và chờ redirect ────────────────────
    def login(self, email: str, password: str) -> None:
        """
        Điền form → submit → chờ redirect về trang chủ.
        Dùng cho happy-path test case.
        """
        self.fill_login_form(email, password)
        with self.page.expect_navigation(wait_until="networkidle"):
            self.click_submit()

    def login_expect_failure(self, email: str, password: str) -> None:
        """
        Điền form → submit → KHÔNG chờ redirect (dự kiến thất bại).
        Dùng cho negative test case.
        """
        self.fill_login_form(email, password)
        self.click_submit()
        # chờ toast lỗi xuất hiện thay vì navigation
        self.page.wait_for_timeout(800)

    # ── assertions bổ sung ───────────────────────────────────────────────────
    def expect_redirect_to_home(self) -> None:
        """Sau đăng nhập thành công, phải chuyển về trang chủ."""
        expect(self.page.locator(self._HOME_INDICATOR)).to_be_visible(timeout=8_000)

    def expect_still_on_login_page(self) -> None:
        """Sau lỗi, phải ở lại trang login (không redirect)."""
        self.expect_on_login_page()

    def expect_register_link_visible(self) -> None:
        expect(self.register_link).to_be_visible()

    def expect_forgot_password_link_visible(self) -> None:
        expect(self.forgot_password_link).to_be_visible()

    def click_register_link(self) -> None:
        """Nhấn link Đăng ký và chờ navigation về /register."""
        self.register_link.click()
        self.page.wait_for_url(f"**{self._REGISTER_PATH}")