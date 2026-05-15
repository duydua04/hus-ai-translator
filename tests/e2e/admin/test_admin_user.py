# tests/tests/test_admin_user.py

import pytest
from tests.pages.admin.admin_user_page import AdminUserPage


class TestAdminUser:

    # ---------------- SEARCH ----------------

    def test_search_existing_user(self, page):
        admin = AdminUserPage(page)
        admin.open()

        admin.search_user("Nguyễn Hải")
        admin.expect_user_visible("Nguyễn Hải")

    def test_search_not_found(self, page):
        admin = AdminUserPage(page)
        admin.open()

        admin.search_user("abcxyznotfound")
        admin.expect_no_result()

    # ---------------- FILTER STATUS ----------------

    def test_filter_status(self, page):
        admin = AdminUserPage(page)
        admin.open()

        admin.filter_status("Đang hoạt động")
        admin.expect_user_visible("Đang hoạt động")

    # ---------------- PACKAGE FILTER ----------------

    def test_filter_package(self, page):
        admin = AdminUserPage(page)
        admin.open()

        admin.filter_package("Pro")
        admin.expect_user_visible("Pro")

    # ---------------- SORT ----------------

    def test_sort_newest(self, page):
        admin = AdminUserPage(page)
        admin.open()

        admin.sort_by("Mới nhất trước")

        first_row = admin.get_first_row_text()
        assert first_row is not None

    # ---------------- PAGINATION ----------------

    def test_pagination_page_2(self, page):
        admin = AdminUserPage(page)
        admin.open()

        admin.go_to_page(2)
        admin.expect_page_active(2)

    # ---------------- LOCK/UNLOCK ----------------

    def test_lock_unlock_user(self, page):
        admin = AdminUserPage(page)
        admin.open()

        admin.toggle_lock_user("user@gmail.com")

        # verify UI change
        admin.expect_user_visible("Bị vô hiệu hóa")