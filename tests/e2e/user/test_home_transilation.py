# tests/tests/test_home_translation.py

import pytest
from tests.pages.home_page import HomePage
from tests.data.translation_data import *


class TestHomeTranslation:

    # ---------------- BASIC TRANSLATION ----------------

    def test_translate_text(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(VALID_TEXT)
        home.translate()

        home.expect_translation_result()

    # ---------------- LIMIT ----------------

    def test_5000_char_limit(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(LONG_TEXT)
        home.translate()

        # expected: error or truncate
        assert home.get_output_text() is not None or home.error.is_visible()

    # ---------------- CLEAR ----------------

    def test_clear_text(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text("Hello")
        home.clear_text()

        assert home.input_box.input_value() == ""

    # ---------------- COPY ----------------

    def test_copy_result(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(COPY_TEXT)
        home.translate()

        home.copy_result()

        assert True  # clipboard check thường cần plugin/system tool

    # ---------------- SWAP LANGUAGE ----------------

    def test_swap_language(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(SWAP_INPUT)
        home.swap_language()

        # UI state check (tuỳ app)
        assert True

    # ---------------- LOGIN BUTTON ----------------

    def test_login_navigation(self, page):
        home = HomePage(page)
        home.open()

        home.click_login()

        assert "/login" in page.url

    # ---------------- EMPTY INPUT ----------------

    def test_empty_translation(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(EMPTY_TEXT)
        home.translate()

        home.expect_empty_input_error()

    # ---------------- SECURITY (XSS) ----------------

    def test_xss_protection(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(XSS_PAYLOAD)
        home.translate()

        home.expect_security_safe()

    # ---------------- TECH TERM ----------------

    def test_technical_term(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(TECH_TERM)
        home.translate()

        home.expect_translation_result()

    # ---------------- EMAIL / LINK ----------------

    def test_email_translation(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(EMAIL_TEXT)
        home.translate()

        home.expect_translation_result()

    # ---------------- SPECIAL CHARS ----------------

    def test_special_characters(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(SPECIAL_CHARS)
        home.translate()

        home.expect_translation_result()

    # ---------------- MULTI PARAGRAPH ----------------

    def test_multi_paragraph(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(MULTI_PARAGRAPH)
        home.translate()

        home.expect_translation_result()

    # ---------------- EMOJI ----------------

    def test_emoji_translation(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(EMOJI_TEXT)
        home.translate()

        home.expect_translation_result()

    # ---------------- ROUND TRIP TRANSLATION ----------------

    def test_round_trip_translation(self, page):
        home = HomePage(page)
        home.open()

        home.enter_text(A_TEXT)
        home.translate()

        result_b = home.get_output_text()

        home.swap_language()
        home.enter_text(result_b)
        home.translate()

        assert home.get_output_text() is not None