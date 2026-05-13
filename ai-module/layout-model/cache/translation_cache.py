"""
Translation Cache

Cache SQLite-based để lưu trữ kết quả dịch.
Tối ưu hiệu năng, tránh dịch lại text đã dịch.

Sử dụng Peewee ORM để quản lý database.
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from peewee import Model, SqliteDatabase, CharField, TextField, SQL, AutoField
except ImportError:
    logger.warning("⚠️ Peewee not installed. Cache will be disabled.")
    Model = object
    SqliteDatabase = None


# Global database instance
db = SqliteDatabase(None) if SqliteDatabase else None


class TranslationCacheModel(Model):
    """ORM model cho cache table."""
    
    id = AutoField()
    translator_name = CharField(max_length=50)
    translator_params = TextField()  # JSON params
    original_text = TextField()
    translated_text = TextField()
    
    class Meta:
        database = db
        table_name = "translation_cache"
        constraints = [SQL("""
            UNIQUE (
                translator_name,
                translator_params,
                original_text
            ) ON CONFLICT REPLACE
        """)]


class TranslationCache:
    """
    Translation cache manager.
    
    Lưu trữ translations đã thực hiện để tránh dịch lại.
    
    Ví dụ:
        cache = TranslationCache(db_path="/path/to/cache.db")
        
        # Lưu translation
        cache.set("openai", {"model": "gpt-4"}, "Hello", "Xin chào")
        
        # Lấy từ cache
        result = cache.get("openai", {"model": "gpt-4"}, "Hello")
        # result = "Xin chào"
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Khởi tạo cache.
        
        Args:
            db_path: Đường dẫn đến cache database (SQLite)
                    Mặc định: ~/.cache/hus-ai-translator/translations.db
        """
        if db_path is None:
            db_path = str(
                Path.home() / ".cache" / "hus-ai-translator" / "translations.db"
            )
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Khởi tạo database."""
        global db
        
        if db is None or SqliteDatabase is None:
            logger.warning("❌ Peewee not available. Cache disabled.")
            return
        
        try:
            # Tạo thư mục nếu cần
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Khởi tạo database
            db.init(self.db_path)
            db.create_tables([TranslationCacheModel], safe=True)
            
            logger.info(f"✅ Cache initialized at {self.db_path}")
        
        except Exception as e:
            logger.error(f"❌ Failed to init cache: {e}")
    
    def set(
        self,
        translator_name: str,
        translator_params: dict,
        original_text: str,
        translated_text: str
    ) -> bool:
        """
        Lưu translation vào cache.
        
        Args:
            translator_name: Tên translator (ví dụ: "openai")
            translator_params: Tham số dịch (dict, sẽ JSON hóa)
            original_text: Text gốc
            translated_text: Text đã dịch
        
        Returns:
            True nếu thành công, False nếu failed
        """
        if db is None or SqliteDatabase is None:
            return False
        
        try:
            params_json = json.dumps(translator_params, sort_keys=True, ensure_ascii=False)
            
            TranslationCacheModel.create(
                translator_name=translator_name,
                translator_params=params_json,
                original_text=original_text,
                translated_text=translated_text,
            )
            
            logger.debug(
                f"✅ Cached: {translator_name} | {len(original_text)} chars"
            )
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to cache: {e}")
            return False
    
    def get(
        self,
        translator_name: str,
        translator_params: dict,
        original_text: str
    ) -> Optional[str]:
        """
        Lấy translation từ cache.
        
        Args:
            translator_name: Tên translator
            translator_params: Tham số dịch
            original_text: Text gốc
        
        Returns:
            Text đã dịch nếu found, None nếu not found
        """
        if db is None or SqliteDatabase is None:
            return None
        
        try:
            params_json = json.dumps(translator_params, sort_keys=True, ensure_ascii=False)
            
            result = TranslationCacheModel.get_or_none(
                TranslationCacheModel.translator_name == translator_name,
                TranslationCacheModel.translator_params == params_json,
                TranslationCacheModel.original_text == original_text,
            )
            
            if result:
                logger.debug(f"✅ Cache hit: {translator_name}")
                return result.translated_text
            else:
                logger.debug(f"❌ Cache miss: {translator_name}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Failed to get from cache: {e}")
            return None
    
    def clear(self) -> bool:
        """Xóa toàn bộ cache."""
        if db is None or SqliteDatabase is None:
            return False
        
        try:
            TranslationCacheModel.delete().execute()
            logger.info("✅ Cache cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to clear cache: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Lấy thống kê cache."""
        if db is None or SqliteDatabase is None:
            return {"error": "Cache disabled"}
        
        try:
            total = TranslationCacheModel.select().count()
            
            # Đếm theo translator
            stats = {}
            for row in TranslationCacheModel.select(
                TranslationCacheModel.translator_name
            ).distinct():
                count = TranslationCacheModel.select().where(
                    TranslationCacheModel.translator_name == row.translator_name
                ).count()
                stats[row.translator_name] = count
            
            return {
                "total_cached": total,
                "by_translator": stats,
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to get cache stats: {e}")
            return {"error": str(e)}
