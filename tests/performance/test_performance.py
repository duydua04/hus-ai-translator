"""
e2e/user/test_performance.py
─────────────────────────────
Đo thời gian thực tế — giới hạn 2000 ký tự/lần dịch.
Chạy: pytest e2e/user/test_performance.py -v -s --headed
"""

import time
import pytest
from playwright.sync_api import Page
from tests.performance.pages.performance_page import PerformancePage
from tests.performance.data.performance_data import (
    PDF_2P, TEXT_SMALL, TEXT_MEDIUM, TEXT_LARGE,
    LABEL_SMALL, LABEL_MEDIUM, LABEL_LARGE,
    PDF_5P, PDF_10P, PDF_20P,PDF_1P,TEXT_SMALL_SMALLER, TEXT_SMALL_SMALL, LABEL_SMALL_SMALLER, LABEL_SMALL_SMALL,   
)
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
SEP = "─" * 55


@pytest.fixture()
def perf_page(authenticated_user_page: Page) -> PerformancePage:
    return PerformancePage(authenticated_user_page, BASE_URL)


# ======================================================================
# TEXT
# ======================================================================

class TestTextTranslationTiming:
    def test_translate_small_smaller(self, perf_page):
        print(f"\n{SEP}\n  📝 Dịch  {LABEL_SMALL_SMALLER}\n{SEP}")
        r = perf_page.translate_text_timed(TEXT_SMALL_SMALLER)
        print(f"  ✅ Hoàn thành : {r.elapsed_seconds:.3f}s")
        if r.error:
            print(f"  ❌ Lỗi : {r.error}")
            pytest.fail(r.error)

    def test_translate_small_small(self, perf_page):
        print(f"\n{SEP}\n  📝 Dịch  {LABEL_SMALL_SMALL}\n{SEP}")
        r = perf_page.translate_text_timed(TEXT_SMALL_SMALL)
        print(f"  ✅ Hoàn thành : {r.elapsed_seconds:.3f}s")
        if r.error:
            print(f"  ❌ Lỗi : {r.error}")
            pytest.fail(r.error)
    def test_translate_small(self, perf_page):
        print(f"\n{SEP}\n  📝 Dịch  {LABEL_SMALL}\n{SEP}")
        r = perf_page.translate_text_timed(TEXT_SMALL)
        print(f"  ✅ Hoàn thành : {r.elapsed_seconds:.3f}s")
        if r.error:
            print(f"  ❌ Lỗi : {r.error}")
            pytest.fail(r.error)

    def test_translate_medium(self, perf_page):
        print(f"\n{SEP}\n  📝 Dịch  {LABEL_MEDIUM}\n{SEP}")
        r = perf_page.translate_text_timed(TEXT_MEDIUM)
        print(f"  ✅ Hoàn thành : {r.elapsed_seconds:.3f}s")
        if r.error:
            print(f"  ❌ Lỗi : {r.error}")
            pytest.fail(r.error)

    def test_translate_large(self, perf_page):
        print(f"\n{SEP}\n  📝 Dịch  {LABEL_LARGE}\n{SEP}")
        r = perf_page.translate_text_timed(TEXT_LARGE)
        print(f"  ✅ Hoàn thành : {r.elapsed_seconds:.3f}s")
        if r.error:
            print(f"  ❌ Lỗi : {r.error}")
            pytest.fail(r.error)

    def test_text_timing_summary(self, perf_page):
        cases = [
            (LABEL_SMALL_SMALLER,  TEXT_SMALL_SMALLER,  10),
            (LABEL_SMALL_SMALL,   TEXT_SMALL_SMALL,   20),
            (LABEL_SMALL,  TEXT_SMALL,  60),
            (LABEL_MEDIUM, TEXT_MEDIUM, 120),
            (LABEL_LARGE,  TEXT_LARGE,  180),
        ]

        print(f"\n{'═'*60}")
        print(f"  📊 BẢNG THỜI GIAN DỊCH VĂN BẢN")
        print(f"{'═'*60}")
        print(f"  {'Độ dài':<30} {'Thời gian':>10}")
        print(f"  {'─'*45}")

        for label, text, timeout in cases:
            print(f"  ⏳ Đang đo {label[:28]}...", end="", flush=True)
            r = perf_page.translate_text_timed(text, timeout=timeout)
            icon = "✅" if not r.error else "❌"
            print(f"\r  {icon} {label:<30} {r.elapsed_seconds:>8.3f}s")

        print(f"{'═'*60}\n")


# ======================================================================
# PDF
# ======================================================================

class TestPDFTranslationTiming:
    def test_translate_pdf_1page(self, perf_page):
        print(f"\n{SEP}\n  📄 Dịch PDF 1 trang\n{SEP}")
        r = perf_page.translate_pdf_timed(PDF_1P)
        print(f"  ✅ Hoàn thành : {r.elapsed_seconds:.3f}s")
        if r.error:
            print(f"  ❌ Lỗi : {r.error}")
            pytest.fail(r.error)    
    def test_translate_pdf_2pages(self, perf_page):   
        print(f"\n{SEP}\n  📄 Dịch PDF 2 trang\n{SEP}")
        r = perf_page.translate_pdf_timed(PDF_2P)
        print(f"  ✅ Hoàn thành : {r.elapsed_seconds:.3f}s")
        if r.error:
            print(f"  ❌ Lỗi : {r.error}")
            pytest.fail(r.error)
    def test_translate_pdf_5pages(self, perf_page):
        print(f"\n{SEP}\n  📄 Dịch PDF 5 trang\n{SEP}")
        r = perf_page.translate_pdf_timed(PDF_5P)
        print(f"  ✅ Hoàn thành : {r.elapsed_seconds:.3f}s")
        if r.error:
            print(f"  ❌ Lỗi : {r.error}")
            pytest.fail(r.error)

    def test_translate_pdf_10pages(self, perf_page):
        print(f"\n{SEP}\n  📄 Dịch PDF 10 trang\n{SEP}")
        r = perf_page.translate_pdf_timed(PDF_10P)
        print(f"  ✅ Hoàn thành : {r.elapsed_seconds:.3f}s")
        if r.error:
            print(f"  ❌ Lỗi : {r.error}")
            pytest.fail(r.error)

    def test_translate_pdf_20pages(self, perf_page):
        print(f"\n{SEP}\n  📄 Dịch PDF 20 trang\n{SEP}")
        r = perf_page.translate_pdf_timed(PDF_20P, timeout=180)
        print(f"  ✅ Hoàn thành : {r.elapsed_seconds:.3f}s")
        if r.error:
            print(f"  ❌ Lỗi : {r.error}")
            pytest.fail(r.error)

    def test_pdf_timing_summary(self, perf_page):
        cases = [
            ("PDF  1 trang", PDF_1P,  60),
            ("PDF  2 trang", PDF_2P,  60),
            ("PDF  5 trang", PDF_5P,  60),
            ("PDF 10 trang", PDF_10P, 120),
            ("PDF 20 trang", PDF_20P, 180),
        ]

        print(f"\n{'═'*60}")
        print(f"  📊 BẢNG THỜI GIAN DỊCH PDF")
        print(f"{'═'*60}")
        print(f"  {'Tài liệu':<20} {'Thời gian':>10}")
        print(f"  {'─'*35}")

        for label, filename, timeout in cases:
            print(f"  ⏳ Đang đo {label}...", end="", flush=True)
            r = perf_page.translate_pdf_timed(filename, timeout=timeout)
            icon = "✅" if not r.error else "❌"
            print(f"\r  {icon} {label:<20} {r.elapsed_seconds:>8.3f}s")

        print(f"{'═'*60}\n")


# ======================================================================
# FULL REPORT
# ======================================================================

class TestFullTimingReport:

    def test_full_report(self, perf_page):
        text_cases = [
            (LABEL_SMALL_SMALLER,  TEXT_SMALL_SMALLER,  10),
            (LABEL_SMALL_SMALL,   TEXT_SMALL_SMALL,   20),
            (LABEL_SMALL,  TEXT_SMALL,  60),
            (LABEL_MEDIUM, TEXT_MEDIUM, 120),
            (LABEL_LARGE,  TEXT_LARGE,  180),
        ]
        pdf_cases = [
            ("PDF  1 trang", PDF_1P,  60),
            ("PDF  2 trang", PDF_2P,  60),
            ("PDF  5 trang", PDF_5P,  60),
            ("PDF 10 trang", PDF_10P, 120),
            ("PDF 20 trang", PDF_20P, 180),

        ]

        print(f"\n{'═'*60}")
        print(f"  ⏱  BÁO CÁO HIỆU NĂNG HỆ THỐNG")
        print(f"{'═'*60}")

        print(f"\n  [VĂN BẢN THÔ — tối đa 2000 ký tự]")
        print(f"  {'Độ dài':<32} {'Thời gian':>10}")
        print(f"  {'─'*45}")
        for label, text, timeout in text_cases:
            print(f"  ⏳ {label[:30]}...", end="", flush=True)
            r = perf_page.translate_text_timed(text, timeout=timeout)
            icon = "✅" if not r.error else "❌"
            print(f"\r  {icon} {label:<32} {r.elapsed_seconds:>8.3f}s")

        print(f"\n  [FILE PDF]")
        print(f"  {'Tài liệu':<20} {'Thời gian':>10}")
        print(f"  {'─'*35}")
        for label, filename, timeout in pdf_cases:
            print(f"  ⏳ {label}...", end="", flush=True)
            r = perf_page.translate_pdf_timed(filename, timeout=timeout)
            icon = "✅" if not r.error else "❌"
            print(f"\r  {icon} {label:<20} {r.elapsed_seconds:>8.3f}s")

        print(f"\n{'═'*60}\n")