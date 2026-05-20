"""
e2e/admin/test_dashboard.py
────────────────────────────
Test E2E cho trang Dashboard – Admin (port 3001).
Kiểm tra các số liệu thống kê hiển thị đúng và đầy đủ.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.admin.dashboard_page import DashboardPage


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURE – DashboardPage đã đăng nhập
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def dash(authenticated_admin_page: Page, dashboard_page: DashboardPage) -> DashboardPage:
    """DashboardPage đã đăng nhập admin sẵn, đã navigate."""
    # TODO: kiểm tra lại cách DashboardPage nhận page
    dashboard_page.page = authenticated_admin_page
    dashboard_page.navigate()
    return dashboard_page


# ══════════════════════════════════════════════════════════════════════════════
# 1. KIỂM TRA CÁC THẺ THỐNG KÊ (STAT CARDS)
# ══════════════════════════════════════════════════════════════════════════════

class TestDashboardStatCards:

    def test_hien_thi_tong_so_user(self, dash: DashboardPage):
        """Dashboard hiển thị thẻ tổng số user → giá trị là số dương."""
        # TODO: thay selector thẻ thống kê
        TOTAL_USERS_CARD = "[data-testid='stat-total-users']"  # ← đổi
        STAT_VALUE       = "[data-testid='stat-value']"         # ← đổi (con của card)

        card = dash.page.locator(TOTAL_USERS_CARD)
        expect(card).to_be_visible()

        value_text = card.locator(STAT_VALUE).inner_text()
        # TODO: tuỳ app hiển thị số như thế nào (1,234 hoặc 1234)
        value = int(value_text.replace(",", "").replace(".", "").strip())
        assert value > 0, f"Tổng số user phải > 0, nhưng thấy: {value}"

    def test_hien_thi_tong_so_bai_dich(self, dash: DashboardPage):
        """Dashboard hiển thị thẻ tổng số bài dịch."""
        # TODO: thay selector
        TOTAL_TRANS_CARD = "[data-testid='stat-total-translations']"  # ← đổi
        STAT_VALUE       = "[data-testid='stat-value']"

        card = dash.page.locator(TOTAL_TRANS_CARD)
        expect(card).to_be_visible()

        value_text = card.locator(STAT_VALUE).inner_text()
        value = int(value_text.replace(",", "").replace(".", "").strip())
        assert value >= 0, "Tổng số bài dịch không được âm"

    def test_hien_thi_tong_so_feedback(self, dash: DashboardPage):
        """Dashboard hiển thị thẻ tổng số feedback."""
        # TODO: thay selector
        TOTAL_FB_CARD = "[data-testid='stat-total-feedback']"  # ← đổi
        STAT_VALUE    = "[data-testid='stat-value']"

        card = dash.page.locator(TOTAL_FB_CARD)
        expect(card).to_be_visible()

    def test_tat_ca_stat_cards_co_gia_tri(self, dash: DashboardPage):
        """Tất cả thẻ thống kê phải hiển thị giá trị (không rỗng, không '--')."""
        # TODO: thay selector tất cả stat cards
        ALL_STAT_VALUES = "[data-testid='stat-value']"  # ← đổi

        values = dash.page.locator(ALL_STAT_VALUES).all_inner_texts()
        assert len(values) > 0, "Phải có ít nhất 1 thẻ thống kê"
        for v in values:
            assert v.strip() not in ("", "--", "N/A"), \
                f"Thẻ thống kê không được rỗng: '{v}'"


# ══════════════════════════════════════════════════════════════════════════════
# 2. KIỂM TRA BIỂU ĐỒ / CHART
# ══════════════════════════════════════════════════════════════════════════════

class TestDashboardCharts:

    def test_bieu_do_hien_thi(self, dash: DashboardPage):
        """Biểu đồ thống kê phải hiển thị được (không bị lỗi render)."""
        # TODO: thay selector container biểu đồ (canvas hoặc svg của chart)
        CHART_CONTAINER = "[data-testid='dashboard-chart']"  # ← đổi

        expect(dash.page.locator(CHART_CONTAINER)).to_be_visible()

    def test_bieu_do_theo_ngay_hien_thi(self, dash: DashboardPage):
        """Biểu đồ số lượng dịch theo ngày render thành công."""
        # TODO: thay selector
        DAILY_CHART = "[data-testid='chart-daily-translations']"  # ← đổi

        expect(dash.page.locator(DAILY_CHART)).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# 3. KIỂM TRA ĐIỀU HƯỚNG TỪ DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

class TestDashboardNavigation:

    def test_click_xem_tat_ca_users(self, dash: DashboardPage):
        """Click 'Xem tất cả' ở thẻ user → điều hướng sang trang quản lý user."""
        # TODO: thay selector nút và URL đích
        VIEW_ALL_USERS_BTN = "[data-testid='view-all-users']"   # ← đổi
        USER_MANAGE_PATH   = "/users"                      # ← đổi đúng path

        dash.page.locator(VIEW_ALL_USERS_BTN).click()
        dash.page.wait_for_load_state("networkidle")

        expect(dash.page).to_have_url(f"http://localhost:3001{USER_MANAGE_PATH}")

    def test_click_xem_tat_ca_feedback(self, dash: DashboardPage):
        """Click 'Xem tất cả' ở thẻ feedback → điều hướng sang trang feedback."""
        # TODO: thay selector và URL đích
        VIEW_ALL_FB_BTN = "[data-testid='view-all-feedback']"  # ← đổi
        FB_PATH         = "/feedback"                      # ← đổi đúng path

        dash.page.locator(VIEW_ALL_FB_BTN).click()
        dash.page.wait_for_load_state("networkidle")

        expect(dash.page).to_have_url(f"http://localhost:3001{FB_PATH}")