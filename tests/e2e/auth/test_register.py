import pytest
import allure

from copy import deepcopy

from playwright.sync_api import expect

from tests.pages.user.register_page import RegisterPage
from tests.utils.faker_factory import get_faker

from tests.data.register_data import (
    VALID_USER,
    REGISTER_DUPLICATE_EMAIL_CASE,
    REGISTER_VALIDATION_CASES
)


@allure.feature("Authentication")
@allure.story("Register")
class TestRegister:

    """
    E2E test suite cho Register feature.
    """

    # =====================================================
    # SUCCESS REGISTER
    # =====================================================

    @pytest.mark.smoke
    @allure.title("Đăng ký tài khoản mới thành công")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_success(
        self,
        page,
        base_url
    ):

        fake = get_faker()

        test_data = deepcopy(VALID_USER)

        test_data["email"] = fake.unique.email()

        rp = RegisterPage(page).navigate(base_url)

        rp.submit(
            full_name=test_data["full_name"],
            email=test_data["email"],
            password=test_data["password"],
            confirm_password=test_data["confirm_password"],
            wait_for_navigation=False
        )

        expect(page).to_have_url(
            f"{base_url}/login",
            timeout=10000
        )

    # =====================================================
    # DUPLICATE EMAIL
    # =====================================================

    @pytest.mark.regression
    @allure.title("Đăng ký thất bại do Email đã tồn tại")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_duplicate_email(
        self,
        page,
        base_url,
        existing_user
    ):

        test_data = deepcopy(
            REGISTER_DUPLICATE_EMAIL_CASE["data"]
        )

        test_data["email"] = existing_user["email"]

        rp = RegisterPage(page).navigate(base_url)

        rp.fill_registration_form(
            full_name=test_data["full_name"],
            email=test_data["email"],
            password=test_data["password"]
        )

        rp.click_register(wait_for_navigation=False)

        expect(
            page.get_by_text(
                REGISTER_DUPLICATE_EMAIL_CASE["expected_error"]
            )
        ).to_be_visible(timeout=10000)

    # =====================================================
    # VALIDATION TESTS
    # =====================================================

    @pytest.mark.regression
    @pytest.mark.parametrize(
        "case",
        REGISTER_VALIDATION_CASES,
        ids=[case["name"] for case in REGISTER_VALIDATION_CASES]
    )
    @allure.title("Register validation")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_validation(
        self,
        page,
        base_url,
        case
    ):

        fake = get_faker()

        # clone valid base data
        test_data = deepcopy(VALID_USER)

        # unique email mỗi lần test
        test_data["email"] = fake.unique.email()

        # override field invalid
        test_data.update(case["override"])

        rp = RegisterPage(page).navigate(base_url)

        rp.fill_registration_form(
            full_name=test_data["full_name"],
            email=test_data["email"],
            password=test_data["password"],
            confirm_password=test_data["confirm_password"]
        )

        rp.click_register(wait_for_navigation=False)

        expect(
            page.get_by_text(case["expected_error"])
        ).to_be_visible(timeout=10000)