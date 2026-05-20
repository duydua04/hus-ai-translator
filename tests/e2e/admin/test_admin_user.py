"""
e2e/admin/test_admin_user.py
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.admin.admin_user_page import AdminUserPage


@pytest.fixture()
def admin_users(admin_user_page: AdminUserPage) -> AdminUserPage:
    admin_user_page.open()
    return admin_user_page

# ══════════════════════════════════════════════════════════════════════════════
# LOCATORS – map từ HTML thực tế
# ══════════════════════════════════════════════════════════════════════════════

class L:
    # Bảng
    TABLE_ROW      = ".data-table tbody tr"
    COL_HEADERS    = ".data-table thead th"

    # Ô dữ liệu trong row
    CELL_NAME      = ".user-cell__name"
    CELL_EMAIL     = ".user-cell__email"
    CELL_STATUS    = "td .badge:last-child"   # badge trạng thái (cột 3)
    CELL_DATE      = ".cell-date"

    # Tìm kiếm & lọc
    SEARCH_INPUT   = ".search__input"
    FILTER_STATUS  = ".filter-select"

    # Hành động
    VIEW_BTN       = ".table-action[title='Xem chi tiết']"
    LOCK_BTN       = ".table-action--lock[title='Khóa']"

    # Pagination
    PAGINATION     = ".pagination"
    PAGE_INFO      = ".pagination__info"


# ══════════════════════════════════════════════════════════════════════════════
# 1. HIỂN THỊ DANH SÁCH USER
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminUserList:

    def test_hien_thi_danh_sach_user(self, admin_users: AdminUserPage):
        """Trang quản lý user tải xong → có ít nhất 1 user trong bảng."""
        rows = admin_users.page.locator(L.TABLE_ROW)
        expect(rows.first).to_be_visible()

    def test_hien_thi_du_cot_thong_tin(self, admin_users: AdminUserPage):
        """Bảng user phải có đủ các cột: Người dùng, Gói, Trạng thái, Ngày đăng ký, Hành động."""
        headers = admin_users.page.locator(L.COL_HEADERS).all_inner_texts()
        assert "Người dùng"    in headers
        assert "Gói"           in headers
        assert "Trạng thái"    in headers
        assert "Ngày đăng ký"  in headers
        assert "Hành động"     in headers

    def test_hien_thi_ten_va_email_user(self, admin_users: AdminUserPage):
        """Mỗi row phải có tên và email."""
        expect(admin_users.page.locator(L.CELL_NAME).first).to_be_visible()
        expect(admin_users.page.locator(L.CELL_EMAIL).first).to_be_visible()

    def test_hien_thi_pagination(self, admin_users: AdminUserPage):
        """Pagination hiển thị đúng tổng số mục."""
        expect(admin_users.page.locator(L.PAGE_INFO)).to_be_visible()
        info = admin_users.page.locator(L.PAGE_INFO).inner_text()
        assert "mục" in info, f"Pagination info sai: {info}"


# ══════════════════════════════════════════════════════════════════════════════
# 2. TÌM KIẾM / LỌC USER
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminUserSearch:

    def test_tim_kiem_user_theo_email(self, admin_users: AdminUserPage, valid_user: dict):
        """Tìm kiếm email hợp lệ → danh sách chỉ hiển thị user đó."""
        admin_users.page.locator(L.SEARCH_INPUT).fill(valid_user["email"])
        admin_users.page.wait_for_load_state("networkidle")

        emails = admin_users.page.locator(L.CELL_EMAIL).all_inner_texts()
        assert len(emails) >= 1, "Phải có ít nhất 1 kết quả"
        for email in emails:
            assert valid_user["email"].lower() in email.lower(), \
                f"Kết quả tìm kiếm sai: {email}"

    def test_tim_kiem_user_theo_ten(self, admin_users: AdminUserPage):
        """Tìm kiếm theo tên → kết quả khớp."""
        admin_users.page.locator(L.SEARCH_INPUT).fill("Hoàng Duy")
        admin_users.page.wait_for_load_state("networkidle")

        names = admin_users.page.locator(L.CELL_NAME).all_inner_texts()
        assert any("Hoàng Duy" in n for n in names), \
            f"Không tìm thấy user: {names}"

    def test_tim_kiem_email_khong_ton_tai(self, admin_users: AdminUserPage):
        """Tìm kiếm email không tồn tại → bảng rỗng."""
        admin_users.page.locator(L.SEARCH_INPUT).fill("emailkhongtontai@xyz.com")
        admin_users.page.wait_for_load_state("networkidle")

        rows = admin_users.page.locator(L.TABLE_ROW)
        assert rows.count() == 0, "Bảng phải rỗng khi không có kết quả"

    def test_loc_user_theo_trang_thai_active(self, admin_users: AdminUserPage):
        """Lọc 'Đang hoạt động' → chỉ hiển thị user active."""
        admin_users.page.locator(L.FILTER_STATUS).select_option(value="active")
        admin_users.page.wait_for_load_state("networkidle")

        statuses = admin_users.page.locator(L.CELL_STATUS).all_inner_texts()
        assert len(statuses) >= 1, "Phải có ít nhất 1 user active"
        for s in statuses:
            assert "hoạt động" in s.lower(), f"Kết quả lọc sai trạng thái: {s}"

    def test_loc_user_bi_khoa(self, admin_users: AdminUserPage):
        """Lọc 'Bị vô hiệu hóa' → chỉ hiển thị user bị khóa."""
        admin_users.page.locator(L.FILTER_STATUS).select_option(value="locked")
        admin_users.page.wait_for_load_state("networkidle")

        statuses = admin_users.page.locator(L.CELL_STATUS).all_inner_texts()
        assert len(statuses) >= 1, "Phải có ít nhất 1 user bị khóa"
        for s in statuses:
            assert "khóa" in s.lower() or "vô hiệu" in s.lower(), \
                f"Kết quả lọc sai trạng thái: {s}"

    def test_loc_tat_ca_trang_thai(self, admin_users: AdminUserPage):
        """Lọc 'Tất cả trạng thái' → hiển thị toàn bộ user."""
        admin_users.page.locator(L.FILTER_STATUS).select_option(value="")
        admin_users.page.wait_for_load_state("networkidle")

        rows = admin_users.page.locator(L.TABLE_ROW)
        assert rows.count() >= 1


# ══════════════════════════════════════════════════════════════════════════════
# 3. XEM CHI TIẾT USER
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminUserDetail:

    def test_nut_xem_chi_tiet_hien_thi(self, admin_users: AdminUserPage):
        """Mỗi row phải có nút 'Xem chi tiết'."""
        expect(admin_users.page.locator(L.VIEW_BTN).first).to_be_visible()

    def test_xem_chi_tiet_user(self, admin_users: AdminUserPage):
        """Click nút Xem chi tiết → mở modal/trang chi tiết."""
        admin_users.page.locator(L.VIEW_BTN).first.click()
        admin_users.page.wait_for_load_state("networkidle")

        # TODO: cập nhật selector modal chi tiết sau khi có HTML
        # expect(admin_users.page.locator(".user-detail-modal")).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# 4. KHÓA USER
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminUserLock:

    def test_nut_khoa_hien_thi(self, admin_users: AdminUserPage):
        """Mỗi row active phải có nút Khóa."""
        expect(admin_users.page.locator(L.LOCK_BTN).first).to_be_visible()

    def test_khoa_user(self, admin_users: AdminUserPage):
        """Click Khóa → user chuyển sang trạng thái bị vô hiệu hóa."""
        first_row = admin_users.page.locator(L.TABLE_ROW).first

        first_row.locator(L.LOCK_BTN).click()
        admin_users.page.wait_for_load_state("networkidle")

        # TODO: cập nhật sau khi biết badge class khi bị khóa
        # status_badge = first_row.locator(".badge")
        # expect(status_badge).to_contain_text("Vô hiệu")