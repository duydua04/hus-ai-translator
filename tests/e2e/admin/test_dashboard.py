# tests/tests/test_dashboard.py

import pytest
from tests.pages.admin.dashboard_page import DashboardPage
from tests.data.dashboard_data import *


class TestDashboard:

    # ---------------- TIME FILTER ----------------

    def test_time_filter(self, page):
        dashboard = DashboardPage(page)
        dashboard.open()

        for option in TIME_FILTERS:
            dashboard.select_time_filter(option)
            dashboard.expect_metrics_updated()

    # ---------------- TOTAL FEEDBACK LOGIC ----------------

    def test_total_feedback_consistency(self, page):
        dashboard = DashboardPage(page)
        dashboard.open()

        stars = dashboard.get_star_values()
        total = dashboard.get_total_feedback()

        calculated_total = sum(int(s) for s in stars)
        assert calculated_total == total

    # ---------------- AVG SCORE CONSISTENCY ----------------

    def test_avg_score_consistency(self, page):
        dashboard = DashboardPage(page)
        dashboard.open()

        avg_ui = dashboard.get_avg_score()

        # giả lập logic check (thường backend API verify sẽ chuẩn hơn)
        assert avg_ui >= 0 and avg_ui <= 5

    # ---------------- EMPTY DATA ----------------

    def test_empty_data_state(self, page):
        dashboard = DashboardPage(page)
        dashboard.open()

        dashboard.select_time_filter(SAMPLE_MONTH_EMPTY)

        dashboard.expect_no_data()

    # ---------------- SATISFACTION RATE ----------------

    def test_satisfaction_rate_logic(self, page):
        dashboard = DashboardPage(page)
        dashboard.open()

        rate = dashboard.get_satisfaction_rate()

        assert "%" in rate

    # ---------------- REALTIME UPDATE ----------------

    def test_realtime_feedback_update(self, page):
        dashboard = DashboardPage(page)
        dashboard.open()

        before = dashboard.get_total_feedback()

        dashboard.refresh()

        after = dashboard.get_total_feedback()

        assert after >= before

    # ---------------- TREND INDICATOR ----------------

    def test_growth_indicator(self, page):
        dashboard = DashboardPage(page)
        dashboard.open()

        indicator = page.locator(".growth-indicator").text_content()

        assert "↑" in indicator or "↓" in indicator

    # ---------------- CATEGORY FILTER ----------------

    def test_category_filter(self, page):
        dashboard = DashboardPage(page)
        dashboard.open()

        dashboard.select_category(FEEDBACK_CATEGORY)

        expect(page.locator("text=Lỗi kỹ thuật")).to_be_visible()