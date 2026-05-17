import pytest
import allure
from pages.home_page import TranslatorPage

EMAIL    = "user1@example.com"
PASSWORD = "Test1234!"

# Language option values (match <option value="..."> in HTML)
LANG_EN = "5baa6399-bb68-4ea1-adbf-9da0fd83180f"
LANG_VI = "46a5f84f-57f9-4636-a565-c19905f0b07c"


@pytest.fixture(scope="module")
def translator(driver):
    """Login once, open translator page, reuse across all tests in module."""
    page = TranslatorPage(driver)
    page.login_and_open(EMAIL, PASSWORD)
    return page


# ======================================================================
# LAYOUT / RENDER
# ======================================================================
@allure.feature("Translator")
@allure.story("Layout")
class TestTranslatorLayout:

    def test_translator_box_is_displayed(self, translator):
        """Translator widget is visible after login."""
        box = translator.driver.find_element(*TranslatorPage.TRANSLATOR_BOX)
        assert box.is_displayed(), "translator__box should be visible"

    def test_input_textarea_is_present(self, translator):
        area = translator.driver.find_element(*TranslatorPage.INPUT_TEXTAREA)
        assert area.is_displayed()

    def test_output_textarea_is_present(self, translator):
        area = translator.driver.find_element(*TranslatorPage.OUTPUT_TEXTAREA)
        assert area.is_displayed()

    def test_translate_button_is_present(self, translator):
        btn = translator.driver.find_element(*TranslatorPage.TRANSLATE_BTN)
        assert btn.is_displayed()

    def test_clear_button_is_present(self, translator):
        btn = translator.driver.find_element(*TranslatorPage.CLEAR_BTN)
        assert btn.is_displayed()

    def test_copy_button_is_present(self, translator):
        btn = translator.driver.find_element(*TranslatorPage.COPY_BTN)
        assert btn.is_displayed()

    def test_swap_button_is_present(self, translator):
        btn = translator.driver.find_element(*TranslatorPage.SWAP_BTN)
        assert btn.is_displayed()

    def test_source_language_select_is_present(self, translator):
        sel = translator.driver.find_element(*TranslatorPage.SOURCE_SELECT)
        assert sel.is_displayed()

    def test_target_language_select_is_present(self, translator):
        sel = translator.driver.find_element(*TranslatorPage.TARGET_SELECT)
        assert sel.is_displayed()

    def test_char_counter_initial_value(self, translator):
        """Counter should show 0/2000 on fresh load."""
        translator.open()  # reload to reset state
        counter = translator.get_char_counter_text()
        assert "0" in counter and "2000" in counter, (
            f"Expected '0/2000 ký tự', got: {counter}"
        )


# ======================================================================
# LANGUAGE SELECTION
# ======================================================================
@allure.feature("Translator")
@allure.story("Language Selection")
class TestLanguageSelection:

    def test_default_source_language_is_english(self, translator):
        translator.open()
        assert translator.get_source_language() == LANG_EN

    def test_default_target_language_is_vietnamese(self, translator):
        translator.open()
        assert translator.get_target_language() == LANG_VI

    def test_can_change_source_language_to_vietnamese(self, translator):
        translator.open()
        translator.select_source_language(LANG_VI)
        assert translator.get_source_language() == LANG_VI

    def test_can_change_target_language_to_english(self, translator):
        translator.open()
        translator.select_target_language(LANG_EN)
        assert translator.get_target_language() == LANG_EN

    def test_swap_button_switches_languages(self, translator):
        translator.open()
        # Ensure known state: EN → VI
        translator.select_source_language(LANG_EN)
        translator.select_target_language(LANG_VI)

        translator.click_swap()

        assert translator.get_source_language() == LANG_VI, "Source should become VI after swap"
        assert translator.get_target_language() == LANG_EN, "Target should become EN after swap"


# ======================================================================
# INPUT BEHAVIOUR
# ======================================================================
@allure.feature("Translator")
@allure.story("Input")
class TestTranslatorInput:

    def test_type_text_appears_in_input(self, translator):
        translator.open()
        translator.type_text("Hello")
        assert translator.get_input_text() == "Hello"

    def test_char_counter_updates_on_typing(self, translator):
        translator.open()
        translator.type_text("Hello")
        counter = translator.get_char_counter_text()
        assert counter.startswith("5"), f"Expected counter to start with 5, got: {counter}"

    def test_clear_button_empties_input(self, translator):
        translator.open()
        translator.type_text("Some text to clear")
        translator.click_clear()
        assert translator.get_input_text() == "", "Input should be empty after clear"

    def test_clear_button_resets_char_counter(self, translator):
        translator.open()
        translator.type_text("Some text")
        translator.click_clear()
        counter = translator.get_char_counter_text()
        assert counter.startswith("0"), f"Counter should reset to 0, got: {counter}"

    def test_output_is_readonly(self, translator):
        translator.open()
        output = translator.driver.find_element(*TranslatorPage.OUTPUT_TEXTAREA)
        assert output.get_attribute("readonly") is not None, "Output textarea must be read-only"

    def test_copy_button_disabled_when_no_output(self, translator):
        translator.open()
        # No translation done yet — copy should be disabled
        assert not translator.is_copy_button_enabled(), (
            "Copy button should be disabled when output is empty"
        )

    def test_input_placeholder_text(self, translator):
        translator.open()
        area = translator.driver.find_element(*TranslatorPage.INPUT_TEXTAREA)
        placeholder = area.get_attribute("placeholder")
        assert placeholder, "Input area should have a placeholder"

    def test_output_placeholder_text(self, translator):
        translator.open()
        area = translator.driver.find_element(*TranslatorPage.OUTPUT_TEXTAREA)
        placeholder = area.get_attribute("placeholder")
        assert placeholder, "Output area should have a placeholder"


# ======================================================================
# TRANSLATION FLOW
# ======================================================================
@allure.feature("Translator")
@allure.story("Translation")
class TestTranslationFlow:

    def test_translate_english_to_vietnamese(self, translator):
        translator.open()
        translator.select_source_language(LANG_EN)
        translator.select_target_language(LANG_VI)
        translator.type_text("Hello")
        translator.click_translate()
        translator.wait_for_translation()
        output = translator.get_output_text()
        assert output.strip() != "", "Output should not be empty after translation"

    def test_translate_vietnamese_to_english(self, translator):
        translator.open()
        translator.select_source_language(LANG_VI)
        translator.select_target_language(LANG_EN)
        translator.type_text("Xin chào")
        translator.click_translate()
        translator.wait_for_translation()
        output = translator.get_output_text()
        assert output.strip() != "", "Output should not be empty after translation"

    def test_translate_button_text_is_correct(self, translator):
        translator.open()
        btn = translator.driver.find_element(*TranslatorPage.TRANSLATE_BTN)
        assert "Dịch" in btn.text, f"Button text should contain 'Dịch', got: {btn.text}"

    def test_output_cleared_when_input_cleared(self, translator):
        """After translating, clicking clear should reset input; output should also reset."""
        translator.open()
        translator.select_source_language(LANG_EN)
        translator.select_target_language(LANG_VI)
        translator.type_text("Good morning")
        translator.click_translate()
        translator.wait_for_translation()
        translator.click_clear()
        assert translator.get_input_text() == "", "Input should be empty after clear"

    def test_copy_button_enabled_after_translation(self, translator):
        translator.open()
        translator.select_source_language(LANG_EN)
        translator.select_target_language(LANG_VI)
        translator.type_text("Test")
        translator.click_translate()
        translator.wait_for_translation()
        assert translator.is_copy_button_enabled(), (
            "Copy button should be enabled after a translation result appears"
        )

    def test_translate_empty_input_does_not_crash(self, translator):
        """Clicking translate with no input should not throw an error."""
        translator.open()
        translator.click_translate()
        # Page should still be functional
        box = translator.driver.find_element(*TranslatorPage.TRANSLATOR_BOX)
        assert box.is_displayed()

    def test_translate_long_text(self, translator):
        long_text = "This is a test sentence. " * 40  # ~1000 chars
        translator.open()
        translator.select_source_language(LANG_EN)
        translator.select_target_language(LANG_VI)
        translator.type_text(long_text)
        translator.click_translate()
        translator.wait_for_translation(timeout=20)
        assert translator.get_output_text().strip() != ""

    def test_swap_then_translate(self, translator):
        """Swap languages then translate — should still return a result."""
        translator.open()
        translator.select_source_language(LANG_EN)
        translator.select_target_language(LANG_VI)
        translator.click_swap()  # now VI → EN
        translator.type_text("Xin chào thế giới")
        translator.click_translate()
        translator.wait_for_translation()
        assert translator.get_output_text().strip() != ""


# ======================================================================
# AUTH GUARD
# ======================================================================
@allure.feature("Translator")
@allure.story("Auth")
class TestTranslatorAuth:

    def test_unauthenticated_user_redirected_to_login(self, driver):
        """Accessing /home/text without login should redirect to /login."""
        # Clear cookies to simulate logged-out state
        driver.delete_all_cookies()
        driver.get(TranslatorPage.URL)
        assert "/login" in driver.current_url, (
            f"Expected redirect to /login, but URL is: {driver.current_url}"
        )