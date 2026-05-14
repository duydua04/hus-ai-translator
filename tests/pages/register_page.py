from playwright.sync_api import Page, Locator


class RegisterPage:

    URL_PATH = "/register"

    def __init__(self, page: Page):

        self.page = page

        self._full_name_input = page.locator(
            'input[name="full_name"]'
        )

        self._email_input = page.locator(
            'input[name="email"]'
        )

        self._password_input = page.locator(
            'input[name="password"]'
        )

        self._confirm_pw_input = page.locator(
            'input[name="confirm_password"]'
        )

        self._submit_btn = page.get_by_role(
            "button",
            name="Đăng ký"
        )

        self._success_msg = page.locator(
            '.success-message, '
            '.alert-success, '
            '[role="alert"].success'
        )

    def navigate(self, base_url: str):

        self.page.goto(f"{base_url}{self.URL_PATH}")

        return self

    def fill_full_name(self, value: str):

        self._full_name_input.fill(value)

        return self

    def fill_email(self, value: str):

        self._email_input.fill(value)

        return self

    def fill_password(self, value: str):

        self._password_input.fill(value)

        return self

    def fill_confirm_password(self, value: str):

        self._confirm_pw_input.fill(value)

        return self

    def fill_registration_form(
        self,
        full_name,
        email,
        password,
        confirm_password=None
    ):

        self.fill_full_name(full_name)
        self.fill_email(email)
        self.fill_password(password)
        self.fill_confirm_password(
            confirm_password or password
        )

        return self

    def click_register(
        self,
        wait_for_navigation=False
    ):

        self._submit_btn.click()

        return self

    def submit(
        self,
        full_name,
        email,
        password,
        confirm_password=None,
        wait_for_navigation=False
    ):

        self.fill_registration_form(
            full_name,
            email,
            password,
            confirm_password
        )

        self.click_register(wait_for_navigation)

        return self

    @property
    def success_message(self) -> Locator:

        return self._success_msg

    @property
    def email_error(self) -> Locator:

        return self.field_error("email")

    @property
    def password_error(self) -> Locator:

        return self.field_error("password")

    # def field_error(self, field: str) -> Locator:

    #     return self.page.locator(
    #         f'[data-error-for="{field}"], '
    #         f'.{field}-error, '
    #         f'text=/.*{field}.*/i'
    #     )