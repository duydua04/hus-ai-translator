# HUS AI Translator - AI Module

Modul AI cho dịch tài liệu học thuật (PDF, sách, bài báo khoa học) **với khả năng giữ nguyên định dạng layout, công thức toán học, và cấu trúc tài liệu**.

## Mục tiêu

- **Dịch máy chất lượng cao** cho tài liệu học thuật
- **Bảo toàn layout & formatting** (margins, fonts, styles)
- **Giữ nguyên công thức toán** (LaTeX, MathML)
- **Hỗ trợ nhiều dịch vụ** (OpenAI, DeepL, Ollama, Azure, v.v.)
- **Caching thông minh** để tối ưu hiệu năng
- **API modularity** - dễ mở rộng & tích hợp

---

## Cấu Trúc Thư Mục

```
ai-module/
├── __init__.py                          # Export chính
├── requirements.txt                     # Dependencies
├── README.md                           # Tài liệu này
│
├── config/
│   ├── __init__.py
│   └── config_manager.py               # Quản lý cấu hình (singleton + thread-safe)
│
├── document_parser/
│   ├── __init__.py
│   ├── pdf_extractor.py                # Trích xuất text/metadata từ PDF
│   └── layout_analyzer.py              # Phân tích layout (ONNX model)
│
├── translation_engine/
│   ├── __init__.py
│   ├── base_translator.py              # Abstract base class
│   ├── concrete_translators.py         # OpenAI, DeepL, Ollama, Azure
│   └── translator_factory.py           # Factory pattern
│
├── document_reconstructor/
│   ├── __init__.py
│   ├── pdf_builder.py                  # Xây dựng PDF output
│   └── layout_preserver.py             # Bảo toàn formatting
│
├── cache/
│   ├── __init__.py
│   └── translation_cache.py            # SQLite cache
│
└── pipeline.py                         # Main wrapper class (entry point)
```

---

## Quick Start

### **Bước 1: Cài Đặt Dependencies**

```bash
# Vao thu muc ai-module
cd "d:\HUS\18. Data Mining\hus-ai-translator\ai-module"

# Cach 1: Cai toan bo (neu mang nhanh)
pip install -r requirements.txt

# Cach 2: Neu timeout, dung mirror Tsinghua (nhanh hon)
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=1000 -r requirements.txt

# Cach 3: Cai package chinh (minimal)
pip install googletrans==4.0.0 requests tenacity peewee numpy
```

**Kiem tra cai dat:**
```bash
python -c "from ai_module.pipeline import DocumentTranslationPipeline; print('Cai dat thanh cong!')"
```

---

### **Bước 2: Chọn Dịch Vụ & Cài API Keys**

#### **Option A: Dùng Google Translate (Miễn phí, không cần API)**

Google Translate là lựa chọn tốt nhất - miễn phí, không cần API key, hỗ trợ 100+ ngôn ngữ!

```bash
# Không cần setup thêm, google-translate đã cài
python -c "from pipeline import DocumentTranslationPipeline; p = DocumentTranslationPipeline(service='google'); print(p.translate_text('Hello'))"
```

#### **Option B: Dùng OpenAI (Chất lượng cao, có phí)**

```bash
# Set environment variable (Windows PowerShell)
$env:OPENAI_API_KEY = "sk-your-key-here"

# Hoac Windows CMD
set OPENAI_API_KEY=sk-your-key-here
```

#### **Option C: Dùng DeepL (Nhanh, có phí)**

```bash
$env:DEEPL_API_KEY = "your-deepl-key"
```

#### **Option D: Dùng Ollama (Local, Miễn phí)**

```bash
# 1. Download Ollama tu https://ollama.ai
# 2. Cai dat & chay
ollama serve

# 3. Trong terminal khac, pull model
ollama pull llama2
# hoac model khac
ollama pull mistral
ollama pull neural-chat
```

---

### **Bước 3: Chạy Ví Dụ Đầu Tiên**

#### **Ví Dụ 1: Dịch Text Đơn Giản (Không cần API key - Chỉ dùng Google Translate)**

```python
from ai_module.pipeline import DocumentTranslationPipeline

# Dung Google Translate (free, không cần API key)
pipeline = DocumentTranslationPipeline(
    service="google",
    lang_in="en",
    lang_out="vi"
)

# Dich
text = "Machine learning is transforming industries"
result = pipeline.translate_text(text)
print(f"Original:   {text}")
print(f"Translated: {result}")

# Output:
# Original:   Machine learning is transforming industries
# Translated: Hoc may dang bien doi cac nganh cong nghiep
```

**Hoặc dùng OpenAI:**

```python
pipeline = DocumentTranslationPipeline(
    service="openai",
    lang_in="en",
    lang_out="vi",
    model="gpt-3.5-turbo"
    # API key se lay tu OPENAI_API_KEY env var
)

result = pipeline.translate_text("Hello world")
print(result)  # "Xin chao the gioi"
```

---

#### **Ví Dụ 2: Dịch File PDF**

```python
from ai_module.pipeline import DocumentTranslationPipeline

# Khoi tao pipeline voi Google Translate (free)
pipeline = DocumentTranslationPipeline(
    service="google",
    lang_in="en",
    lang_out="vi"
)

# Dich PDF
result = pipeline.translate(
    input_pdf="document_english.pdf",      # File input
    output_pdf="document_vietnamese.pdf"   # File output
)

# Kiem tra ket qua
if result["status"] == "success":
    print("Dich thanh cong!")
    print(f"   Pages: {result['stats']['total_pages']}")
    print(f"   Duration: {result['duration_seconds']:.1f}s")
    print(f"   Output: {result['output_pdf']}")
else:
    print(f"Loi: {result['error']}")
```

---

#### **Ví Dụ 3: Chuyển Đổi Giữa Các Dịch Vụ**

```python
from ai_module.translation_engine import TranslatorFactory

# Danh sach dich vu kha dung
services = TranslatorFactory.get_available_services()
print(f"Available services: {services}")
# Available services: ['openai', 'deepl', 'ollama', 'google', 'azure']

# Dich bang nhieu dich vu
text = "Artificial intelligence"
services_to_try = ["google", "deepl", "ollama"]

for service in services_to_try:
    try:
        translator = TranslatorFactory.create(
            service=service,
            lang_in="en",
            lang_out="vi"
        )
        result = translator.translate(text)
        print(f"[{service.upper()}]: {result}")
    except Exception as e:
        print(f"[{service.upper()}]: Loi {e}")
```

---

#### **Ví Dụ 4: Sử Dụng Cache (Tối ưu Hiệu Năng)**

```python
from ai_module.pipeline import DocumentTranslationPipeline

# Voi cache bat (default)
pipeline = DocumentTranslationPipeline(
    service="google",
    use_cache=True  # Bat cache
)

# Lan dau - dich & luu vao cache
result1 = pipeline.translate_text("Hello")
print(f"First call: {result1}")

# Lan thu 2 - lay tu cache (nhanh hon rat nhieu!)
result2 = pipeline.translate_text("Hello")
print(f"Second call (from cache): {result2}")

# Xem cache stats
stats = pipeline.get_cache_stats()
print(f"Cache stats: {stats}")
# Output:
# Cache stats: {'total_cached': 1, 'by_translator': {'google': 1}}

# Xoa cache neu can
pipeline.clear_cache()
```

---

#### **Ví Dụ 5: Bảo Vệ Công Thức Toán**

```python
from ai_module.document_reconstructor import LayoutPreserver

preserver = LayoutPreserver()

# Text co cong thuc
text = "The Einstein equation $E=mc^2$ is famous and Newton's law $F=ma$ too."

print(f"Original:      {text}")

# Step 1: Bao ve cong thuc
protected_text, formula_map = preserver.protect_formulas(text)
print(f"Protected:     {protected_text}")
print(f"Formula map:   {formula_map}")

# Step 2: Dich (cac cong thuc khong bi dich)
translated_protected = protected_text.replace("Einstein", "Tinh ien-xtai-no").replace("Newton", "Niu-ton")
print(f"Translated:    {translated_protected}")

# Step 3: Restore cong thuc
restored = preserver.restore_formulas(translated_protected, formula_map)
print(f"Restored:      {restored}")
```

---

### **Bước 4: Chạy Toàn Bộ Ví Dụ**

File `example_usage.py` chua 8 vi du hoan chinh:

```bash
python example_usage.py
```

---

### **Bước 5: Debug & Xem Logs**

```python
import logging

# Bat debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Sau do chay code cua ban
from ai_module.pipeline import DocumentTranslationPipeline

pipeline = DocumentTranslationPipeline(service="google")
result = pipeline.translate_text("Hello")

# Se in chi tiet logs:
# 2024-01-15 10:30:45 - ai_module.pipeline - INFO - Initializing...
# 2024-01-15 10:30:46 - ai_module.pipeline - INFO - Pipeline initialized
# ...
```

---

### **Bước 6: Cấu Hình (Nếu Cần)**

```python
from ai_module.config import ConfigManager

# Lay cau hinh
config = ConfigManager.get_instance()

# Set API key
ConfigManager.set("translators.openai.api_key", "sk-your-key")
ConfigManager.set("translators.deepl.api_key", "your-deepl-key")
ConfigManager.set("translation.default_service", "google")

# Xem tat ca config
print(ConfigManager.get_all())
```

---

### **Sheet - Cac lenh dung hay**

#### **Dich text voi Google Translate (free):**
```python
from ai_module.pipeline import DocumentTranslationPipeline
pipeline = DocumentTranslationPipeline(service="google")
print(pipeline.translate_text("Hello"))
```

#### **Dich PDF voi Google Translate:**
```python
from ai_module.pipeline import DocumentTranslationPipeline
pipeline = DocumentTranslationPipeline(service="google")
result = pipeline.translate("input.pdf", "output.pdf")
print(result)
```

#### **Kiem tra service kha dung:**
```python
from ai_module.translation_engine import TranslatorFactory
print(TranslatorFactory.get_available_services())
```

#### **Xem cache stats:**
```python
pipeline = DocumentTranslationPipeline(service="google")
print(pipeline.get_cache_stats())
```

---

### **Cac loi thuong gap & Cach khac phuc**

| Loi | Nguyen Nhan | Cach Sua |
|-----|-----------|---------|
| `ModuleNotFoundError: No module named 'googletrans'` | Package chua cai | `pip install googletrans==4.0.0` |
| `ModuleNotFoundError: No module named 'openai'` | Package chua cai | `pip install openai` |
| `Failed to connect to Ollama` | Ollama chua chay | `ollama serve` |
| `OPENAI_API_KEY not found` | API key chua set | `$env:OPENAI_API_KEY = "sk-..."` |
| `TimeoutError` | Network cham | `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ...` |
| `ConnectivityError` | Khong co internet (DeepL, OpenAI) | Dung Google Translate (local) |

---

## Cấu Hình

Cấu hình lưu tại `~/.config/hus-ai-translator/config.json`:

```json
{
    "translators": {
        "openai": {
            "api_key": "",
            "model": "gpt-4"
        },
        "deepl": {
            "api_key": ""
        },
        "ollama": {
            "base_url": "http://localhost:11434"
        },
        "azure": {
            "api_key": "",
            "endpoint": ""
        }
    },
    "cache": {
        "enabled": true,
        "db_path": "~/.cache/hus-ai-translator/translations.db"
    },
    "translation": {
        "default_service": "openai",
        "default_lang_in": "en",
        "default_lang_out": "vi"
    }
}
```

### **Đặt API Keys**

**Cách 1: Environment Variables**
```bash
export OPENAI_API_KEY="sk-..."
export DEEPL_API_KEY="..."
export AZURE_TRANSLATOR_KEY="..."
export OLLAMA_BASE_URL="http://localhost:11434"
```

**Cách 2: Directly in Code**
```python
pipeline = DocumentTranslationPipeline(
    service="openai",
    api_key="sk-..."  # Explicit
)
```

---

## Chi Tiết Modules

### **ConfigManager** (`config/config_manager.py`)
Singleton pattern, thread-safe. Quản lý toàn bộ cấu hình.

```python
from ai_module.config import ConfigManager

# Lấy cấu hình
api_key = ConfigManager.get("translators.openai.api_key")

# Đặt cấu hình
ConfigManager.set("translators.openai.api_key", "sk-...")

# Lấy tất cả
all_config = ConfigManager.get_all()
```

### **TranslatorFactory** (`translation_engine/translator_factory.py`)
Factory pattern để tạo translators.

```python
from ai_module.translation_engine import TranslatorFactory

# Tạo translator
translator = TranslatorFactory.create(
    service="openai",
    lang_in="en",
    lang_out="vi",
    model="gpt-4",
    api_key="sk-..."
)

# Dịch
text = translator.translate("Hello world")

# Danh sách services
print(TranslatorFactory.get_available_services())
# ['openai', 'deepl', 'ollama', 'azure']
```

### **TranslationCache** (`cache/translation_cache.py`)
SQLite-based cache với Peewee ORM.

```python
from ai_module.cache import TranslationCache

cache = TranslationCache(db_path="~/.cache/translations.db")

# Lưu
cache.set(
    translator_name="openai",
    translator_params={"model": "gpt-4"},
    original_text="Hello",
    translated_text="Xin chào"
)

# Lấy
result = cache.get("openai", {"model": "gpt-4"}, "Hello")
# result = "Xin chào"

# Thống kê
stats = cache.get_stats()
print(stats)
```

### **PDFExtractor** (`document_parser/pdf_extractor.py`)
Trích xuất text & metadata từ PDF.

```python
from ai_module.document_parser import PDFExtractor

extractor = PDFExtractor("/path/to/document.pdf")

# Thông tin chung
print(f"Pages: {extractor.page_count}")
print(f"Title: {extractor.title}")

# Trích xuất text
text = extractor.extract_text(page_number=0)

# Trích xuất tất cả
all_texts = extractor.extract_all_text()

# Metadata trang
metadata = extractor.get_page_metadata(0)
```

### **LayoutPreserver** (`document_reconstructor/layout_preserver.py`)
Bảo toàn formatting & công thức toán.

```python
from ai_module.document_reconstructor import LayoutPreserver

preserver = LayoutPreserver()

# Protect formulas
protected_text, formula_map = preserver.protect_formulas(
    "The equation $E=mc^2$ is important"
)
# protected_text = "The equation __FORMULA_0__ is important"
# formula_map = {"__FORMULA_0__": "$E=mc^2$"}

# Restore formulas
restored = preserver.restore_formulas(
    "Phương trình __FORMULA_0__ rất quan trọng",
    formula_map
)
# restored = "Phương trình $E=mc^2$ rất quan trọng"
```

---

## Translation Services

### **OpenAI** (gpt-4, gpt-3.5-turbo)
```python
pipeline = DocumentTranslationPipeline(
    service="openai",
    model="gpt-4",
    api_key="sk-..."
)
```

### **DeepL**
```python
pipeline = DocumentTranslationPipeline(
    service="deepl",
    api_key="..."
)
```

### **Ollama** (Local LLMs)
```python
# Yêu cầu: Ollama chạy ở http://localhost:11434
pipeline = DocumentTranslationPipeline(
    service="ollama",
    model="llama2"  # hoặc models khác
)
```

### **Azure Translator**
```python
pipeline = DocumentTranslationPipeline(
    service="azure",
    api_key="...",
    endpoint="https://api.cognitive.microsofttranslator.com/"
)
```

---

## Statistics & Monitoring

```python
# Lấy trạng thái
status = pipeline.get_status()
print(status)

# Lấy cache stats
cache_stats = pipeline.get_cache_stats()
print(cache_stats)
# {
#     "total_cached": 1234,
#     "by_translator": {"openai": 900, "deepl": 334}
# }

# Xóa cache
pipeline.clear_cache()
```

---

## Development & Extension

### **Thêm Translation Service Mới**

1. Tạo class trong `translation_engine/concrete_translators.py`:

```python
class NewServiceTranslator(BaseTranslator):
    name = "newservice"
    
    def translate(self, text: str) -> str:
        # Implement translation logic
        pass
```

2. Thêm vào `TRANSLATORS_MAP`:

```python
TRANSLATORS_MAP = {
    "openai": OpenAITranslator,
    "newservice": NewServiceTranslator,
    # ...
}
```

### **Tùy Chỉnh Layout Preservation**

Mở rộng `LayoutPreserver` trong `document_reconstructor/layout_preserver.py`:

```python
class CustomLayoutPreserver(LayoutPreserver):
    def preserve_formatting(self, original_text, translated_text):
        # Custom logic
        return enhanced_text
```

---

## Known Limitations

1. **Layout Preservation**: Hiện tại là placeholder, cần implement dùng pymupdf/pikepdf
2. **Image Extraction**: Chưa full implement
3. **Table Detection**: Sử dụng ONNX layout model (cần download model)
4. **Formula Recognition**: Hỗ trợ LaTeX basic, chưa MathML

---

## Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Sử dụng pipeline
pipeline = DocumentTranslationPipeline(...)
pipeline.translate("input.pdf", "output.pdf")

# Output:
# 2024-01-15 10:30:45 - ai_module.pipeline - INFO - Initializing DocumentTranslationPipeline
# 2024-01-15 10:30:46 - ai_module.pipeline - INFO - Pipeline initialized: openai (en → vi)
# ...
```

---

## Dependencies

Core dependencies (từ `requirements.txt`):

- `pymupdf<1.25.3` - PDF reading
- `pdfminer-six==20250416` - PDF parsing
- `pikepdf` - PDF manipulation
- `onnx`, `onnxruntime` - Layout analysis
- `opencv-python-headless` - Image processing
- `openai>=1.0.0`, `deepl`, `ollama`, `azure-ai-translation-text` - Translation APIs
- `peewee>=3.17.8` - SQLite caching
- `babeldoc` - Document utilities
- `tenacity` - Retry logic
- `numpy`, `tqdm` - Utils

---

## Contributing

Nếu bạn muốn thêm features hoặc cải thiện:

1. Mở rộng các classes cơ sở
2. Thêm tests
3. Commit changes

---

## License

MIT License - xem file LICENSE

---

## Support

Nếu có vấn đề:

1. Kiểm tra file config (`~/.config/hus-ai-translator/config.json`)
2. Kiểm tra API keys & credentials
3. Xem logs (enable DEBUG logging)
4. Kiểm tra network connection (nếu dùng online services)

---

## Examples

Xem thêm file `example_usage.py` để có các ví dụ chi tiết.
