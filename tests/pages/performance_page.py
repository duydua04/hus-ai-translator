"""
pages/performance_page.py
"""

import time
from dataclasses import dataclass
from pathlib import Path
from playwright.sync_api import Page

FIXTURES_DIR = Path(__file__).parent.parent / "data" / "fixtures"


@dataclass
class TimedResult:
    elapsed_seconds: float
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


class PerformancePage:

    TRANSLATE_BTN = ".translator__action .btn--primary"
    INPUT_AREA    = ".translator__input"
    OUTPUT_AREA   = ".translator__output"

    def __init__(self, page: Page, base_url: str):
        self.page     = page
        self.base_url = base_url.rstrip("/")

    def open_text_translator(self):
        self.page.goto(f"{self.base_url}/home/text")
        self.page.wait_for_load_state("networkidle")

    def open_file_translator(self):
        self.page.goto(f"{self.base_url}/home/file")
        self.page.wait_for_load_state("networkidle")

    def _wait_for_output(self, timeout_ms: int):
        """
        Thử cả textarea .value lẫn div .textContent.
        In ra DOM của output element nếu vẫn timeout để debug.
        """
        self.page.wait_for_function(
            """() => {
                const el = document.querySelector('.translator__output');
                if (!el) return false;
                // textarea dùng .value, div/span dùng .textContent
                const text = (el.value || el.textContent || '').trim();
                return text.length > 0;
            }""",
            timeout=timeout_ms,
        )

    def translate_text_timed(self, text: str, timeout: int = 300) -> TimedResult:
        t0 = 0.0
        try:
            self.open_text_translator()
            self.page.fill(self.INPUT_AREA, "")
            self.page.fill(self.INPUT_AREA, text)

            t0 = time.perf_counter()
            self.page.click(self.TRANSLATE_BTN)
            self._wait_for_output(timeout * 1000)

            elapsed = time.perf_counter() - t0
            return TimedResult(elapsed_seconds=round(elapsed, 3))

        except Exception as exc:
            elapsed = time.perf_counter() - t0

            # ── Debug: in ra HTML của output element để biết selector đúng chưa
            try:
                html = self.page.inner_html(".translator__output")
                val  = self.page.evaluate(
                    "() => { const e = document.querySelector('.translator__output'); "
                    "return e ? (e.value || e.textContent || '[empty]') : '[not found]'; }"
                )
                print(f"\n  [DEBUG] .translator__output HTML : {html[:200]}")
                print(f"  [DEBUG] value/textContent        : {repr(val[:200])}")
            except Exception:
                print("\n  [DEBUG] Không thể đọc .translator__output — kiểm tra lại selector")

            return TimedResult(elapsed_seconds=round(elapsed, 3), error=str(exc))

    def translate_pdf_timed(self, filename: str, timeout: int = 300) -> TimedResult:
        file_path = FIXTURES_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"PDF không tồn tại: {file_path}")

        t0 = 0.0
        try:
            self.open_file_translator()
            self.page.set_input_files("input[type='file']", str(file_path))

            t0 = time.perf_counter()
            self.page.click(self.TRANSLATE_BTN)

            self.page.wait_for_selector(
                ".upload__result",
                timeout=timeout * 1000,
            )
            elapsed = time.perf_counter() - t0
            return TimedResult(elapsed_seconds=round(elapsed, 3))

        except Exception as exc:
            elapsed = time.perf_counter() - t0
            return TimedResult(elapsed_seconds=round(elapsed, 3), error=str(exc))