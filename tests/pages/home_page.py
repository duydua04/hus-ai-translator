# tests/pages/home_page.py

from playwright.sync_api import expect


class HomePage:
    def __init__(self, page):
        self.page = page

        # input/output
        self.input_box = page.locator("#source-text")
        self.output_box = page.locator("#translated-text")

        # buttons
        self.translate_btn = page.locator("text=Dịch ngay")
        self.clear_btn = page.locator(".icon-trash")
        self.copy_btn = page.locator(".icon-copy")
        self.swap_btn = page.locator(".icon-swap")
        self.login_btn = page.locator("text=Đăng nhập")

        # messages
        self.error = page.locator(".error-message")

    # ---------------- ACTIONS ----------------

    def open(self):
        self.page.goto("/")

    def enter_text(self, text: str):
        self.input_box.fill(text)

    def translate(self):
        self.translate_btn.click()

    def clear_text(self):
        self.clear_btn.click()

    def copy_result(self):
        self.copy_btn.click()

    def swap_language(self):
        self.swap_btn.click()

    def click_login(self):
        self.login_btn.click()

    # ---------------- ASSERTIONS ----------------

    def expect_translation_result(self):
        expect(self.output_box).not_to_be_empty()

    def expect_empty_input_error(self):
        expect(self.error).to_be_visible()

    def expect_security_safe(self):
        # check script not executed
        expect(self.page.locator("text=alert")).not_to_be_visible()

    def get_output_text(self):
        return self.output_box.text_content()