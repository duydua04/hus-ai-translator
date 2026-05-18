"""
pages/home_page.py
──────────────────
Page Object cho trang dịch văn bản: http://localhost:3000/home/text
Dùng Playwright (sync API) – nhất quán với conftest.py.
"""

from __future__ import annotations

from playwright.sync_api import Page, expect


class HomePage:
    # ── URLs ─────────────────────────────────────────────────────────────────
    PATH = "/home/text"

    # ── Locators ─────────────────────────────────────────────────────────────
    # Bộ chứa tổng thể
    TRANSLATOR_BOX     = ".translator__box"

    # Ngôn ngữ
    SOURCE_SELECT      = ".translator__tabs .translator__select:first-of-type"
    TARGET_SELECT      = ".translator__tabs .translator__select:last-of-type"
    SWAP_BTN           = ".translator__swap-btn"

    # Nhập / xuất
    INPUT_TEXTAREA     = ".translator__input"
    OUTPUT_TEXTAREA    = ".translator__output"
    CHAR_COUNTER       = ".translator__selector-left"

    # Nút hành động
    TRANSLATE_BTN      = ".translator__action .btn--primary"
    CLEAR_BTN          = ".action-btn[title='Xóa']"
    COPY_BTN           = ".action-btn[title='Sao chép']"

    def __init__(self, page: Page, base_url: str) -> None:
        self.page     = page
        self.base_url = base_url.rstrip("/")

    # ── Điều hướng ───────────────────────────────────────────────────────────
    def navigate(self) -> None:
        self.page.goto(f"{self.base_url}{self.PATH}")
        self.page.wait_for_selector(self.TRANSLATOR_BOX)

    # ── Ngôn ngữ ─────────────────────────────────────────────────────────────
    def get_source_language(self) -> str:
        return self.page.locator(self.SOURCE_SELECT).input_value()

    def get_target_language(self) -> str:
        return self.page.locator(self.TARGET_SELECT).input_value()

    def select_source_language(self, value: str) -> None:
        self.page.locator(self.SOURCE_SELECT).select_option(value=value)

    def select_target_language(self, value: str) -> None:
        self.page.locator(self.TARGET_SELECT).select_option(value=value)

    def click_swap(self) -> None:
        self.page.locator(self.SWAP_BTN).click()

    # ── Nhập liệu ────────────────────────────────────────────────────────────
    def type_text(self, text: str) -> None:
        area = self.page.locator(self.INPUT_TEXTAREA)
        area.clear()
        area.fill(text)

    def get_input_text(self) -> str:
        return self.page.locator(self.INPUT_TEXTAREA).input_value()

    def get_output_text(self) -> str:
        return self.page.locator(self.OUTPUT_TEXTAREA).input_value()

    def get_char_counter_text(self) -> str:
        return self.page.locator(self.CHAR_COUNTER).inner_text()

    # ── Hành động ────────────────────────────────────────────────────────────
    def click_translate(self) -> None:
        self.page.locator(self.TRANSLATE_BTN).click()

    def click_clear(self) -> None:
        self.page.locator(self.CLEAR_BTN).click()

    def click_copy(self) -> None:
        self.page.locator(self.COPY_BTN).click()

    def is_copy_button_enabled(self) -> bool:
        return self.page.locator(self.COPY_BTN).is_enabled()

    def is_translate_button_enabled(self) -> bool:
        return self.page.locator(self.TRANSLATE_BTN).is_enabled()

    # ── Chờ kết quả dịch ─────────────────────────────────────────────────────
    def wait_for_translation(self, timeout: int = 15_000) -> None:
        """Chờ output có nội dung (timeout tính bằng ms theo Playwright)."""
        self.page.wait_for_function(
            """selector => {
                const el = document.querySelector(selector);
                return el && el.value && el.value.trim() !== '';
            }""",
            arg=self.OUTPUT_TEXTAREA,
            timeout=timeout,
        )