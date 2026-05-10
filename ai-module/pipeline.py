"""
Main Pipeline for Document Translation

DocumentTranslationPipeline: Class chính orchestrate toàn bộ quy trình dịch.

Workflow:
    1. Đọc PDF input
    2. Trích xuất text & phân tích layout
    3. Dịch text bằng translator engine
    4. Bảo toàn formulas & formatting
    5. Xây dựng lại PDF output
    6. Lưu kết quả
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Import các modules
from config import ConfigManager
from document_parser import PDFExtractor, LayoutAnalyzer
from translation_engine import TranslatorFactory, BaseTranslator, AVAILABLE_SERVICES
from document_reconstructor import PDFBuilder, LayoutPreserver
from cache import TranslationCache

logger = logging.getLogger(__name__)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class DocumentTranslationPipeline:
    """
    Main pipeline cho dịch tài liệu.
    
    Ví dụ sử dụng:
        # Khởi tạo pipeline
        pipeline = DocumentTranslationPipeline(
            service="openai",
            lang_in="en",
            lang_out="vi",
            model="gpt-4",
            api_key="sk-..."
        )
        
        # Dịch PDF
        result = pipeline.translate(
            input_pdf="/path/to/input.pdf",
            output_pdf="/path/to/output.pdf"
        )
        
        # Kiểm tra kết quả
        print(result["status"])  # "success" hoặc "error"
        print(result["stats"])   # statisticsẩ
    
    Attributes:
        service: Tên dịch vụ (openai, deepl, ollama, azure)
        translator: Translator instance
        cache: TranslationCache instance
        layout_preserver: LayoutPreserver instance
    """
    
    def __init__(
        self,
        service: str = "openai",
        lang_in: str = "en",
        lang_out: str = "vi",
        model: str = "",
        use_cache: bool = True,
        **translator_kwargs: Any
    ):
        """
        Khởi tạo pipeline.
        
        Args:
            service: Dịch vụ dịch (openai, deepl, ollama, azure)
            lang_in: Ngôn ngữ nguồn
            lang_out: Ngôn ngữ đích
            model: Model dùng (tùy service)
            use_cache: Có dùng cache không
            **translator_kwargs: Tham số khác (api_key, endpoint, etc.)
        
        Ví dụ:
            pipeline = DocumentTranslationPipeline(
                service="openai",
                lang_in="en",
                lang_out="vi",
                model="gpt-4",
                api_key="sk-..."
            )
        """
        logger.info("🚀 Initializing DocumentTranslationPipeline")
        
        # Validate service
        if service not in AVAILABLE_SERVICES:
            available = ", ".join(AVAILABLE_SERVICES)
            raise ValueError(
                f"❌ Unknown service: {service}\n"
                f"Available: {available}"
            )
        
        self.service = service.lower()
        self.lang_in = lang_in
        self.lang_out = lang_out
        self.model = model
        self.use_cache = use_cache
        
        # Khởi tạo config manager
        self.config = ConfigManager.get_instance()
        
        # Khởi tạo translator
        try:
            self.translator = TranslatorFactory.create(
                service=self.service,
                lang_in=self.lang_in,
                lang_out=self.lang_out,
                model=self.model,
                **translator_kwargs
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize translator: {e}")
            raise
        
        # Khởi tạo cache
        cache_db_path = self.config.get(
            "cache.db_path",
            str(Path.home() / ".cache" / "hus-ai-translator" / "translations.db")
        )
        self.cache = TranslationCache(db_path=cache_db_path) if use_cache else None
        
        # Khởi tạo layout preserver
        self.layout_preserver = LayoutPreserver()
        
        # Thống kê
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_pages": 0,
            "total_text_chars": 0,
            "translated_chars": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        
        logger.info(
            f"✅ Pipeline initialized: "
            f"{self.service} ({self.lang_in} → {self.lang_out})"
        )
    
    def translate(
        self,
        input_pdf: str,
        output_pdf: str,
        batch_size: int = 1,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Dịch PDF file.
        
        Args:
            input_pdf: Đường dẫn PDF input
            output_pdf: Đường dẫn PDF output
            batch_size: Số text translation xử lý cùng lúc
            verbose: In chi tiết progress không
        
        Returns:
            Dict kết quả:
            {
                "status": "success" | "error",
                "input_pdf": str,
                "output_pdf": str,
                "stats": {...},
                "error": str (nếu failed),
            }
        """
        logger.info(f"📄 Starting translation: {Path(input_pdf).name}")
        
        self.stats["start_time"] = datetime.now().isoformat()
        
        try:
            # 1. Mở file PDF
            logger.info("📖 Opening PDF...")
            extractor = PDFExtractor(input_pdf)
            self.stats["total_pages"] = extractor.page_count
            
            # 2. Khởi tạo PDF builder
            builder = PDFBuilder(input_pdf)
            
            # 3. Process từng trang
            logger.info(f"🔄 Processing {extractor.page_count} pages...")
            
            for page_num in range(extractor.total_pages):
                if verbose:
                    print(f"Processing page {page_num + 1}/{extractor.page_count}...")
                
                # Trích xuất text
                text = extractor.extract_text(page_num)
                self.stats["total_text_chars"] += len(text)
                
                # Skip empty text
                if not text.strip():
                    logger.debug(f"⏭️ Skipping empty page {page_num}")
                    continue
                
                # Protect formulas
                protected_text, formula_map = self.layout_preserver.protect_formulas(text)
                
                # Dịch (với cache)
                translated_text = self._translate_with_cache(protected_text)
                
                # Restore formulas
                translated_text = self.layout_preserver.restore_formulas(
                    translated_text,
                    formula_map
                )
                
                self.stats["translated_chars"] += len(translated_text)
                
                # Thêm vào builder
                builder.add_translated_text(
                    page=page_num,
                    original_text=text,
                    translated_text=translated_text
                )
            
            # 4. Build output PDF
            logger.info("🏗️ Building output PDF...")
            success = builder.build(output_pdf)
            
            if not success:
                raise Exception("Failed to build PDF")
            
            # 5. Kết thúc
            self.stats["end_time"] = datetime.now().isoformat()
            
            # Tính toán thời gian
            duration = (
                datetime.fromisoformat(self.stats["end_time"]) -
                datetime.fromisoformat(self.stats["start_time"])
            ).total_seconds()
            
            logger.info(
                f"✅ Translation completed in {duration:.1f}s\n"
                f"   Pages: {self.stats['total_pages']}\n"
                f"   Text characters: {self.stats['total_text_chars']}\n"
                f"   Translated characters: {self.stats['translated_chars']}\n"
                f"   Cache hits: {self.stats['cache_hits']}\n"
                f"   Output: {output_pdf}"
            )
            
            return {
                "status": "success",
                "input_pdf": str(input_pdf),
                "output_pdf": str(output_pdf),
                "stats": self.stats.copy(),
                "duration_seconds": duration,
            }
        
        except Exception as e:
            logger.error(f"❌ Translation failed: {e}")
            
            return {
                "status": "error",
                "input_pdf": str(input_pdf),
                "output_pdf": str(output_pdf) if output_pdf else None,
                "error": str(e),
                "stats": self.stats.copy(),
            }
    
    def _translate_with_cache(self, text: str) -> str:
        """
        Dịch text với cache.
        
        Args:
            text: Text cần dịch
        
        Returns:
            Text đã dịch
        """
        # 1. Check cache
        if self.cache:
            cached = self.cache.get(
                translator_name=self.service,
                translator_params={
                    "model": self.model,
                    "lang_in": self.lang_in,
                    "lang_out": self.lang_out,
                },
                original_text=text
            )
            
            if cached:
                self.stats["cache_hits"] += 1
                logger.debug(f"📦 Cache hit: {len(text)} chars")
                return cached
            else:
                self.stats["cache_misses"] += 1
        
        # 2. Dịch
        try:
            translated = self.translator.translate(text)
        except Exception as e:
            logger.error(f"❌ Translation failed: {e}")
            # Fallback: trả về text gốc
            translated = text
        
        # 3. Cache result
        if self.cache and translated != text:
            self.cache.set(
                translator_name=self.service,
                translator_params={
                    "model": self.model,
                    "lang_in": self.lang_in,
                    "lang_out": self.lang_out,
                },
                original_text=text,
                translated_text=translated
            )
        
        return translated
    
    def translate_text(self, text: str) -> str:
        """
        Dịch một đoạn text đơn giản (không qua PDF).
        
        Args:
            text: Text cần dịch
        
        Returns:
            Text đã dịch
        """
        return self._translate_with_cache(text)
    
    def get_status(self) -> Dict[str, Any]:
        """Lấy trạng thái pipeline."""
        return {
            "service": self.service,
            "model": self.model,
            "lang_in": self.lang_in,
            "lang_out": self.lang_out,
            "cache_enabled": self.use_cache,
            "stats": self.stats.copy(),
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Lấy thống kê cache."""
        if not self.cache:
            return {"cache_enabled": False}
        
        return self.cache.get_stats()
    
    def clear_cache(self) -> bool:
        """Xóa cache."""
        if not self.cache:
            return False
        
        return self.cache.clear()
    
    def __repr__(self) -> str:
        return (
            f"DocumentTranslationPipeline("
            f"service={self.service}, "
            f"lang_in={self.lang_in}, "
            f"lang_out={self.lang_out}, "
            f"model={self.model})"
        )
