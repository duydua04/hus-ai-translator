"""
Configuration Manager

Quản lý cấu hình toàn bộ AI module (API keys, settings, paths).
Sử dụng singleton pattern & thread-safe.

Các cấu hình chính:
    - API Keys (OpenAI, DeepL, Azure, TencentCloud, etc.)
    - Cache settings
    - Model paths
    - Temporary directories
"""

import json
import logging
import os
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Singleton config manager với thread-safety.
    
    Lưu trữ cấu hình tại: ~/.config/hus-ai-translator/config.json
    """
    
    _instance: Optional["ConfigManager"] = None
    _lock = RLock()
    
    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        
        self._initialized = True
        self._config_path = (
            Path.home() / ".config" / "hus-ai-translator" / "config.json"
        )
        self._config_data: Dict[str, Any] = {}
        self._ensure_config_exists()
    
    @classmethod
    def get_instance(cls) -> "ConfigManager":
        """Lấy singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def _ensure_config_exists(self) -> None:
        """Đảm bảo config file tồn tại, nếu không thì tạo mặc định."""
        if not self._config_path.exists():
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            self._config_data = self._get_default_config()
            self._save_config()
            logger.info(f"✅ Created default config at {self._config_path}")
        else:
            self._load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Lấy cấu hình mặc định."""
        return {
            "translators": {
                "openai": {"api_key": "", "model": "gpt-4"},
                "deepl": {"api_key": ""},
                "azure": {"api_key": "", "endpoint": ""},
                "tencentcloud": {"secret_id": "", "secret_key": ""},
                "ollama": {"base_url": "http://localhost:11434"},
            },
            "cache": {
                "enabled": True,
                "db_path": str(Path.home() / ".cache" / "hus-ai-translator" / "translations.db"),
            },
            "models": {
                "layout_model_path": "",  # ONNX layout detection model
            },
            "translation": {
                "default_service": "openai",
                "default_lang_in": "en",
                "default_lang_out": "vi",
                "batch_size": 1,
            },
        }
    
    def _load_config(self) -> None:
        """Tải config từ file."""
        with self._lock:
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    self._config_data = json.load(f)
                logger.info(f"✅ Loaded config from {self._config_path}")
            except json.JSONDecodeError:
                logger.warning("⚠️ Config file corrupted, using defaults")
                self._config_data = self._get_default_config()
    
    def _save_config(self) -> None:
        """Lưu config vào file."""
        with self._lock:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._config_data, f, indent=4, ensure_ascii=False)
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Lấy cấu hình theo key (hỗ trợ nested, ví dụ: "translators.openai.api_key").
        
        Args:
            key: Config key, có thể nested với dấu "."
            default: Giá trị mặc định nếu key không tồn tại
        
        Returns:
            Giá trị cấu hình hoặc default
        """
        instance = cls.get_instance()
        
        # Hỗ trợ nested keys như "translators.openai.api_key"
        keys = key.split(".")
        value = instance._config_data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        # Từ environment variables (override config file)
        env_key = f"HUS_AI_{key.upper().replace('.', '_')}"
        if env_key in os.environ:
            return os.environ[env_key]
        
        return value
    
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """
        Đặt cấu hình theo key.
        
        Args:
            key: Config key, có thể nested (ví dụ: "translators.openai.api_key")
            value: Giá trị cần đặt
        """
        instance = cls.get_instance()
        
        keys = key.split(".")
        config = instance._config_data
        
        # Tạo nested dict nếu cần
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        instance._save_config()
    
    @classmethod
    def load_from_env(cls) -> None:
        """
        Tải cấu hình từ environment variables.
        Format: HUS_AI_TRANSLATORS_OPENAI_API_KEY = "..."
        """
        instance = cls.get_instance()
        
        # Đơn giản: chỉ load env vars nếu cần thiết
        logger.info("✅ Environment variables can override config values")
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Lấy toàn bộ config."""
        instance = cls.get_instance()
        return instance._config_data.copy()


# Convenience function
def get_config(key: str, default: Any = None) -> Any:
    """Shortcut để lấy config."""
    return ConfigManager.get(key, default)


def set_config(key: str, value: Any) -> None:
    """Shortcut để đặt config."""
    ConfigManager.set(key, value)
