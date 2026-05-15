# tests/pages/dashboard_page.py

from playwright.sync_api import expect


class DashboardPage:
    def __init__(self, page):
        self.page = page

        # filters
        self.time_filter = page.locator("#time-filter")
        self.category_filter = page.locator(".category-filter")

        # metrics
        self.total_feedback = page.locator("#total-feedback")
        self.avg_score = page.locator("#avg-score")
        self.satisfaction_rate = page.locator("#satisfaction-rate")

        # charts
        self.star_items = page.locator(".star-item")  # 5★ -> 1★
        self.pie_chart = page.locator(".pie-chart")

    # ---------------- ACTIONS ----------------

    def open(self):
        self.page.goto("/admin/dashboard")

    def select_time_filter(self, option: str):
        self.time_filter.click()
        self.page.locator(f"text={option}").click()

    def select_category(self, category: str):
        self.category_filter.click()
        self.page.locator(f"text={category}").click()

    def refresh(self):
        self.page.reload()

    # ---------------- GET DATA ----------------

    def get_star_values(self):
        return self.star_items.all_text_contents()

    def get_total_feedback(self):
        return int(self.total_feedback.text_content())

    def get_avg_score(self):
        return float(self.avg_score.text_content())

    def get_satisfaction_rate(self):
        return self.satisfaction_rate.text_content()

    # ---------------- ASSERTIONS ----------------

    def expect_no_data(self):
        expect(self.page.locator("text=No data")).to_be_visible()

    def expect_metrics_updated(self):
        expect(self.total_feedback).not_to_have_text("0")