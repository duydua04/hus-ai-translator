import pytest
import allure

from playwright.sync_api import expect

from tests.pages.user.user_login_page import UserLoginPage

from tests.data.user_login_data import (
    EMPTY_FIELDS,
    EMPTY_EMAIL,
    EMPTY_PASSWORD,
    INVALID_EMAIL,
    INVALID_PASSWORD,
    INVALID_EMAIL_FORMAT
)


@allure.feature("Authentication")
@allure.story("User Login")
class TestUserLogin:

    @allure.title("Login successfully with valid user")
    def test_valid_user_login(
        self,
        page,
        registered_user
    ):
        login_page = UserLoginPage(page)

        login_page.navigate()

        login_page.login(
            registered_user["email"],
            registered_user["password"]
        )

        expect(page).to_have_url(
            "http://localhost:3000/home/text"
        )

    @allure.title("Login failed with invalid password")
    def test_invalid_password_login(
        self,
        page,
        registered_user
    ):
        login_page = UserLoginPage(page)

        login_page.navigate()

        login_page.login(
            registered_user["email"],
            "wrong_password"
        )
        page.pause()
        
        expect(
            login_page.get_by_text(INVALID_PASSWORD["expected_error"])
        ).to_be_visible(timeout=10000)

    @pytest.mark.parametrize(
        "test_data",
        [
            EMPTY_FIELDS,
            EMPTY_EMAIL,
            EMPTY_PASSWORD
        ]
    )
    @allure.title("Login button disabled with empty fields")
    def test_login_button_disabled(
        self,
        page,
        test_data
    ):
        login_page = UserLoginPage(page)

        login_page.navigate()

        login_page.email_input.fill(
            test_data["email"]
        )

        login_page.password_input.fill(
            test_data["password"]
        )

        expect(
            login_page.login_button
        ).to_be_disabled()

    @allure.title("Login failed with invalid email")
    def test_invalid_email_login(
        self,
        page
    ):
        login_page = UserLoginPage(page)

        login_page.navigate()

        login_page.login(
            INVALID_EMAIL["email"],
            INVALID_EMAIL["password"]
        )

        expect(
            login_page.get_by_text(INVALID_EMAIL["expected_error"])
        ).to_be_visible(timeout=10000)

    @allure.title("Login failed with invalid email format")
    def test_invalid_email_format(
        self,
        page
    ):
        login_page = UserLoginPage(page)

        login_page.navigate()

        login_page.login(
           INVALID_EMAIL_FORMAT["email"],
           INVALID_EMAIL_FORMAT["password"]
        )

        expect(page).to_have_url(
            "http://localhost:3000/login"
        )