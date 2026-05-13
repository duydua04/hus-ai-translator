"""
Translator Factory

Factory pattern để tạo translators dựa trên service name.
Giúp quản lý & tạo các translator instance một cách thuận tiện.
"""

import logging
from typing import Optional, Dict, Any

from .base_translator import BaseTranslator
from .concrete_translators import TRANSLATORS_MAP

logger = logging.getLogger(__name__)

# Danh sách các services có sẵn
AVAILABLE_SERVICES = list(TRANSLATORS_MAP.keys())


class TranslatorFactory:
    """
    Factory để tạo translators.
    
    Ví dụ:
        # Tạo OpenAI translator
        translator = TranslatorFactory.create(
            service="openai",
            lang_in="en",
            lang_out="vi",
            model="gpt-4"
        )
        
        # Dịch
        result = translator.translate("Hello, how are you?")
    """
    
    @staticmethod
    def create(
        service: str,
        lang_in: str = "en",
        lang_out: str = "vi",
        model: str = "",
        **kwargs: Any
    ) -> BaseTranslator:
        """
        Tạo một translator instance.
        
        Args:
            service: Tên service ("openai", "deepl", "ollama", "azure")
            lang_in: Ngôn ngữ nguồn (ví dụ: "en", "english")
            lang_out: Ngôn ngữ đích (ví dụ: "vi", "vietnamese")
            model: Model cụ thể (tùy service)
            **kwargs: Các tham số khác (api_key, endpoint, etc.)
        
        Returns:
            BaseTranslator instance
        
        Raises:
            ValueError: Nếu service không hỗ trợ
        
        Ví dụ:
            translator = TranslatorFactory.create(
                service="openai",
                lang_in="en",
                lang_out="vi",
                model="gpt-4",
                api_key="sk-..."
            )
        """
        
        service = service.lower().strip()
        
        # Kiểm tra service hỗ trợ
        if service not in TRANSLATORS_MAP:
            available = ", ".join(AVAILABLE_SERVICES)
            raise ValueError(
                f"❌ Unknown translator service: '{service}'\n"
                f"Available: {available}"
            )
        
        translator_class = TRANSLATORS_MAP[service]
        
        try:
            translator = translator_class(
                lang_in=lang_in,
                lang_out=lang_out,
                model=model,
                **kwargs
            )
            
            logger.info(
                f"✅ Created {service} translator: "
                f"{lang_in} → {lang_out}"
            )
            
            return translator
        
        except Exception as e:
            logger.error(
                f"❌ Failed to create translator {service}: {e}"
            )
            raise
    
    @staticmethod
    def get_available_services() -> list:
        """Lấy danh sách services có sẵn."""
        return AVAILABLE_SERVICES.copy()
    
    @staticmethod
    def get_translator_info(service: str) -> Dict[str, Any]:
        """
        Lấy thông tin về một translator.
        
        Args:
            service: Tên service
        
        Returns:
            Dictionary chứa thông tin
        """
        service = service.lower().strip()
        
        if service not in TRANSLATORS_MAP:
            return {"error": f"Unknown service: {service}"}
        
        translator_class = TRANSLATORS_MAP[service]
        
        return {
            "name": translator_class.name,
            "class": translator_class.__name__,
            "description": translator_class.__doc__,
        }
    
    @staticmethod
    def list_services() -> str:
        """Hiển thị danh sách các services."""
        info = "🌐 Available Translation Services:\n"
        
        for service in AVAILABLE_SERVICES:
            info_dict = TranslatorFactory.get_translator_info(service)
            name = info_dict.get("name", service)
            info += f"\n  • {name.upper()}: {info_dict.get('class', '')}\n"
        
        return info


# Convenience function
def create_translator(
    service: str,
    lang_in: str = "en",
    lang_out: str = "vi",
    model: str = "",
    **kwargs: Any
) -> BaseTranslator:
    """Shortcut để tạo translator."""
    return TranslatorFactory.create(
        service=service,
        lang_in=lang_in,
        lang_out=lang_out,
        model=model,
        **kwargs
    )
