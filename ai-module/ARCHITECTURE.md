"""
ARCHITECTURE SUMMARY
Tóm tắt kiến trúc HUS AI Translator - AI Module

Ngày tạo: 2024-01-15
Phiên bản: 0.1.0
"""

# =============================================================================
# KIẾN TRÚC TỔNG QUAN
# =============================================================================

"""
Input PDF
    ↓
    ├─→ [PDF Extractor] ──→ Text + Metadata
    │
    ├─→ [Layout Analyzer] ──→ Layout Info (regions, bounding boxes)
    │
    ├─→ [Layout Preserver] ──→ Protect Formulas & Formatting
    │                          (formulas → placeholders)
    │
    ├─→ [Translation Engine] ──→ Translated Text
    │   (OpenAI/DeepL/Ollama/Azure)
    │
    ├─→ [Cache Manager] ──→ Store/Retrieve Translations
    │
    ├─→ [Layout Preserver] ──→ Restore Formulas & Formatting
    │
    └─→ [PDF Builder] ──→ Output PDF (with translations)
                          ↓
                      Output PDF
"""


# =============================================================================
# CẤU TRÚC THƯ MỤC CHI TIẾT
# =============================================================================

"""
ai-module/                           # Root
│
├── __init__.py                       # Module exports: DocumentTranslationPipeline
├── requirements.txt                  # Dependencies (all libraries needed)
├── README.md                         # Full documentation
├── example_usage.py                  # Usage examples (code)
│
├── config/                          
│   ├── __init__.py
│   └── config_manager.py             # Singleton config manager
│       • load/save config  (JSON file at ~/.config/hus-ai-translator/config.json)
│       • thread-safe with RLock
│       • support nested keys (e.g., "translators.openai.api_key")
│       • environment variable override
│
├── document_parser/                 
│   ├── __init__.py
│   ├── pdf_extractor.py              # Extract text/metadata from PDF
│       • open PDF using pymupdf
│       • extract text per page
│       • get metadata (title, author, etc.)
│       • extract images (placeholder)
│       • context manager support
│   │
│   └── layout_analyzer.py            # Analyze document layout (ONNX model)
│       • detect text regions, tables, figures
│       • bounding boxes for each element
│       • preserve margin info
│       • extract specialized elements (formulas, tables)
│
├── translation_engine/              
│   ├── __init__.py
│   ├── base_translator.py            # Abstract base class
│       • abstract method: translate(text)
│       • batch translate support
│       • language support checking
│       • language mapping (en → english)
│   │
│   ├── concrete_translators.py       # Actual implementations
│       • OpenAITranslator (uses OpenAI GPT API)
│       • DeepLTranslator (uses DeepL API)
│       • OllamaTranslator (uses Local Ollama)
│       • AzureTranslator (uses Microsoft Azure)
│       • All inherit from BaseTranslator
│   │
│   └── translator_factory.py         # Factory pattern
│       • TranslatorFactory.create(service, lang_in, lang_out, model, **kwargs)
│       • get available services
│       • get translator info
│       • list services
│
├── document_reconstructor/          
│   ├── __init__.py
│   ├── pdf_builder.py                # Build output PDF
│       • add_translated_text(page, original, translated, bbox)
│       • build(output_path) - creates final PDF
│       • get translation summary
│       • group by page
│   │
│   └── layout_preserver.py           # Preserve formatting
│       • analyze formatting (bold, italic, code, etc.)
│       • protect formulas ($ ... $ → __FORMULA_0__)
│       • restore formulas (vice versa)
│       • preserve_formatting() - apply styles
│       • extract formulas for protection
│
├── cache/                           
│   ├── __init__.py
│   └── translation_cache.py          # SQLite cache with Peewee ORM
│       • TranslationCacheModel (db schema)
│       • set(translator_name, params, original, translated)
│       • get(translator_name, params, original) → translated
│       • clear() - delete all cache
│       • get_stats() - cache statistics
│
└── pipeline.py                       # MAIN CLASS: DocumentTranslationPipeline
    documentTranslationPipeline()     • __init__ - setup all modules
                                      • translate(input_pdf, output_pdf) - main workflow
                                      • translate_text(text) - single text
                                      • _translate_with_cache() - internal helper
                                      • get_status() - pipeline status
                                      • get_cache_stats() - cache info
                                      • clear_cache() - clear cached translations
"""


# =============================================================================
# DÒNG CHẢY (WORKFLOW) CHI TIẾT
# =============================================================================

"""
MAIN WORKFLOW: translate(input_pdf, output_pdf)

1. INITIALIZATION
   ├─ Load ConfigManager (singleton)
   ├─ Create TranslatorFactory → Translator instance
   ├─ Initialize TranslationCache
   └─ Initialize LayoutPreserver

2. OPEN PDF
   ├─ PDFExtractor(input_pdf)
   └─ Read metadata (pages, title, author)

3. INITIALIZE OUTPUT
   └─ PDFBuilder(input_pdf)

4. PROCESS EACH PAGE
   For page = 0 to page_count:
   ├─ Extract text from page
   ├─ Protect formulas ($ ... $ → placeholders)
   ├─ Translate with cache:
   │  ├─ Check cache.get(service, params, text)
   │  ├─ If not found: translator.translate(text)
   │  └─ Store in cache
   ├─ Restore formulas (placeholders → $ ... $)
   ├─ Add to PDFBuilder
   └─ Update stats

5. BUILD OUTPUT
   ├─ PDFBuilder.build(output_pdf)
   └─ Save to disk

6. RETURN RESULT
   ├─ status: "success" | "error"
   ├─ stats: {pages, chars, duration, ...}
   └─ error (if failed)
"""


# =============================================================================
# DEPENDENCY GRAPH
# =============================================================================

"""
External Libraries (requirements.txt)
    │
    ├─ pymupdf <──────────────────── PDFExtractor
    ├─ pdfminer-six ──────────────── PDFExtractor
    ├─ pikepdf ───────────────────── PDFBuilder
    │
    ├─ onnx ──────────────────────── LayoutAnalyzer
    ├─ onnxruntime ───────────────── LayoutAnalyzer
    ├─ opencv-python-headless ────── LayoutAnalyzer
    │
    ├─ openai ───────────────────── OpenAITranslator
    ├─ deepl ────────────────────── DeepLTranslator
    ├─ ollama ───────────────────── OllamaTranslator
    ├─ azure-ai-translation-text ─── AzureTranslator
    ├─ requests ─────────────────── OllamaTranslator (HTTP)
    │
    ├─ peewee ───────────────────── TranslationCache
    ├─ sqlite3 (built-in) ───────── TranslationCache (via peewee)
    │
    ├─ tenacity ─────────────────── Retry logic (translators)
    ├─ tqdm ─────────────────────── Progress bars
    ├─ numpy ────────────────────── Numerical ops
    ├─ fontTools ────────────────── Font handling
    ├─ huggingface_hub ──────────── Model downloads
    └─ python-dotenv ────────────── .env support
"""


# =============================================================================
# KEY DESIGN PATTERNS
# =============================================================================

"""
1. SINGLETON PATTERN
   └─ ConfigManager
      • Single instance across application
      • Thread-safe with RLock
      • Shared configuration state

2. FACTORY PATTERN
   └─ TranslatorFactory
      • Create translator instances
      • Decouple from specific implementations
      • Easy to add new translators

3. ABSTRACT BASE CLASS (ABC)
   └─ BaseTranslator
      • Define interface for all translators
      • Enforce implementation of translate()
      • Common functionality (language mapping)

4. STRATEGY PATTERN
   └─ Different Translators
      • Each translator is a strategy
      • Swap at runtime via TranslatorFactory
      • Different implementations: OpenAI, DeepL, etc.

5. CONTEXT MANAGER
   └─ PDFExtractor
      • __enter__() / __exit__()
      • Automatic resource cleanup
      • with statement support

6. DECORATOR PATTERN (via Retry)
   └─ Tenacity @retry
      • Automatic retry on failure
      • Exponential backoff
      • Applied to translators
"""


# =============================================================================
# MODULE RESPONSIBILITIES
# =============================================================================

"""
config_manager.py
├─ Responsibility: Manage configuration
├─ Scope: Global (singleton)
├─ Key Methods: get(), set(), get_all()
└─ Thread-Safety: Yes (RLock)

pdf_extractor.py
├─ Responsibility: Extract text/metadata from PDF
├─ Scope: Per-file (instantiated per PDF)
├─ Key Methods: extract_text(), extract_all_text(), get_page_metadata()
└─ Thread-Safety: No

layout_analyzer.py
├─ Responsibility: Analyze document layout (ONNX model)
├─ Scope: Per-file
├─ Key Methods: analyze(), extract_text_regions(), extract_tables()
└─ Thread-Safety: No (ONNX sessions not thread-safe by default)

base_translator.py
├─ Responsibility: Define translator interface
├─ Scope: Abstract
├─ Key Methods: translate(), translate_batch()
└─ Thread-Safety: N/A (abstract)

concrete_translators.py
├─ Responsibility: Implement specific translation services
├─ Scope: Per instance (created by factory)
├─ Key Methods: translate()
└─ Thread-Safety: Depends on API (generally thread-safe)

translator_factory.py
├─ Responsibility: Create translator instances
├─ Scope: Utility (mostly static methods)
├─ Key Methods: create(), get_available_services()
└─ Thread-Safety: Yes (thread-safe factory)

pdf_builder.py
├─ Responsibility: Build output PDF from translations
├─ Scope: Per-file
├─ Key Methods: add_translated_text(), build()
└─ Thread-Safety: No

layout_preserver.py
├─ Responsibility: Preserve formatting & protect formulas
├─ Scope: Utility
├─ Key Methods: protect_formulas(), restore_formulas()
└─ Thread-Safety: Yes (stateless)

translation_cache.py
├─ Responsibility: Cache translations (SQLite)
├─ Scope: Global (shared cache)
├─ Key Methods: set(), get(), clear(), get_stats()
└─ Thread-Safety: Yes (SQLite is thread-safe)

pipeline.py
├─ Responsibility: Orchestrate entire workflow
├─ Scope: Per-task (new instance per translation)
├─ Key Methods: translate(), translate_text()
└─ Thread-Safety: No (stateful, not designed for multi-threading)
"""


# =============================================================================
# USAGE PATTERNS
# =============================================================================

"""
PATTERN 1: Simple PDF Translation
────────────────────────────────────────────────────────────────────
from ai_module.pipeline import DocumentTranslationPipeline

pipeline = DocumentTranslationPipeline(
    service="openai", 
    lang_in="en", 
    lang_out="vi"
)

result = pipeline.translate("input.pdf", "output.pdf")


PATTERN 2: With Custom Configuration
────────────────────────────────────────────────────────────────────
from ai_module.config import ConfigManager

ConfigManager.set("translators.openai.api_key", "sk-...")
# Then create pipeline


PATTERN 3: Multiple Translations (Batch)
────────────────────────────────────────────────────────────────────
from ai_module.translation_engine import TranslatorFactory

translator = TranslatorFactory.create("openai", "en", "vi")

for text in texts:
    result = translator.translate(text)
    print(result)


PATTERN 4: Cache Reuse
────────────────────────────────────────────────────────────────────
from ai_module.cache import TranslationCache

pipeline = DocumentTranslationPipeline(use_cache=True)

# First run - fills cache
pipeline.translate("file1.pdf", "file1_out.pdf")

# Second run - uses cache where possible
pipeline.translate("file2.pdf", "file2_out.pdf")


PATTERN 5: Custom Translator Implementation
────────────────────────────────────────────────────────────────────
from ai_module.translation_engine.base_translator import BaseTranslator

class CustomTranslator(BaseTranslator):
    name = "custom"
    
    def translate(self, text):
        # Your implementation
        return translated_text

# Register in TRANSLATORS_MAP
"""


# =============================================================================
# CONFIGURATION HIERARCHY
# =============================================================================

"""
Configuration Priority (highest to lowest):
    1. Runtime parameters (explicit keyword arguments)
       └─ pipeline = DocumentTranslationPipeline(api_key="sk-...")
    2. Environment variables
       └─ export OPENAI_API_KEY="sk-..."
    3. Config file
       └─ ~/.config/hus-ai-translator/config.json
    4. Default values (hardcoded in code)
       └─ model = "gpt-4"
"""


# =============================================================================
# SCALABILITY CONSIDERATIONS
# =============================================================================

"""
MULTI-THREADING
├─ ConfigManager: Thread-safe (RLock)
├─ TranslationCache: Thread-safe (SQLite)
├─ Translators: Depends on API (check docs)
├─ PDFExtractor: Not thread-safe per-instance
└─ PDFBuilder: Not thread-safe per-instance

OPTIMIZATION TIPS
├─ Reuse pipeline instances
├─ Use batch_size > 1 for translator.translate_batch()
├─ Enable cache for repeated texts
├─ Use faster models when possible (gpt-3.5-turbo vs gpt-4)
├─ Consider using Ollama locally for cost savings
└─ Profile with Python's cProfile module

MEMORY USAGE
├─ PDF in memory: ~50-500MB (depending on PDF size)
├─ Cache database: ~1-10MB per 10K translations
├─ Translator client: ~50MB (varies by service)
└─ ONNX model: ~500MB-2GB (layout analysis model)
"""


# =============================================================================
# ERROR HANDLING STRATEGY
# =============================================================================

"""
TRY-EXCEPT BLOCKS
├─ PDF opening: FileNotFoundError, Exception
├─ Translator creation: ValueError (unknown service)
├─ Translation call: Generic Exception (API errors)
├─ Cache operations: Exception → log, continue
└─ PDF building: Exception → return error status

GRACEFUL DEGRADATION
├─ If translator fails: Use fallback translator or return original text
├─ If cache fails: Continue without caching
├─ If layout analysis fails: Process as plain text
├─ If formula protection fails: Continue with text as-is

LOGGING LEVELS
├─ DEBUG: Detailed operations (cache hit/miss, API calls)
├─ INFO: Major steps (pipeline init, translation start/end)
├─ WARNING: Potential issues (API key not found, deprecated features)
└─ ERROR: Failures (translation failed, file not found)
"""


# =============================================================================
# NEXT STEPS FOR IMPLEMENTATION
# =============================================================================

"""
PHASE 1: Core (NOW)
├─ Pipeline structure
├─ Config management
├─ Translator factory
├─ Basic translators (OpenAI, DeepL)
├─ Cache layer
└─ PDF extractor (basic)

PHASE 2: Enhancement
├─ Full PDFMiner integration for better text extraction
├─ ONNX model integration for layout analysis
├─ PDF builder (pymupdf/pikepdf)
├─ Formula detection & proper preservation
├─ Image extraction
├─ Table extraction & handling
└─ More translator services (Google, Baidu, etc.)

PHASE 3: Production
├─ Unit tests (pytest)
├─ Integration tests
├─ Performance benchmarking
├─ Docker deployment
├─ API endpoint (Flask/FastAPI)
├─ Async support (asyncio)
├─ Distributed processing (Celery)
└─ Web UI (Gradio or custom)

PHASE 4: MLOps (Optional)
├─ Model monitoring
├─ Translation quality metrics (BLEU, BERTScore)
├─ Fine-tuning for domain-specific translations
├─ A/B testing for translators
└─ Analytics & reporting
"""


# =============================================================================
# FILE CHECKLIST - WHAT'S CREATED
# =============================================================================

"""
CREATED FILES:
├─ __init__.py
├─ requirements.txt
├─ README.md
├─ example_usage.py
├─ pipeline.py                       (Main class)
│
├─ config/
│   ├─ __init__.py
│   └─ config_manager.py
│
├─ document_parser/
│   ├─ __init__.py
│   ├─ pdf_extractor.py
│   └─ layout_analyzer.py
│
├─ translation_engine/
│   ├─ __init__.py
│   ├─ base_translator.py
│   ├─ concrete_translators.py
│   └─ translator_factory.py
│
├─ document_reconstructor/
│   ├─ __init__.py
│   ├─ pdf_builder.py
│   └─ layout_preserver.py
│
└─ cache/
    ├─ __init__.py
    └─ translation_cache.py

PLACEHOLDERS (Implement later):
├─ PDF Builder (full pymupdf/pikepdf integration)
├─ Layout Analyzer (ONNX model integration)
├─ Image extraction
├─ Table extraction
└─ Advanced formula preservation
"""


if __name__ == "__main__":
    print(__doc__)
