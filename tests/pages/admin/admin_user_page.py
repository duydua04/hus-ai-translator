# tests/pages/admin/admin_user_page.py

from playwright.sync_api import Page, expect


class AdminUserPage:
    def __init__(self, page: Page, base_url: str = ""):
        self.page = page
        self.base_url = base_url

        # Locators
        self.search_input    = page.locator(".search__input")
        self.status_dropdown = page.locator(".filter-select")
        self.table_rows      = page.locator(".data-table tbody tr")
        self.pagination      = page.locator(".pagination")

    # ---------------- ACTIONS ----------------

    def open(self):
        self.page.goto(f"{self.base_url}/users")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_selector(".data-table", timeout=10_000)

    def search_user(self, keyword: str):
        self.search_input.fill(keyword)
        self.page.wait_for_load_state("networkidle")

    def filter_status(self, value: str):
        # value: "" | "active" | "locked"
        self.status_dropdown.select_option(value=value)
        self.page.wait_for_load_state("networkidle")

    def go_to_page(self, page_number: int):
        self.page.locator(
            ".pagination__btn:not([disabled])",
            has_text=str(page_number)
        ).click()
        self.page.wait_for_load_state("networkidle")

    def click_view(self, user_email: str):
        row = self.page.locator(".data-table tbody tr", has_text=user_email)
        row.locator(".table-action[title='Xem chi tiết']").click()

    def click_lock(self, user_email: str):
        row = self.page.locator(".data-table tbody tr", has_text=user_email)
        row.locator(".table-action--lock[title='Khóa']").click()

    # ---------------- ASSERTIONS ----------------

    def expect_user_visible(self, keyword: str):
        expect(self.page.locator(".data-table")).to_contain_text(keyword)

    def expect_no_result(self):
        expect(self.table_rows).to_have_count(0)

    def expect_page_active(self, page_number: int):
        expect(
            self.page.locator(".pagination__btn--active")
        ).to_contain_text(str(page_number))

    def get_first_row_text(self) -> str:
        return self.table_rows.first.text_content()