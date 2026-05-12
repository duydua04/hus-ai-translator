"""
Base Translator Class

Abstract base class cho tất cả translation engines.
Định nghĩa interface chung cho các translators.

Các translator cụ thể sẽ kế thừa từ class này.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class BaseTranslator(ABC):
    """
    Abstract base class cho translation engines.
    
    Các translator cụ thể (OpenAI, DeepL, Ollama, etc.) sẽ kế thừa class này
    và implement method translate().
    
    Attributes:
        name: Tên translator (ví dụ: "openai", "deepl")
        lang_in: Ngôn ngữ nguồn (ví dụ: "en", "zh")
        lang_out: Ngôn ngữ đích (ví dụ: "vi", "ja")
        model: Model sử dụng
        envs: Environment variables / credentials
    """
    
    # Các lớp con phải override
    name: str = "base"
    envs: Dict[str, str] = {}
    lang_map: Dict[str, str] = {}  # Map ngôn ngữ từ các định dạng khác nhau
    supported_lang_pairs: Dict[str, list] = {}  # Các cặp ngôn ngữ hỗ trợ
    
    def __init__(
        self,
        lang_in: str,
        lang_out: str,
        model: str = "",
        **kwargs: Any
    ):
        """
        Khởi tạo translator.
        
        Args:
            lang_in: Ngôn ngữ nguồn (ví dụ: "en", "english")
            lang_out: Ngôn ngữ đích (ví dụ: "vi", "vietnamese")
            model: Model cụ thể sử dụng
            **kwargs: Các tham số khác (api_key, endpoint, etc.)
        """
        # Chuẩn hóa mã ngôn ngữ
        self.lang_in = self.lang_map.get(lang_in.lower(), lang_in.lower())
        self.lang_out = self.lang_map.get(lang_out.lower(), lang_out.lower())
        self.model = model
        self.kwargs = kwargs
        
        # Khởi tạo credentials từ kwargs
        self._setup_credentials(**kwargs)
        
        logger.info(
            f"✅ Initialized {self.__class__.__name__} "
            f"({self.lang_in} → {self.lang_out}, model: {self.model})"
        )
    
    def _setup_credentials(self, **kwargs: Any) -> None:
        """
        Setup credentials từ kwargs hoặc environment variables.
        Các lớp con sẽ override method này.
        """
        pass
    
    @abstractmethod
    def translate(self, text: str) -> str:
        """
        Dịch text từ ngôn ngữ nguồn sang ngôn ngữ đích.
        
        Args:
            text: Text cần dịch (một câu hoặc đoạn ngắn)
        
        Returns:
            Text đã dịch
        
        Raises:
            Exception: Nếu dịch thất bại
        """
        pass
    
    def translate_batch(self, texts: list[str]) -> list[str]:
        """
        Dịch batch texts.
        
        Default implementation: dịch từng cái một.
        Các lớp con có thể override để batch processing tối ưu.
        
        Args:
            texts: Danh sách texts cần dịch
        
        Returns:
            Danh sách texts đã dịch
        """
        return [self.translate(text) for text in texts]
    
    def is_language_supported(self, lang_in: str, lang_out: str) -> bool:
        """
        Kiểm tra cặp ngôn ngữ có hỗ trợ không.
        
        Args:
            lang_in: Ngôn ngữ nguồn
            lang_out: Ngôn ngữ đích
        
        Returns:
            True nếu hỗ trợ, False nếu không
        """
        if not self.supported_lang_pairs:
            # Nếu không định nghĩa, assume tất cả supported
            return True
        
        lang_in = self.lang_map.get(lang_in.lower(), lang_in.lower())
        lang_out = self.lang_map.get(lang_out.lower(), lang_out.lower())
        
        return lang_in in self.supported_lang_pairs.get(lang_out, [])
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name}, "
            f"lang_in={self.lang_in}, "
            f"lang_out={self.lang_out}, "
            f"model={self.model})"
        )
