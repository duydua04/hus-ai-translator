"""
Translation Engine Module

Các translation engines & services:
- base_translator.py: Abstract base class cho translators
- concrete_translators.py: Implementations (OpenAI, DeepL, Ollama, etc.)
- translator_factory.py: Factory pattern để tạo translators

Export:
    - BaseTranslator: Abstract base
    - TranslatorFactory: Factory để chọn & tạo translators
    - AVAILABLE_SERVICES: Danh sách services hỗ trợ
"""

from .translator_factory import TranslatorFactory, AVAILABLE_SERVICES
from .base_translator import BaseTranslator

__all__ = [
    "BaseTranslator",
    "TranslatorFactory",
    "AVAILABLE_SERVICES",
]
