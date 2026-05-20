"""
pages/rating_modal_page.py  –  UPDATED
────────────────────────────────────────
Không tự goto URL nữa – modal được mở từ HomePage sau khi dịch xong.
"""

from playwright.sync_api import Page, expect


class RatingModalPage:
    def __init__(self, page: Page):
        self.page = page

        # Modal
        self.modal            = page.locator(".modal")
        self.modal_close      = page.locator(".modal__close")

        # Star rating
        self.stars            = page.locator(".star-rating .star")
        self.star_n           = lambda n: page.locator(f".star[aria-label='{n} sao']")

        # Textareas
        self.review_input     = page.locator("textarea[placeholder='Nhập nhận xét về bản dịch (tuỳ chọn)...']")
        self.correction_input = page.locator("textarea[placeholder='Nhập nội dung bản dịch đúng hơn theo ý bạn...']")

        # Toggle correction
        self.toggle_correction = page.locator(".btn-toggle-correction")

        # Footer buttons
        self.cancel_btn       = page.locator(".profile-page__btn--ghost")
        self.submit_btn       = page.locator(".profile-page__btn--primary")

    # ── ACTIONS ──────────────────────────────────────────────────────────────

    def open_via_home_page(self, base_url: str, source: str = "en", target: str = "vi") -> None:
        """
        Luồng đúng để mở modal:
          1. Vào /home/text (đã login sẵn nhờ authenticated_user_page)
          2. Nhập text → dịch → chờ output
          3. Click nút đánh giá → chờ modal
        """
        from pages.home_page import HomePage
        hp = HomePage(self.page, base_url)
        hp.navigate()
        hp.select_source_language(source)
        hp.select_target_language(target)
        hp.type_text("Hello world")
        hp.click_translate()
        hp.wait_for_translation()

        # Click nút đánh giá xuất hiện sau khi có kết quả dịch
        self.page.wait_for_selector(".btn--rate", timeout=10_000)
        self.page.locator(".btn--rate").click()
        self.page.wait_for_selector(".modal", timeout=5_000)

    def click_star(self, n: int):
        self.star_n(n).click()

    def fill_review(self, text: str):
        self.review_input.fill(text)

    def fill_correction(self, text: str):
        self.correction_input.fill(text)

    def toggle_correction_section(self):
        self.toggle_correction.click()

    def submit(self):
        self.submit_btn.click()

    def cancel(self):
        self.cancel_btn.click()

    def close(self):
        self.modal_close.click()

    # ── ASSERTIONS ───────────────────────────────────────────────────────────

    def expect_modal_visible(self):
        expect(self.modal).to_be_visible()

    def expect_modal_hidden(self):
        expect(self.modal).to_be_hidden()

    def expect_star_selected(self, n: int):
        # TODO: cập nhật class sau khi biết app thêm class gì khi chọn sao
        expect(self.star_n(n)).to_have_class(r".*star--active.*")

    def expect_submit_disabled(self):
        expect(self.submit_btn).to_be_disabled()

    def expect_submit_enabled(self):
        expect(self.submit_btn).to_be_enabled()