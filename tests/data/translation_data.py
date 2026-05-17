"""
Test data cho chức năng Dịch văn bản – Text Mode.
"""

from pages.home_page import HomePage

# ── shorthand ─────────────────────────────────────────────────────────────────
EN = HomePage.LANG_EN
VI = HomePage.LANG_VI

# ── văn bản mẫu hợp lệ ───────────────────────────────────────────────────────
SAMPLES = {
    "short_vi": {
        "text":   "Giải tích hàm số",
        "source": VI,
        "target": EN,
        "desc":   "Văn bản ngắn tiếng Việt → tiếng Anh",
    },
    "short_en": {
        "text":   "Mathematical analysis",
        "source": EN,
        "target": VI,
        "desc":   "Văn bản ngắn tiếng Anh → tiếng Việt",
    },
    "with_latex_inline": {
        "text":   "Cho hàm số $f(x) = x^2 + 1$, tìm đạo hàm.",
        "source": VI,
        "target": EN,
        "desc":   "Văn bản có công thức LaTeX inline $...$",
    },
    "with_latex_display": {
        "text":   "Tích phân sau đây bằng bao nhiêu?\n$$\\int_0^1 x^2\\,dx$$",
        "source": VI,
        "target": EN,
        "desc":   "Văn bản có công thức LaTeX display $$...$$",
    },
    "medium_vi": {
        "text": (
            "Trong toán học, giải tích là một nhánh nghiên cứu về giới hạn, "
            "đạo hàm, tích phân và chuỗi vô hạn. Giải tích được phát triển "
            "độc lập bởi Isaac Newton và Gottfried Wilhelm Leibniz vào thế kỷ 17."
        ),
        "source": VI,
        "target": EN,
        "desc":   "Đoạn văn trung bình ~50 từ tiếng Việt",
    },
}

# ── boundary ──────────────────────────────────────────────────────────────────
BOUNDARY = {
    "exactly_2000": {
        "text":   "a" * 2000,
        "desc":   "Đúng 2000 ký tự – giới hạn tối đa",
        "source": VI,
        "target": EN,
    },
    "over_2000": {
        "text":   "a" * 2001,
        "desc":   "2001 ký tự – vượt giới hạn",
        "source": VI,
        "target": EN,
    },
    "single_char": {
        "text":   "A",
        "desc":   "1 ký tự – giá trị biên tối thiểu",
        "source": EN,
        "target": VI,
    },
}

# ── negative ──────────────────────────────────────────────────────────────────
NEGATIVE = {
    "empty_string": {
        "text":   "",
        "desc":   "Chuỗi rỗng – nút Dịch ngay không nên hoạt động",
        "source": VI,
        "target": EN,
    },
    "whitespace_only": {
        "text":   "     ",
        "desc":   "Chỉ khoảng trắng – hệ thống không nên dịch",
        "source": VI,
        "target": EN,
    },
}

# ── swap pairs ────────────────────────────────────────────────────────────────
SWAP_PAIRS = [
    {"source": VI, "target": EN, "desc": "VI→EN hoán thành EN→VI"},
    {"source": EN, "target": VI, "desc": "EN→VI hoán thành VI→EN"},
]