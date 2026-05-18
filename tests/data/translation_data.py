"""
data/translation_data.py
────────────────────────
Dữ liệu test cho luồng dịch văn bản (text translation).

UUID của ngôn ngữ phải khớp với giá trị <option value="..."> trong HTML.
Nếu backend trả về ID khác, cập nhật LANG_EN / LANG_VI tại đây.
"""

# ── Language option values ────────────────────────────────────────────────────
LANG_EN = "5baa6399-bb68-4ea1-adbf-9da0fd83180f"
LANG_VI = "46a5f84f-57f9-4636-a565-c19905f0b07c"

# ── Giới hạn ký tự ───────────────────────────────────────────────────────────
MAX_CHARS = 2000

# ── Dữ liệu dịch hợp lệ ─────────────────────────────────────────────────────
VALID_TRANSLATIONS = [
    {
        "id": "en_to_vi_short",
        "source": LANG_EN,
        "target": LANG_VI,
        "input": "Hello",
        "description": "Dịch từ ngắn EN → VI",
    },
    {
        "id": "vi_to_en_short",
        "source": LANG_VI,
        "target": LANG_EN,
        "input": "Xin chào",
        "description": "Dịch từ ngắn VI → EN",
    },
    {
        "id": "en_to_vi_sentence",
        "source": LANG_EN,
        "target": LANG_VI,
        "input": "Good morning, how are you today?",
        "description": "Dịch câu hoàn chỉnh EN → VI",
    },
    {
        "id": "vi_to_en_sentence",
        "source": LANG_VI,
        "target": LANG_EN,
        "input": "Chào buổi sáng, bạn có khỏe không?",
        "description": "Dịch câu hoàn chỉnh VI → EN",
    },
    {
        "id": "en_to_vi_paragraph",
        "source": LANG_EN,
        "target": LANG_VI,
        "input": (
            "Artificial intelligence is transforming the way we live and work. "
            "Machine learning models can now understand and generate human language "
            "with remarkable accuracy."
        ),
        "description": "Dịch đoạn văn EN → VI",
    },
]

# ── Văn bản dài (gần giới hạn) ───────────────────────────────────────────────
LONG_TEXT_EN = "This is a test sentence for performance evaluation. " * 38  # ~1976 ký tự
LONG_TEXT_VI = "Đây là câu kiểm tra hiệu năng của hệ thống dịch thuật. " * 34  # ~1938 ký tự

# ── Văn bản vượt giới hạn ────────────────────────────────────────────────────
OVER_LIMIT_TEXT = "A" * (MAX_CHARS + 1)

# ── Văn bản đặc biệt ─────────────────────────────────────────────────────────
SPECIAL_TEXTS = [
    {
        "id": "only_numbers",
        "input": "12345 67890",
        "description": "Chỉ có số",
    },
    {
        "id": "only_punctuation",
        "input": "!!! ??? ...",
        "description": "Chỉ có ký tự đặc biệt",
    },
    {
        "id": "mixed_language",
        "input": "Hello thế giới",
        "description": "Trộn lẫn ngôn ngữ",
    },
    {
        "id": "html_injection",
        "input": "<script>alert('xss')</script>",
        "description": "Văn bản chứa HTML/script tag",
    },
    {
        "id": "unicode_emoji",
        "input": "Hello 😊 Xin chào 🌍",
        "description": "Văn bản có emoji",
    },
]