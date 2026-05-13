"""
Configuration Management Module

Quản lý toàn bộ cấu hình cho AI module:
- API keys & credentials
- Translator settings
- Cache configuration
- Paths & temporary directories
"""

from .config_manager import ConfigManager

__all__ = ["ConfigManager"]
