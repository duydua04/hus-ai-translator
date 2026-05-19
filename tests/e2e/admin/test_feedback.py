"""
e2e/admin/test_feedback.py
───────────────────────────
Test E2E cho luồng Feedback:
  - User gửi feedback
  - Admin xem danh sách feedback
  - Admin lọc và phản hồi feedback
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from pages.admin.feedback_page import FeedbackPage


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURE – FeedbackPage đã đăng nhập admin
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def fb_page(authenticated_admin_page: Page, feedback_page: FeedbackPage) -> FeedbackPage:
    """
    FeedbackPage đã đăng nhập admin sẵn.
    authenticated_admin_page lo việc login, feedback_page lo POM.
    """
    # Gán page đã login vào FeedbackPage
    # TODO: kiểm tra lại cách FeedbackPage nhận page (tuỳ cách bạn viết POM)
    feedback_page.page = authenticated_admin_page
    feedback_page.navigate()
    return feedback_page


# ══════════════════════════════════════════════════════════════════════════════
# 1. USER GỬI FEEDBACK
# ══════════════════════════════════════════════════════════════════════════════

class TestUserSendFeedback:
    """
    Test luồng user gửi feedback từ phía user (port 3000).
    Dùng authenticated_user_page.
    """

    def test_gui_feedback_hop_le(self, authenticated_user_page: Page):
        """User điền feedback hợp lệ → gửi thành công → hiển thị thông báo."""
        # TODO: thay các selector cho đúng app (user side)
        FEEDBACK_BTN     = "[data-testid='feedback-btn']"      # ← nút mở form feedback
        RATING_STAR      = "[data-testid='star-5']"             # ← chọn 5 sao
        CONTENT_INPUT    = "[data-testid='feedback-content']"   # ← ô nhập nội dung
        SUBMIT_BTN       = "[data-testid='submit-feedback']"    # ← nút gửi
        SUCCESS_MSG      = "[data-testid='feedback-success']"   # ← thông báo thành công

        authenticated_user_page.locator(FEEDBACK_BTN).click()
        authenticated_user_page.locator(RATING_STAR).click()
        authenticated_user_page.locator(CONTENT_INPUT).fill(
            "Ứng dụng dịch rất tốt, giao diện dễ dùng!"
        )
        authenticated_user_page.locator(SUBMIT_BTN).click()

        expect(authenticated_user_page.locator(SUCCESS_MSG)).to_be_visible()

    def test_gui_feedback_thieu_noi_dung(self, authenticated_user_page: Page):
        """User không nhập nội dung → nút gửi bị disabled hoặc hiển thị lỗi."""
        FEEDBACK_BTN  = "[data-testid='feedback-btn']"    # ← đổi
        RATING_STAR   = "[data-testid='star-3']"           # ← đổi
        SUBMIT_BTN    = "[data-testid='submit-feedback']"  # ← đổi

        authenticated_user_page.locator(FEEDBACK_BTN).click()
        authenticated_user_page.locator(RATING_STAR).click()
        # Không nhập content

        # TODO: tuỳ app: nút disabled hoặc hiện thông báo lỗi
        submit = authenticated_user_page.locator(SUBMIT_BTN)
        expect(submit).to_be_disabled()

    def test_gui_feedback_thieu_rating(self, authenticated_user_page: Page):
        """User không chọn sao đánh giá → không thể gửi."""
        FEEDBACK_BTN  = "[data-testid='feedback-btn']"    # ← đổi
        CONTENT_INPUT = "[data-testid='feedback-content']"  # ← đổi
        SUBMIT_BTN    = "[data-testid='submit-feedback']"  # ← đổi

        authenticated_user_page.locator(FEEDBACK_BTN).click()
        authenticated_user_page.locator(CONTENT_INPUT).fill("Feedback test không có sao")
        # Không chọn rating

        submit = authenticated_user_page.locator(SUBMIT_BTN)
        expect(submit).to_be_disabled()


# ══════════════════════════════════════════════════════════════════════════════
# 2. ADMIN XEM DANH SÁCH FEEDBACK
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminViewFeedback:

    def test_hien_thi_danh_sach_feedback(self, fb_page: FeedbackPage):
        """Trang admin feedback tải xong → có ít nhất 1 feedback trong danh sách."""
        # TODO: thay selector danh sách feedback
        FEEDBACK_ROW = "[data-testid='feedback-row']"  # ← đổi

        rows = fb_page.page.locator(FEEDBACK_ROW)
        expect(rows.first).to_be_visible()

    def test_hien_thi_du_thong_tin_moi_feedback(self, fb_page: FeedbackPage):
        """Mỗi feedback phải có: tên user, nội dung, rating, ngày gửi."""
        # TODO: thay các selector cho đúng
        FEEDBACK_ROW    = "[data-testid='feedback-row']"       # ← đổi
        USER_NAME_COL   = "[data-testid='feedback-username']"  # ← đổi
        CONTENT_COL     = "[data-testid='feedback-content']"   # ← đổi
        RATING_COL      = "[data-testid='feedback-rating']"    # ← đổi
        DATE_COL        = "[data-testid='feedback-date']"      # ← đổi

        first_row = fb_page.page.locator(FEEDBACK_ROW).first
        expect(first_row.locator(USER_NAME_COL)).not_to_be_empty()
        expect(first_row.locator(CONTENT_COL)).not_to_be_empty()
        expect(first_row.locator(RATING_COL)).to_be_visible()
        expect(first_row.locator(DATE_COL)).not_to_be_empty()


# ══════════════════════════════════════════════════════════════════════════════
# 3. ADMIN LỌC FEEDBACK
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminFilterFeedback:

    def test_loc_theo_rating_cao(self, fb_page: FeedbackPage):
        """Lọc rating 5 sao → chỉ hiển thị feedback 5 sao."""
        # TODO: thay selector bộ lọc và rating
        FILTER_SELECT   = "[data-testid='filter-rating']"    # ← đổi
        RATING_DISPLAY  = "[data-testid='feedback-rating']"  # ← đổi

        fb_page.page.locator(FILTER_SELECT).select_option(value="5")
        fb_page.page.wait_for_load_state("networkidle")

        # Kiểm tra tất cả kết quả đều là 5 sao
        # TODO: tuỳ cách app hiển thị rating (số, sao, text)
        ratings = fb_page.page.locator(RATING_DISPLAY).all_inner_texts()
        for r in ratings:
            assert "5" in r, f"Kết quả lọc phải là 5 sao, nhưng thấy: {r}"

    def test_loc_theo_trang_thai_chua_phan_hoi(self, fb_page: FeedbackPage):
        """Lọc trạng thái 'Chưa phản hồi' → chỉ hiển thị feedback chưa xử lý."""
        # TODO: thay selector và value cho đúng
        FILTER_STATUS  = "[data-testid='filter-status']"       # ← đổi
        STATUS_DISPLAY = "[data-testid='feedback-status']"     # ← đổi

        fb_page.page.locator(FILTER_STATUS).select_option(value="pending")
        fb_page.page.wait_for_load_state("networkidle")

        statuses = fb_page.page.locator(STATUS_DISPLAY).all_inner_texts()
        for s in statuses:
            # TODO: thay text trạng thái cho đúng app
            assert "chưa" in s.lower() or "pending" in s.lower(), \
                f"Kết quả lọc phải là 'chưa phản hồi', nhưng thấy: {s}"

    def test_tim_kiem_feedback_theo_ten_user(self, fb_page: FeedbackPage, valid_user: dict):
        """Tìm kiếm theo tên user → chỉ hiển thị feedback của user đó."""
        # TODO: thay selector search box
        SEARCH_INPUT    = "[data-testid='feedback-search']"   # ← đổi
        USER_NAME_COL   = "[data-testid='feedback-username']" # ← đổi

        fb_page.page.locator(SEARCH_INPUT).fill(valid_user["email"])
        fb_page.page.keyboard.press("Enter")
        fb_page.page.wait_for_load_state("networkidle")

        results = fb_page.page.locator(USER_NAME_COL).all_inner_texts()
        for name in results:
            assert valid_user["email"] in name, \
                f"Kết quả tìm kiếm sai user: {name}"


# ══════════════════════════════════════════════════════════════════════════════
# 4. ADMIN PHẢN HỒI FEEDBACK
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminReplyFeedback:

    def test_phan_hoi_feedback_thanh_cong(self, fb_page: FeedbackPage):
        """Admin mở feedback → nhập phản hồi → gửi → trạng thái cập nhật thành 'Đã phản hồi'."""
        # TODO: thay tất cả selector cho đúng app
        FEEDBACK_ROW    = "[data-testid='feedback-row']"         # ← đổi
        REPLY_BTN       = "[data-testid='reply-btn']"            # ← đổi (nút trong mỗi row)
        REPLY_INPUT     = "[data-testid='reply-input']"          # ← đổi
        SUBMIT_REPLY    = "[data-testid='submit-reply']"         # ← đổi
        STATUS_DISPLAY  = "[data-testid='feedback-status']"      # ← đổi

        # Lấy feedback đầu tiên chưa phản hồi
        first_row = fb_page.page.locator(FEEDBACK_ROW).first
        first_row.locator(REPLY_BTN).click()

        fb_page.page.locator(REPLY_INPUT).fill("Cảm ơn bạn đã gửi phản hồi. Chúng tôi sẽ cải thiện!")
        fb_page.page.locator(SUBMIT_REPLY).click()
        fb_page.page.wait_for_load_state("networkidle")

        # Kiểm tra trạng thái đổi sang "Đã phản hồi"
        # TODO: thay text trạng thái cho đúng app
        expect(first_row.locator(STATUS_DISPLAY)).to_contain_text("Đã phản hồi")

    def test_phan_hoi_trong_khong_gui_duoc(self, fb_page: FeedbackPage):
        """Admin không nhập nội dung phản hồi → không thể gửi."""
        FEEDBACK_ROW = "[data-testid='feedback-row']"   # ← đổi
        REPLY_BTN    = "[data-testid='reply-btn']"       # ← đổi
        SUBMIT_REPLY = "[data-testid='submit-reply']"    # ← đổi

        first_row = fb_page.page.locator(FEEDBACK_ROW).first
        first_row.locator(REPLY_BTN).click()
        # Không nhập nội dung

        expect(fb_page.page.locator(SUBMIT_REPLY)).to_be_disabled()