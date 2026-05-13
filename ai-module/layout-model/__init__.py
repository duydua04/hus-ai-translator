"""
HUS AI Translator - Document Translation AI Module

Module chính để dịch tài liệu học thuật (PDF, sách, bài báo) với khả năng:
- Giữ nguyên định dạng layout & cấu trúc
- Dịch công thức toán & bảng biểu
- Hỗ trợ nhiều ngôn ngữ & dịch vụ
- Caching & tối ưu hiệu năng

Cấu trúc:
    - document_parser/: Trích xuất & phân tích tài liệu
    - translation_engine/: Các engine dịch (OpenAI, DeepL, Ollama, etc.)
    - document_reconstructor/: Xây dựng lại tài liệu đã dịch
    - cache/: Caching layer
    - config/: Configuration management
"""

__version__ = "0.1.0"
__author__ = "HUS AI Team"
__license__ = "MIT"

from .pipeline import DocumentTranslationPipeline

__all__ = [
    "DocumentTranslationPipeline",
]
