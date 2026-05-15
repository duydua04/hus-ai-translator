# tests/pages/feedback_page.py

from playwright.sync_api import expect


class FeedbackPage:
    def __init__(self, page):
        self.page = page

        # filters
        self.status_tabs = page.locator(".status-tab")
        self.language_dropdown = page.locator("#language-filter")
        self.rating_dropdown = page.locator("#rating-filter")
        self.type_dropdown = page.locator("#type-filter")

        # search
        self.search_input = page.locator("input[name='search']")

        # table
        self.rows = page.locator("table tbody tr")

        # actions
        self.export_csv_btn = page.locator("text=Xuất CSV")

        # detail
        self.view_btn = page.locator("text=Xem")

    # ---------------- ACTIONS ----------------

    def open(self):
        self.page.goto("/admin/feedback")

    def click_tab(self, tab_name: str):
        self.page.locator(f"text={tab_name}").click()

    def filter_language(self, lang: str):
        self.language_dropdown.click()
        self.page.locator(f"text={lang}").click()

    def filter_rating(self, option: str):
        self.rating_dropdown.click()
        self.page.locator(f"text={option}").click()

    def filter_type(self, option: str):
        self.type_dropdown.click()
        self.page.locator(f"text={option}").click()

    def search(self, keyword: str):
        self.search_input.fill(keyword)
        self.search_input.press("Enter")

    def export_csv(self):
        with self.page.expect_download() as download_info:
            self.export_csv_btn.click()
        return download_info.value

    def open_detail(self):
        self.rows.first.click()
        self.view_btn.click()

    # ---------------- ASSERTIONS ----------------

    def expect_rows_exist(self):
        expect(self.rows.first).to_be_visible()

    def expect_empty_state(self):
        expect(self.page.locator("text=Không tìm thấy")).to_be_visible()

    def expect_tab_active(self, tab_name: str):
        expect(self.page.locator(f"text={tab_name}")).to_have_class(lambda c: "active" in c)

    def get_first_row_time(self):
        return self.rows.first.text_content()