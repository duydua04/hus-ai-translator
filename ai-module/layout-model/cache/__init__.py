"""
Cache Module

Caching layer để tối ưu hiệu năng:
- translation_cache.py: SQLite-based translation cache

Export:
    - TranslationCache: Cache translations
"""

from .translation_cache import TranslationCache

__all__ = ["TranslationCache"]
