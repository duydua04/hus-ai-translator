from playwright.sync_api import Page


class BaseLoginPage:

    def __init__(self, page: Page):
        self.page = page

        self._email_input = page.locator(
            "input[type='email']"
        )

        self._password_input = page.locator(
            "input[type='password']"
        )

        self._submit_btn = page.get_by_role(
            "button",
            name="Đăng nhập"
        )

        self._success_msg = page.locator(
            '.success-message, '
            '.alert-success, '
            '[role="alert"].success'
        )

    @property
    def email_input(self):
        return self._email_input

    @property
    def password_input(self):
        return self._password_input

    @property
    def login_button(self):
        return self._submit_btn

    def navigate(self):
        self.page.goto(self.URL)

    def login(self, email: str, password: str):
        self._email_input.fill(email)
        self._password_input.fill(password)

        self._submit_btn.click()