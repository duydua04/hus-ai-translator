"""
Page Object: Trang đăng ký người dùng.
Selector dựa theo DOM thực tế (name attribute + class).
"""
import allure
from playwright.sync_api import Page, expect


class RegisterPage:

    URL_PATH = "/register"

    # ── Selectors ─────────────────────────────────────────────────────────────
    SEL_INPUT_FULLNAME         = '[name="full_name"]'
    SEL_INPUT_EMAIL            = '[name="email"]'
    SEL_INPUT_PASSWORD         = '[name="password"]'
    SEL_INPUT_CONFIRM_PASSWORD = '[name="confirm_password"]'
    SEL_BTN_SUBMIT             = 'button.auth-form__submit'
    SEL_LINK_LOGIN             = 'a[href="/login"]'

    # Thông báo lỗi inline — thẻ xuất hiện dưới field khi validate
    # Điều chỉnh nếu app dùng class khác
    SEL_ERROR_FULLNAME         = '.auth-form__field:has([name="full_name"]) .auth-form__error'
    SEL_ERROR_EMAIL            = '.auth-form__field:has([name="email"]) .auth-form__error'
    SEL_ERROR_PASSWORD         = '.auth-form__field:has([name="password"]) .auth-form__error'
    SEL_ERROR_CONFIRM          = '.auth-form__field:has([name="confirm_password"]) .auth-form__error'

    # Toast thông báo toàn cục
    SEL_ERROR_TOAST            = '.toast--error'
    SEL_SUCCESS_TOAST          = '.toast--success'

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self):
        with allure.step("Mở trang đăng ký"):
            self.page.goto(f"{self.base_url}{self.URL_PATH}")
            self.page.wait_for_load_state("networkidle")

    # ── Actions ───────────────────────────────────────────────────────────────

    def fill_fullname(self, value: str):
        self.page.fill(self.SEL_INPUT_FULLNAME, value)

    def fill_email(self, value: str):
        self.page.fill(self.SEL_INPUT_EMAIL, value)

    def fill_password(self, value: str):
        self.page.fill(self.SEL_INPUT_PASSWORD, value)

    def fill_confirm_password(self, value: str):
        self.page.fill(self.SEL_INPUT_CONFIRM_PASSWORD, value)

    def click_submit(self):
        self.page.click(self.SEL_BTN_SUBMIT)

    def click_login_link(self):
        self.page.click(self.SEL_LINK_LOGIN)

    def clear_field(self, selector: str):
        self.page.triple_click(selector)
        self.page.keyboard.press("Backspace")

    # ── Compound actions ──────────────────────────────────────────────────────

    def fill_form(self, full_name="", email="", password="", confirm_password=""):
        with allure.step(f"Điền form: full_name={full_name}, email={email}"):
            if full_name:
                self.fill_fullname(full_name)
            if email:
                self.fill_email(email)
            if password:
                self.fill_password(password)
            if confirm_password:
                self.fill_confirm_password(confirm_password)

    def register(self, full_name: str, email: str,
                 password: str, confirm_password: str):
        self.fill_form(full_name, email, password, confirm_password)
        with allure.step("Nhấn nút Đăng ký"):
            self.click_submit()

    # ── Getters / Assertions ──────────────────────────────────────────────────

    def _error_selector(self, field: str) -> str:
        mapping = {
            "full_name":        self.SEL_ERROR_FULLNAME,
            "email":            self.SEL_ERROR_EMAIL,
            "password":         self.SEL_ERROR_PASSWORD,
            "confirm_password": self.SEL_ERROR_CONFIRM,
        }
        if field not in mapping:
            raise ValueError(f"Field không hợp lệ: '{field}'")
        return mapping[field]

    def get_field_error(self, field: str) -> str:
        return self.page.text_content(self._error_selector(field)) or ""

    def get_toast_error(self) -> str:
        self.page.wait_for_selector(self.SEL_ERROR_TOAST, timeout=5000)
        return self.page.text_content(self.SEL_ERROR_TOAST) or ""

    def get_toast_success(self) -> str:
        self.page.wait_for_selector(self.SEL_SUCCESS_TOAST, timeout=5000)
        return self.page.text_content(self.SEL_SUCCESS_TOAST) or ""

    def is_on_register_page(self) -> bool:
        return self.URL_PATH in self.page.url

    def is_redirected_after_register(self) -> bool:
        self.page.wait_for_url(
            lambda url: "/login" in url or "/home" in url or url == self.base_url + "/",
            timeout=8000,
        )
        return True

    def expect_field_error(self, field: str, expected_text: str):
        with allure.step(f"Kiểm tra lỗi field '{field}': '{expected_text}'"):
            sel = self._error_selector(field)
            expect(self.page.locator(sel)).to_contain_text(expected_text)

    @property
    def field_selectors(self) -> dict:
        return {
            "full_name":        self.SEL_INPUT_FULLNAME,
            "email":            self.SEL_INPUT_EMAIL,
            "password":         self.SEL_INPUT_PASSWORD,
            "confirm_password": self.SEL_INPUT_CONFIRM_PASSWORD,
        }