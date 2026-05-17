# tests/pages/admin_user_page.py

from playwright.sync_api import expect


class AdminUserPage:
    def __init__(self, page):
        self.page = page

        # Locators (giả định - bạn chỉnh theo UI thật)
        self.search_input = page.locator("input[name='search']")
        self.status_dropdown = page.locator("#status-filter")
        self.package_dropdown = page.locator("#package-filter")
        self.sort_dropdown = page.locator("#sort-filter")

        self.table_rows = page.locator("table tbody tr")
        self.pagination = page.locator(".pagination")
        self.page_2 = page.locator("text=2")

    # ---------------- ACTIONS ----------------

    def open(self):
        self.page.goto("/admin/users")

    def search_user(self, keyword: str):
        self.search_input.fill(keyword)
        self.search_input.press("Enter")

    def filter_status(self, status: str):
        self.status_dropdown.click()
        self.page.locator(f"text={status}").click()

    def filter_package(self, package: str):
        self.package_dropdown.click()
        self.page.locator(f"text={package}").click()

    def sort_by(self, option: str):
        self.sort_dropdown.click()
        self.page.locator(f"text={option}").click()

    def go_to_page(self, page_number: int):
        self.page.locator(f"text={page_number}").click()

    def toggle_lock_user(self, user_email: str):
        row = self.page.locator("tr", has_text=user_email)
        row.locator("button").click()  # lock/unlock button
        self.page.locator("text=Confirm").click()

    # ---------------- ASSERTIONS ----------------

    def expect_user_visible(self, keyword: str):
        expect(self.page.locator("table")).to_contain_text(keyword)

    def expect_no_result(self):
        expect(self.page.locator("text=Không tìm thấy")).to_be_visible()

    def expect_page_active(self, page_number: int):
        expect(self.page.locator(f".pagination .active")).to_contain_text(str(page_number))

    def get_first_row_text(self):
        return self.table_rows.first.text_content()