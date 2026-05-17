# tests/tests/test_feedback.py

import pytest
from tests.pages.admin.feedback_page import FeedbackPage
from tests.data.feedback_data import *


class TestFeedback:

    # ---------------- EXPORT CSV ----------------

    def test_export_csv(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        file = feedback.export_csv()
        assert file.name.endswith(".csv")

    def test_export_csv_after_filter(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        feedback.click_tab("Cần xử lý")
        file = feedback.export_csv()

        assert file.name.endswith(".csv")

    # ---------------- STATUS TAB ----------------

    def test_status_tabs(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        for tab in STATUS_TABS:
            feedback.click_tab(tab)
            feedback.expect_rows_exist()
            feedback.expect_tab_active(tab)

    # ---------------- LANGUAGE FILTER ----------------

    def test_language_filter(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        feedback.filter_language(LANGUAGE)
        feedback.expect_rows_exist()

    # ---------------- SEARCH ----------------

    def test_search_feedback(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        feedback.search(SEARCH_KEYWORD)
        feedback.expect_rows_exist()

    def test_search_not_found(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        feedback.search(INVALID_SEARCH)
        feedback.expect_empty_state()

    def test_search_by_user(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        feedback.search(USER_NAME)
        feedback.expect_rows_exist()

    # ---------------- RATING FILTER ----------------

    def test_rating_filter(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        for option in RATING_OPTIONS:
            feedback.filter_rating(option)
            feedback.expect_rows_exist()

    # ---------------- TYPE FILTER ----------------

    def test_type_filter(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        for option in TYPE_OPTIONS:
            feedback.filter_type(option)
            feedback.expect_rows_exist()

    # ---------------- DETAIL VIEW ----------------

    def test_view_feedback_detail(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        feedback.open_detail()
        feedback.expect_rows_exist()

    # ---------------- DEFAULT SORT ----------------

    def test_default_sort(self, page):
        feedback = FeedbackPage(page)
        feedback.open()

        first_row = feedback.get_first_row_time()
        assert first_row is not None