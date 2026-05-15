import pytest
import allure

from playwright.sync_api import expect

from tests.pages.admin.admin_login_page import AdminLoginPage

from tests.data.admin_login_data import (
    VALID_ADMIN_LOGIN,
    INVALID_ADMIN_PASSWORD,
    LOCKED_ADMIN_ACCOUNT
)


@allure.feature("Authentication")
@allure.story("Admin Login")
class TestAdminLogin:

    @allure.title("Login successfully with valid admin")
    def test_valid_admin_login(self, page):

        login_page = AdminLoginPage(page)

        login_page.navigate()

        login_page.login(
            VALID_ADMIN_LOGIN["email"],
            VALID_ADMIN_LOGIN["password"]
        )

        expect(page).to_have_url(
            "http://localhost:3001/dash"
        )

    @pytest.mark.parametrize(
        "test_data",
        [
            INVALID_ADMIN_PASSWORD,
            LOCKED_ADMIN_ACCOUNT
        ]
    )
    def test_invalid_admin_login(
        self,
        page,
        test_data
    ):
        login_page = AdminLoginPage(page)

        login_page.navigate()

        login_page.login(
            test_data["email"],
            test_data["password"]
        )

        expect(
            login_page.error_message
        ).to_be_visible()