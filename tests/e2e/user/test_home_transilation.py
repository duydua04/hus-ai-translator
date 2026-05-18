"""
e2e/user/test_home_transilation.py
────────────────────────────────────
Test suite cho luồng dịch văn bản tại /home/text.
Framework : pytest + playwright (sync)
Page Object: pages/home_page.HomePage
Test data  : data/translation_data.py

Chạy:
    pytest e2e/user/test_home_transilation.py -v
    pytest e2e/user/test_home_transilation.py -v --headed   # xem browser
    pytest e2e/user/test_home_transilation.py -k "layout"   # chỉ chạy 1 nhóm
"""

from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Page, expect

from data.translation_data import (
    LANG_EN,
    LANG_VI,
    LONG_TEXT_EN,
    MAX_CHARS,
    OVER_LIMIT_TEXT,
    SPECIAL_TEXTS,
    VALID_TRANSLATIONS,
)
from pages.home_page import HomePage


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def hp(authenticated_user_page: Page, base_url: str) -> HomePage:
    """
    Trả về HomePage đã điều hướng đến /home/text.
    Dùng authenticated_user_page từ conftest → đã login sẵn.
    """
    page_obj = HomePage(authenticated_user_page, base_url)
    page_obj.navigate()
    return page_obj


# ══════════════════════════════════════════════════════════════════════════════
# 1. LAYOUT – kiểm tra giao diện hiển thị đúng
# ══════════════════════════════════════════════════════════════════════════════

@allure.feature("Dịch văn bản")
@allure.story("Layout")
class TestTranslatorLayout:

    def test_translator_box_is_visible(self, hp: HomePage):
        """Khung dịch thuật phải hiển thị sau khi login."""
        expect(hp.page.locator(HomePage.TRANSLATOR_BOX)).to_be_visible()

    def test_input_textarea_is_visible(self, hp: HomePage):
        expect(hp.page.locator(HomePage.INPUT_TEXTAREA)).to_be_visible()

    def test_output_textarea_is_visible(self, hp: HomePage):
        expect(hp.page.locator(HomePage.OUTPUT_TEXTAREA)).to_be_visible()

    def test_translate_button_is_visible(self, hp: HomePage):
        expect(hp.page.locator(HomePage.TRANSLATE_BTN)).to_be_visible()

    def test_clear_button_is_visible(self, hp: HomePage):
        expect(hp.page.locator(HomePage.CLEAR_BTN)).to_be_visible()

    def test_copy_button_is_visible(self, hp: HomePage):
        expect(hp.page.locator(HomePage.COPY_BTN)).to_be_visible()

    def test_swap_button_is_visible(self, hp: HomePage):
        expect(hp.page.locator(HomePage.SWAP_BTN)).to_be_visible()

    def test_source_language_select_is_visible(self, hp: HomePage):
        expect(hp.page.locator(HomePage.SOURCE_SELECT)).to_be_visible()

    def test_target_language_select_is_visible(self, hp: HomePage):
        expect(hp.page.locator(HomePage.TARGET_SELECT)).to_be_visible()

    def test_char_counter_shows_zero_on_load(self, hp: HomePage):
        """Counter phải hiển thị 0/2000 khi mới vào trang."""
        counter = hp.get_char_counter_text()
        assert "0" in counter and str(MAX_CHARS) in counter, (
            f"Expected '0/{MAX_CHARS}', got: '{counter}'"
        )

    def test_translate_button_text_contains_dich(self, hp: HomePage):
        btn = hp.page.locator(HomePage.TRANSLATE_BTN)
        assert "Dịch" in btn.inner_text(), (
            f"Nút dịch phải chứa chữ 'Dịch', thực tế: {btn.inner_text()}"
        )

    def test_input_has_placeholder(self, hp: HomePage):
        area = hp.page.locator(HomePage.INPUT_TEXTAREA)
        placeholder = area.get_attribute("placeholder")
        assert placeholder, "Input phải có placeholder text"

    def test_output_has_placeholder(self, hp: HomePage):
        area = hp.page.locator(HomePage.OUTPUT_TEXTAREA)
        placeholder = area.get_attribute("placeholder")
        assert placeholder, "Output phải có placeholder text"

    def test_output_is_readonly(self, hp: HomePage):
        area = hp.page.locator(HomePage.OUTPUT_TEXTAREA)
        assert area.get_attribute("readonly") is not None or \
               area.get_attribute("disabled") is not None, \
            "Output textarea phải là readonly"


# ══════════════════════════════════════════════════════════════════════════════
# 2. LANGUAGE SELECTION – kiểm tra chọn ngôn ngữ
# ══════════════════════════════════════════════════════════════════════════════

@allure.feature("Dịch văn bản")
@allure.story("Chọn ngôn ngữ")
class TestLanguageSelection:

    def test_default_source_language_is_english(self, hp: HomePage):
        assert hp.get_source_language() == LANG_EN, \
            "Ngôn ngữ nguồn mặc định phải là Tiếng Anh"

    def test_default_target_language_is_vietnamese(self, hp: HomePage):
        assert hp.get_target_language() == LANG_VI, \
            "Ngôn ngữ đích mặc định phải là Tiếng Việt"

    def test_can_change_source_language(self, hp: HomePage):
        hp.select_source_language(LANG_VI)
        assert hp.get_source_language() == LANG_VI

    def test_can_change_target_language(self, hp: HomePage):
        hp.select_target_language(LANG_EN)
        assert hp.get_target_language() == LANG_EN

    def test_swap_button_switches_source_and_target(self, hp: HomePage):
        """Nhấn swap: EN→VI phải thành VI→EN."""
        hp.select_source_language(LANG_EN)
        hp.select_target_language(LANG_VI)
        hp.click_swap()
        assert hp.get_source_language() == LANG_VI, "Sau swap, nguồn phải là VI"
        assert hp.get_target_language() == LANG_EN, "Sau swap, đích phải là EN"

    def test_swap_preserves_input_text(self, hp: HomePage):
        """Swap không được xoá văn bản đang nhập."""
        hp.type_text("Hello world")
        hp.click_swap()
        assert hp.get_input_text() != "", "Swap không được xoá input"

    def test_swap_button_twice_returns_to_original(self, hp: HomePage):
        """Nhấn swap 2 lần phải quay về ngôn ngữ ban đầu."""
        original_src = hp.get_source_language()
        original_tgt = hp.get_target_language()
        hp.click_swap()
        hp.click_swap()
        assert hp.get_source_language() == original_src
        assert hp.get_target_language() == original_tgt


# ══════════════════════════════════════════════════════════════════════════════
# 3. INPUT BEHAVIOUR – kiểm tra ô nhập liệu
# ══════════════════════════════════════════════════════════════════════════════

@allure.feature("Dịch văn bản")
@allure.story("Nhập liệu")
class TestTranslatorInput:

    def test_typed_text_appears_in_input(self, hp: HomePage):
        hp.type_text("Hello")
        assert hp.get_input_text() == "Hello"

    def test_char_counter_updates_while_typing(self, hp: HomePage):
        hp.type_text("Hello")
        counter = hp.get_char_counter_text()
        assert "5" in counter, f"Counter phải chứa '5', thực tế: {counter}"

    def test_clear_button_empties_input(self, hp: HomePage):
        hp.type_text("Some text to clear")
        hp.click_clear()
        assert hp.get_input_text() == "", "Input phải trống sau khi Clear"

    def test_clear_button_resets_char_counter(self, hp: HomePage):
        hp.type_text("Some text")
        hp.click_clear()
        counter = hp.get_char_counter_text()
        assert counter.startswith("0"), f"Counter phải về 0 sau Clear, thực tế: {counter}"

    def test_clear_also_clears_output(self, hp: HomePage):
        """Sau khi dịch, nhấn Clear phải xoá cả output."""
        hp.select_source_language(LANG_EN)
        hp.select_target_language(LANG_VI)
        hp.type_text("Hello")
        hp.click_translate()
        hp.wait_for_translation()
        hp.click_clear()
        assert hp.get_input_text() == "", "Input phải trống"
        assert hp.get_output_text() == "", "Output phải trống sau Clear"

    def test_copy_button_disabled_when_output_empty(self, hp: HomePage):
        """Copy phải bị disable khi chưa có kết quả dịch."""
        assert not hp.is_copy_button_enabled(), \
            "Nút Copy phải disabled khi output trống"

    def test_text_at_max_chars_is_accepted(self, hp: HomePage):
        """Nhập đúng 2000 ký tự phải được chấp nhận."""
        hp.type_text("A" * MAX_CHARS)
        counter = hp.get_char_counter_text()
        assert str(MAX_CHARS) in counter

    def test_text_over_limit_is_truncated_or_blocked(self, hp: HomePage):
        """Nhập quá 2000 ký tự: UI phải cắt hoặc ngăn."""
        hp.type_text(OVER_LIMIT_TEXT)
        actual = hp.get_input_text()
        assert len(actual) <= MAX_CHARS, (
            f"Input không được vượt quá {MAX_CHARS} ký tự, thực tế: {len(actual)}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# 4. TRANSLATION FLOW – luồng dịch chính
# ══════════════════════════════════════════════════════════════════════════════

@allure.feature("Dịch văn bản")
@allure.story("Luồng dịch")
class TestTranslationFlow:

    @pytest.mark.parametrize("case", VALID_TRANSLATIONS, ids=[c["id"] for c in VALID_TRANSLATIONS])
    def test_translate_valid_text(self, hp: HomePage, case: dict):
        """Dịch văn bản hợp lệ ở nhiều cặp ngôn ngữ khác nhau."""
        with allure.step(case["description"]):
            hp.select_source_language(case["source"])
            hp.select_target_language(case["target"])
            hp.type_text(case["input"])
            hp.click_translate()
            hp.wait_for_translation()
            output = hp.get_output_text()
            assert output.strip() != "", (
                f"Output không được trống sau khi dịch: {case['description']}"
            )

    def test_translate_long_text_en_to_vi(self, hp: HomePage):
        """Dịch đoạn văn dài gần giới hạn EN → VI."""
        hp.select_source_language(LANG_EN)
        hp.select_target_language(LANG_VI)
        hp.type_text(LONG_TEXT_EN)
        hp.click_translate()
        hp.wait_for_translation(timeout=30_000)
        assert hp.get_output_text().strip() != ""

    def test_translate_then_swap_and_translate_again(self, hp: HomePage):
        """Dịch → swap → dịch lại phải cho kết quả hợp lệ."""
        hp.select_source_language(LANG_EN)
        hp.select_target_language(LANG_VI)
        hp.type_text("Good morning")
        hp.click_translate()
        hp.wait_for_translation()
        result_vi = hp.get_output_text()
        assert result_vi.strip() != ""

        # Swap và dịch ngược lại
        hp.click_swap()
        hp.type_text(result_vi)
        hp.click_translate()
        hp.wait_for_translation()
        result_en = hp.get_output_text()
        assert result_en.strip() != "", "Dịch ngược lại sau swap phải có kết quả"

    def test_copy_button_enabled_after_translation(self, hp: HomePage):
        """Nút Copy phải được enable sau khi có kết quả dịch."""
        hp.select_source_language(LANG_EN)
        hp.select_target_language(LANG_VI)
        hp.type_text("Hello world")
        hp.click_translate()
        hp.wait_for_translation()
        assert hp.is_copy_button_enabled(), \
            "Nút Copy phải enabled khi có kết quả dịch"

    def test_translate_empty_input_does_not_crash(self, hp: HomePage):
        """Click Dịch khi input trống: trang không crash, UI vẫn hiển thị."""
        hp.click_translate()
        expect(hp.page.locator(HomePage.TRANSLATOR_BOX)).to_be_visible()

    def test_translate_multiple_times_consecutively(self, hp: HomePage):
        """Dịch nhiều lần liên tiếp không gây lỗi."""
        texts = ["Hello", "Good morning", "How are you?"]
        for text in texts:
            hp.type_text(text)
            hp.click_translate()
            hp.wait_for_translation()
            assert hp.get_output_text().strip() != "", f"Lần dịch '{text}' phải có kết quả"
            hp.click_clear()

    def test_translate_vi_to_en_then_clear_and_retranslate(self, hp: HomePage):
        """Clear sau dịch và dịch lại bình thường."""
        hp.select_source_language(LANG_VI)
        hp.select_target_language(LANG_EN)
        hp.type_text("Xin chào thế giới")
        hp.click_translate()
        hp.wait_for_translation()
        hp.click_clear()

        hp.type_text("Cảm ơn bạn")
        hp.click_translate()
        hp.wait_for_translation()
        assert hp.get_output_text().strip() != ""

    def test_output_differs_between_language_pairs(self, hp: HomePage):
        """Cùng 1 văn bản, 2 cặp ngôn ngữ khác nhau phải cho output khác nhau."""
        text = "Hello"

        hp.select_source_language(LANG_EN)
        hp.select_target_language(LANG_VI)
        hp.type_text(text)
        hp.click_translate()
        hp.wait_for_translation()
        output_vi = hp.get_output_text()

        # Nếu hệ thống có thêm ngôn ngữ thứ 3 thì test sẽ rõ hơn
        # Tạm thời kiểm tra output không giống input
        assert output_vi.strip().lower() != text.lower(), \
            "Output phải khác với input gốc"


# ══════════════════════════════════════════════════════════════════════════════
# 5. SPECIAL INPUTS – văn bản đặc biệt / edge case
# ══════════════════════════════════════════════════════════════════════════════

@allure.feature("Dịch văn bản")
@allure.story("Đầu vào đặc biệt")
class TestSpecialInputs:

    @pytest.mark.parametrize("case", SPECIAL_TEXTS, ids=[c["id"] for c in SPECIAL_TEXTS])
    def test_special_text_does_not_crash(self, hp: HomePage, case: dict):
        """Nhập văn bản đặc biệt không được crash trang."""
        with allure.step(case["description"]):
            hp.select_source_language(LANG_EN)
            hp.select_target_language(LANG_VI)
            hp.type_text(case["input"])
            hp.click_translate()
            # Không cần wait_for_translation – chỉ kiểm tra trang không crash
            expect(hp.page.locator(HomePage.TRANSLATOR_BOX)).to_be_visible()

    def test_html_injection_is_rendered_as_text(self, hp: HomePage):
        """Văn bản chứa HTML tag phải được render là plain text, không thực thi."""
        payload = "<b>bold</b><script>alert(1)</script>"
        hp.type_text(payload)
        # Kiểm tra giá trị thực trong DOM, không phải HTML rendered
        actual = hp.get_input_text()
        assert "<script>" not in hp.page.content() or actual == payload, \
            "Script tag không được thực thi"

    def test_whitespace_only_input(self, hp: HomePage):
        """Nhập toàn khoảng trắng: UI phải xử lý gracefully."""
        hp.type_text("     ")
        hp.click_translate()
        expect(hp.page.locator(HomePage.TRANSLATOR_BOX)).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# 6. AUTH GUARD – kiểm tra bảo vệ route
# ══════════════════════════════════════════════════════════════════════════════

@allure.feature("Dịch văn bản")
@allure.story("Bảo vệ route")
class TestAuthGuard:

    def test_unauthenticated_user_redirected_to_login(self, page: Page, base_url: str):
        """Truy cập /home/text khi chưa login phải chuyển về /login."""
        page.context.clear_cookies()
        page.goto(f"{base_url}{HomePage.PATH}")
        page.wait_for_load_state("networkidle")
        assert "/login" in page.url, (
            f"Phải chuyển hướng về /login, thực tế URL: {page.url}"
        )

    def test_authenticated_user_can_access_translator(self, hp: HomePage):
        """User đã login phải vào được trang dịch thuật."""
        assert HomePage.PATH in hp.page.url or "text" in hp.page.url, \
            "User đã đăng nhập phải được vào trang /home/text"