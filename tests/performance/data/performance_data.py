# performance_data.py
# Văn bản mẫu tiếng Anh chuẩn cho performance test
# Mỗi sample được đếm từ chính xác

UNIT = (
    "The quick brown fox jumps over the lazy dog near the river bank. "
    "Artificial intelligence is transforming the way we live and work every day. "
    "Climate change poses significant challenges to ecosystems around the world. "
    "Researchers are developing new technologies to address global health problems. "
    "Education and innovation are key drivers of economic growth and development. "
)
# ≈ 50 words per unit


def build_text(target_chars: int) -> str:
    """Tạo text đúng số ký tự, không vượt quá giới hạn 2000."""
    repeated = (UNIT * (target_chars // len(UNIT) + 2)).strip()
    return repeated[:target_chars]
 


# 3 mức đo — đều dưới 2000 ký tự
TEXT_SMALL_SMALLER  = build_text(10)
TEXT_SMALL_SMALL   = build_text(100)   # ~40 từ   — rất nhanh
TEXT_SMALL  = build_text(400)   # ~80 từ   — nhanh
TEXT_MEDIUM = build_text(1000)  # ~200 từ  — trung bình
TEXT_LARGE  = build_text(1900)  # ~380 từ  — gần tối đa
 
# Tên hiển thị

LABEL_SMALL_SMALLER  = f"~10 ký tự  (~{len(TEXT_SMALL_SMALLER.split())} từ)"
LABEL_SMALL_SMALL   = f"~100 ký tự (~{len(TEXT_SMALL_SMALL.split())} từ)"
LABEL_SMALL  = f"~400 ký tự  (~{len(TEXT_SMALL.split())} từ)"
LABEL_MEDIUM = f"~1000 ký tự (~{len(TEXT_MEDIUM.split())} từ)"
LABEL_LARGE  = f"~1900 ký tự (~{len(TEXT_LARGE.split())} từ)"
 

# Thresholds (giây) — chỉnh theo SLA thực tế của hệ thống
THRESHOLD_TEXT_SMALL_SMALLER = 1.0
THRESHOLD_TEXT_SMALL_SMALL   = 2.0
THRESHOLD_TEXT_100  = 5.0
THRESHOLD_TEXT_500  = 15.0
THRESHOLD_TEXT_1000 = 30.0

THRESHOLD_PDF_1P = 10.0
THRESHOLD_PDF_2P = 15.0
THRESHOLD_PDF_5P  = 20.0
THRESHOLD_PDF_10P = 40.0
THRESHOLD_PDF_20P = 80.0

# File names — đặt PDF vào data/fixtures/
PDF_1P = "Easy-Test1-EV.pdf"
PDF_2P = "Easy-Test3-EV.pdf"
PDF_5P  = "Test-Large-5Page-EV.pdf"
PDF_10P = "Test-Large-10Page-EVpdf.pdf"
PDF_20P = "Test-Large-20Page-EVpdf.pdf"

# Language pair mặc định
DEFAULT_SOURCE_LANG = "en"
DEFAULT_TARGET_LANG = "vi"