"""
Example Usage of HUS AI Translator

Các ví dụ chi tiết cách sử dụng pipeline.
"""

import sys
import logging
from pathlib import Path

# Thêm ai-module vào path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline import DocumentTranslationPipeline
from translation_engine import TranslatorFactory, AVAILABLE_SERVICES
from config import ConfigManager
from cache import TranslationCache

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_1_basic_usage():
    """Example 1: Dich co ban voi Google Translate"""
    print("\n" + "="*70)
    print("Example 1: Basic Translation with Google Translate")
    print("="*70)
    
    try:
        # Khoi tao pipeline dung Google Translate
        pipeline = DocumentTranslationPipeline(
            service="google",
            lang_in="en",
            lang_out="vi",
        )
        
        # Dich mot doan text don gian
        text = "Artificial intelligence is transforming education."
        result = pipeline.translate_text(text)
        
        print(f"Original: {text}")
        print(f"Translated: {result}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_2_pdf_translation():
    """Example 2: Dich file PDF"""
    print("\n" + "="*70)
    print("Example 2: PDF Translation with Google Translate")
    print("="*70)
    
    try:
        # Khoi tao pipeline dung Google Translate
        pipeline = DocumentTranslationPipeline(
            service="google",
            lang_in="en",
            lang_out="vi",
        )
        
        # Paths
        input_pdf = "input_document.pdf"  # Thay doi duong dan
        output_pdf = "output_document_vi.pdf"
        
        # Kiem tra file ton tai
        if not Path(input_pdf).exists():
            print(f"Warning: File not found: {input_pdf}")
            print("Skipping PDF translation example...")
            return
        
        # Dich
        result = pipeline.translate(
            input_pdf=input_pdf,
            output_pdf=output_pdf,
            verbose=True
        )
        
        if result["status"] == "success":
            print("\nTranslation successful!")
            stats = result["stats"]
            print(f"  Pages: {stats['total_pages']}")
            print(f"  Original chars: {stats['total_text_chars']}")
            print(f"  Translated chars: {stats['translated_chars']}")
            print(f"  Duration: {result['duration_seconds']:.1f}s")
            print(f"  Output: {output_pdf}")
        else:
            print(f"\nTranslation failed: {result['error']}")
    
    except Exception as e:
        print(f"Error: {e}")


def example_3_different_services():
    """Example 3: Thu cac translation services khac nhau"""
    print("\n" + "="*70)
    print("Example 3: Using Different Translation Services")
    print("="*70)
    
    # Text can dich
    text = "Machine learning is a subset of artificial intelligence."
    
    # Cac services khac nhau
    services_config = [
        {
            "service": "google",
            "model": "",
            "kwargs": {}
        },
        {
            "service": "deepl",
            "model": "",
            "kwargs": {}
        },
        {
            "service": "ollama",
            "model": "llama2",
            "kwargs": {}
        },
    ]
    
    for config in services_config:
        service = config["service"]
        print(f"\nTranslating with {service.upper()}...")
        
        try:
            pipeline = DocumentTranslationPipeline(
                service=service,
                lang_in="en",
                lang_out="vi",
                model=config["model"],
                **config["kwargs"]
            )
            
            result = pipeline.translate_text(text)
            print(f"  Result: {result}")
        
        except Exception as e:
            print(f"  Error: {e}")


def example_4_cache_management():
    """Example 4: Quan ly cache"""
    print("\n" + "="*70)
    print("Example 4: Cache Management")
    print("="*70)
    
    # Khoi tao cache
    cache = TranslationCache()
    
    # Them vao cache
    print("\nCaching some translations...")
    
    translations = [
        ("hello", "xin chao"),
        ("good morning", "chao buoi sang"),
        ("thank you", "cam on"),
    ]
    
    for original, translated in translations:
        cache.set(
            translator_name="example",
            translator_params={"lang": "en-vi"},
            original_text=original,
            translated_text=translated
        )
        print(f"  Cached: '{original}' -> '{translated}'")
    
    # Lay tu cache
    print("\nRetrieving from cache...")
    
    for original, expected in translations:
        result = cache.get("example", {"lang": "en-vi"}, original)
        if result == expected:
            print(f"  Found: '{original}' -> '{result}'")
        else:
            print(f"  Not found: '{original}'")
    
    # Thong ke
    print("\nCache Statistics:")
    stats = cache.get_stats()
    print(f"  Total cached: {stats.get('total_cached', 0)}")
    print(f"  By translator: {stats.get('by_translator', {})}")
    
    # Xoa cache
    print("\nClearing cache...")
    cache.clear()
    print("  Cache cleared")


def example_5_translator_factory():
    """Example 5: Su dung TranslatorFactory"""
    print("\n" + "="*70)
    print("Example 5: TranslatorFactory Usage")
    print("="*70)
    
    # Danh sach services
    print("\nAvailable services:")
    for service in AVAILABLE_SERVICES:
        print(f"  - {service.upper()}")
    
    # Tao translators
    print("\nCreating translators...")
    
    text = "Hello, how are you?"
    
    for service in AVAILABLE_SERVICES:
        try:
            translator = TranslatorFactory.create(
                service=service,
                lang_in="en",
                lang_out="vi"
            )
            print(f"  Created {service}: {translator}")
        
        except Exception as e:
            print(f"  Failed to create {service}: {e}")


def example_6_config_management():
    """Example 6: Quan ly cau hinh"""
    print("\n" + "="*70)
    print("Example 6: Configuration Management")
    print("="*70)
    
    config = ConfigManager.get_instance()
    
    # Lay cau hinh
    print("\nReading configuration...")
    
    default_service = config.get("translation.default_service")
    default_lang_in = config.get("translation.default_lang_in")
    default_lang_out = config.get("translation.default_lang_out")
    
    print(f"  Default service: {default_service}")
    print(f"  Default lang_in: {default_lang_in}")
    print(f"  Default lang_out: {default_lang_out}")
    
    # Dat cau hinh
    print("\nUpdating configuration...")
    
    config.set("translation.default_service", "google")
    config.set("translation.default_lang_in", "zh")
    
    print("  Configuration updated")
    
    # Toan bo config
    print("\nFull configuration:")
    all_config = config.get_all()
    import json
    print(json.dumps(all_config, indent=2, ensure_ascii=False)[:500] + "...")


def example_7_batch_translation():
    """Example 7: Dich nhieu doan cung luc"""
    print("\n" + "="*70)
    print("Example 7: Batch Translation with Google Translate")
    print("="*70)
    
    try:
        pipeline = DocumentTranslationPipeline(
            service="google",
            lang_in="en",
            lang_out="vi",
            use_cache=True
        )
        
        # Danh sach texts
        texts = [
            "Python is a programming language.",
            "Deep learning is powerful.",
            "The model has high accuracy.",
            "Machine learning is important.",
            "Data science is the future.",
        ]
        
        print(f"\nTranslating {len(texts)} texts...")
        
        for i, text in enumerate(texts, 1):
            result = pipeline.translate_text(text)
            print(f"\n  {i}. EN: {text}")
            print(f"     VI: {result}")
        
        # Cache stats
        cache_stats = pipeline.get_cache_stats()
        print(f"\nCache stats:")
        print(f"  Total cached: {cache_stats.get('total_cached', 0)}")
    
    except Exception as e:
        print(f"Error: {e}")


def example_8_formula_protection():
    """Example 8: Bao ve cong thuc toan"""
    print("\n" + "="*70)
    print("Example 8: Formula Protection")
    print("="*70)
    
    from document_reconstructor import LayoutPreserver
    
    preserver = LayoutPreserver()
    
    # Text co cong thuc
    text = "The Einstein equation $E=mc^2$ and Newton's law $F=ma$ are fundamental."
    
    print(f"\nOriginal text:")
    print(f"  {text}")
    
    # Protect formulas
    protected, formula_map = preserver.protect_formulas(text)
    
    print(f"\nProtected text:")
    print(f"  {protected}")
    
    print(f"\nFormula map:")
    for placeholder, formula in formula_map.items():
        print(f"  {placeholder} -> {formula}")
    
    # Simulate translation
    translated_protected = protected.replace("Einstein", "Tinh ien-xtai-no").replace("Newton", "Niu-ton")
    
    print(f"\nSimulated translated (protected):")
    print(f"  {translated_protected}")
    
    # Restore formulas
    restored = preserver.restore_formulas(translated_protected, formula_map)
    
    print(f"\nRestored text:")
    print(f"  {restored}")


def main():
    """Run all examples"""
    print("\n" + "#"*70)
    print("HUS AI Translator - Usage Examples")
    print("#"*70)
    
    examples = [
        ("Basic Text Translation", example_1_basic_usage),
        ("PDF Translation", example_2_pdf_translation),
        ("Different Services", example_3_different_services),
        ("Cache Management", example_4_cache_management),
        ("TranslatorFactory", example_5_translator_factory),
        ("Configuration Management", example_6_config_management),
        ("Batch Translation", example_7_batch_translation),
        ("Formula Protection", example_8_formula_protection),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nNote: Some examples require API keys.")
    print("   Set them via environment variables or config file.")
    
    # Run all examples (co the comment out nhung cai khong can)
    # example_1_basic_usage()
    # example_2_pdf_translation()
    # example_3_different_services()
    # example_4_cache_management()
    # example_5_translator_factory()
    # example_6_config_management()
    # example_7_batch_translation()
    # example_8_formula_protection()
    
    # For now, run just a few examples
    print("\n" + "-"*70)
    print("Running selected examples...")
    print("-"*70)
    
    example_5_translator_factory()
    example_4_cache_management()
    example_6_config_management()
    example_8_formula_protection()
    
    print("\n" + "#"*70)
    print("Examples completed!")
    print("#"*70)


if __name__ == "__main__":
    main()
