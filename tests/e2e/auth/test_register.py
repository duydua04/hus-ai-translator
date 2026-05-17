import pytest
import allure

from playwright.sync_api import expect

from utils.faker_factory import UserFactory
from data.register_data import (
    EXISTING_USER,
    INVALID_PASSWORDS,
    INVALID_EMAILS,
    PASSWORD_MISMATCH,
    REQUIRED_FIELDS,
)


def new_user() -> dict:
    return UserFactory.valid_user()


@allure.feature("Xác thực người dùng")
@allure.story("Đăng ký tài khoản")
@pytest.mark.auth
class TestRegister:

    # ── TC-REG-01 ─────────────────────────────────────────────────────────────
    @allure.title("TC-REG-01: Đăng ký thành công với dữ liệu hợp lệ")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_register_success(self, register_page):
        user = new_user()

        with allure.step("Điền form đăng ký hợp lệ và submit"):
            register_page.register(
                full_name=user["full_name"],
                email=user["email"],
                password=user["password"],
                confirm_password=user["confirm_password"],
            )

        with allure.step("Kiểm tra chuyển hướng sau khi đăng ký thành công"):
            assert register_page.is_redirected_after_register(), (
                "Sau đăng ký thành công phải chuyển về trang login hoặc home"
            )

    # ── TC-REG-02 ─────────────────────────────────────────────────────────────
    @allure.title("TC-REG-02: Đăng ký với email đã tồn tại")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_register_duplicate_email(self, register_page):
        user = new_user()

        with allure.step("Đăng ký với email đã tồn tại trong hệ thống"):
            register_page.register(
                full_name=user["full_name"],
                email=EXISTING_USER["email"],
                password=user["password"],
                confirm_password=user["confirm_password"],
            )

        with allure.step(
            f"Kiểm tra thông báo lỗi: "
            f"'{EXISTING_USER['expected_error']}'"
        ):
            expect(
                register_page.page.get_by_text(
                    EXISTING_USER["expected_error"]
                )
            ).to_be_visible(timeout=5000)

        with allure.step("Xác nhận vẫn ở trang đăng ký"):
            assert register_page.is_on_register_page()

    # ── TC-REG-03 ─────────────────────────────────────────────────────────────
    @allure.title("TC-REG-03: Confirm password không khớp với password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_register_password_mismatch(self, register_page):
        user = new_user()

        with allure.step("Nhập confirm password không khớp"):
            register_page.register(
                full_name=user["full_name"],
                email=user["email"],
                password=PASSWORD_MISMATCH["password"],
                confirm_password=PASSWORD_MISMATCH["confirm_password"],
            )

        with allure.step(
            f"Kiểm tra thông báo lỗi: "
            f"'{PASSWORD_MISMATCH['expected_error']}'"
        ):
            expect(
                register_page.page.get_by_text(
                    PASSWORD_MISMATCH["expected_error"]
                )
            ).to_be_visible(timeout=5000)

    # ── TC-REG-04 ─────────────────────────────────────────────────────────────
    @allure.title("TC-REG-04: Mật khẩu không đủ mạnh [{case[id]}]")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "case",
        INVALID_PASSWORDS,
        ids=[c["id"] for c in INVALID_PASSWORDS]
    )
    def test_register_weak_password(self, register_page, case):
        user = new_user()

        with allure.step(f"Trường hợp: {case['description']}"):
            register_page.register(
                full_name=user["full_name"],
                email=user["email"],
                password=case["password"],
                confirm_password=case["confirm_password"],
            )

        with allure.step(
            f"Kiểm tra thông báo lỗi: "
            f"'{case['expected_error']}'"
        ):
            expect(
                register_page.page.get_by_text(
                    case["expected_error"]
                )
            ).to_be_visible(timeout=5000)

    # ── TC-REG-05 ─────────────────────────────────────────────────────────────
    @allure.title("TC-REG-05: Email sai định dạng [{case[id]}]")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "case",
        INVALID_EMAILS,
        ids=[c["id"] for c in INVALID_EMAILS]
    )
    def test_register_invalid_email(self, register_page, case):
        user = new_user()

        with allure.step(f"Nhập email không hợp lệ: '{case['email']}'"):
            register_page.register(
                full_name=user["full_name"],
                email=case["email"],
                password=user["password"],
                confirm_password=user["confirm_password"],
            )

        with allure.step(
            f"Kiểm tra thông báo lỗi: "
            f"'{case['expected_error']}'"
        ):
            expect(
                register_page.page.get_by_text(
                    case["expected_error"]
                )
            ).to_be_visible(timeout=5000)

    # ── TC-REG-06 ─────────────────────────────────────────────────────────────
    @allure.title("TC-REG-06: Bỏ trống trường bắt buộc [{case[field]}]")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "case",
        REQUIRED_FIELDS,
        ids=[c["field"] for c in REQUIRED_FIELDS]
    )
    def test_register_required_fields(self, register_page, case):
        user = new_user()

        with allure.step("Điền đầy đủ form trước"):
            register_page.fill_form(
                full_name=user["full_name"],
                email=user["email"],
                password=user["password"],
                confirm_password=user["confirm_password"],
            )

        with allure.step(
            f"Xóa trắng field '{case['field']}' rồi submit"
        ):
            register_page.clear_field(
                register_page.field_selectors[case["field"]]
            )
            register_page.click_submit()

        with allure.step(
            f"Kiểm tra thông báo lỗi: "
            f"'{case['expected_error']}'"
        ):
            expect(
                register_page.page.get_by_text(
                    case["expected_error"]
                )
            ).to_be_visible(timeout=5000)

    # ── TC-REG-07 ─────────────────────────────────────────────────────────────
    @allure.title(
        "TC-REG-07: Link 'Đã có tài khoản?' chuyển sang trang Đăng nhập"
    )
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.smoke
    def test_register_link_to_login(self, register_page):

        with allure.step("Nhấn link chuyển sang trang đăng nhập"):
            register_page.click_login_link()

        with allure.step("Xác nhận URL chứa '/login'"):
            register_page.page.wait_for_url(
                "**/login",
                timeout=5000
            )
            assert "/login" in register_page.page.url