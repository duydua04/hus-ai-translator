"""
e2e/user/test_rating_modal.py  –  UPDATED
───────────────────────────────────────────
Luồng đúng:
  authenticated_user_page (đã login) → vào /home/text
  → dịch 1 câu → chờ output → click .btn--rate → modal xuất hiện

Chạy:
    pytest e2e/user/test_rating_modal.py -v
    pytest e2e/user/test_rating_modal.py -v --headed
    pytest e2e/user/test_rating_modal.py -k "display"
"""

from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.rating_modal_page import RatingModalPage


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURE
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def rating(authenticated_user_page: Page, base_url: str) -> RatingModalPage:
    """
    Trả về RatingModalPage đã mở modal sẵn.
    Dùng authenticated_user_page → đã login, không cần login lại.
    Luồng: /home/text → nhập text → dịch → click .btn--rate → modal mở.
    """
    rm = RatingModalPage(authenticated_user_page)
    rm.open_via_home_page(base_url)
    return rm


# ══════════════════════════════════════════════════════════════════════════════
# 1. HIỂN THỊ – kiểm tra UI khi modal mở
# ══════════════════════════════════════════════════════════════════════════════

@allure.feature("Rating Modal")
@allure.story("Hiển thị")
class TestRatingModalDisplay:

    def test_modal_hien_thi(self, rating: RatingModalPage):
        """Modal đánh giá hiển thị đầy đủ các thành phần."""
        rating.expect_modal_visible()
        expect(rating.stars).to_have_count(5)
        expect(rating.review_input).to_be_visible()
        expect(rating.submit_btn).to_be_visible()
        expect(rating.cancel_btn).to_be_visible()

    def test_hien_thi_du_5_sao(self, rating: RatingModalPage):
        """Star rating có đúng 5 nút sao."""
        expect(rating.stars).to_have_count(5)

    def test_correction_hien_thi_mac_dinh(self, rating: RatingModalPage):
        """Phần đề xuất sửa hiển thị mặc định khi mở modal."""
        expect(rating.correction_input).to_be_visible()

    def test_toggle_an_hien_correction(self, rating: RatingModalPage):
        """Click toggle → ẩn correction → click lại → hiện lại."""
        expect(rating.correction_input).to_be_visible()
        rating.toggle_correction_section()
        expect(rating.correction_input).to_be_hidden()
        rating.toggle_correction_section()
        expect(rating.correction_input).to_be_visible()

    def test_submit_disabled_khi_chua_chon_sao(self, rating: RatingModalPage):
        """Nút Gửi bị disabled khi chưa chọn sao."""
        rating.expect_submit_disabled()


# ══════════════════════════════════════════════════════════════════════════════
# 2. ACTIONS – các thao tác trong modal
# ══════════════════════════════════════════════════════════════════════════════

@allure.feature("Rating Modal")
@allure.story("Thao tác")
class TestRatingModalActions:

    @pytest.mark.parametrize("star", [1, 2, 3, 4, 5])
    def test_chon_sao(self, rating: RatingModalPage, star: int):
        """Click từng sao → nút Gửi được enable."""
        with allure.step(f"Chọn {star} sao"):
            rating.click_star(star)
            rating.expect_submit_enabled()

    def test_nhap_nhan_xet(self, rating: RatingModalPage):
        """Nhập nhận xét → textarea hiển thị đúng nội dung."""
        rating.fill_review("Bản dịch khá tốt, tự nhiên")
        expect(rating.review_input).to_have_value("Bản dịch khá tốt, tự nhiên")

    def test_nhap_de_xuat_sua(self, rating: RatingModalPage):
        """Nhập đề xuất sửa → textarea hiển thị đúng nội dung."""
        rating.fill_correction("Nên dịch là: Xin chào thế giới")
        expect(rating.correction_input).to_have_value("Nên dịch là: Xin chào thế giới")

    def test_huy_dong_modal(self, rating: RatingModalPage):
        """Click Huỷ → modal đóng."""
        rating.cancel()
        rating.expect_modal_hidden()

    def test_close_btn_dong_modal(self, rating: RatingModalPage):
        """Click X → modal đóng."""
        rating.close()
        rating.expect_modal_hidden()


# ══════════════════════════════════════════════════════════════════════════════
# 3. SUBMIT – các trường hợp gửi đánh giá
# ══════════════════════════════════════════════════════════════════════════════

@allure.feature("Rating Modal")
@allure.story("Gửi đánh giá")
class TestRatingModalSubmit:

    def test_gui_day_du_sao_va_nhan_xet(self, rating: RatingModalPage):
        """Chọn 5 sao + nhập nhận xét đầy đủ → Gửi → modal đóng."""
        rating.click_star(5)
        rating.fill_review("Bản dịch rất tốt, chính xác!")
        rating.fill_correction("Không cần sửa gì thêm.")
        rating.submit()
        rating.expect_modal_hidden()

    def test_gui_chi_voi_sao_khong_nhan_xet(self, rating: RatingModalPage):
        """Chỉ chọn sao (review và correction để trống) → vẫn gửi được."""
        rating.click_star(3)
        rating.submit()
        rating.expect_modal_hidden()

    def test_gui_voi_correction_an(self, rating: RatingModalPage):
        """Toggle ẩn correction → chọn sao → gửi thành công."""
        rating.toggle_correction_section()
        rating.click_star(4)
        rating.fill_review("Tạm ổn")
        rating.submit()
        rating.expect_modal_hidden()

    def test_gui_khong_chon_sao(self, rating: RatingModalPage):
        """Nhấn Gửi mà không chọn sao → modal vẫn mở (sao là bắt buộc)."""
        rating.fill_review("Có nhận xét nhưng không chọn sao")
        rating.submit()
        rating.expect_modal_visible()

    @pytest.mark.parametrize("star,review", [
        (1, "Kết quả rất kém"),
        (2, "Cần cải thiện nhiều"),
        (3, "Tạm được"),
        (4, "Khá tốt"),
        (5, "Xuất sắc!"),
    ])
    def test_gui_tung_muc_sao(
        self, rating: RatingModalPage, star: int, review: str
    ):
        """Gửi đánh giá với từng mức sao từ 1 đến 5."""
        with allure.step(f"{star} sao – '{review}'"):
            rating.click_star(star)
            rating.fill_review(review)
            rating.submit()
            rating.expect_modal_hidden()