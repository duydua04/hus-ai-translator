"""
Layout Preserver

Bảo toàn layout & formatting của tài liệu gốc khi dịch.

- Giữ nguyên vị trí text, images, tables
- Bảo toàn fonts, sizes, colors, styles
- Xử lý formulas & special characters
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class LayoutPreserver:
    """
    Helper class để bảo toàn layout khi dịch.
    
    Ví dụ:
        preserver = LayoutPreserver(
            original_layout_info={...}  # từ layout analyzer
        )
        
        # Transform text với formatting giữ nguyên
        formatted_text = preserver.preserve_formatting(
            original_text="Hello **bold** world",
            translated_text="Xin chào **đậm** thế giới"
        )
    """
    
    def __init__(self, original_layout_info: Optional[Dict[str, Any]] = None):
        """
        Khởi tạo preserver.
        
        Args:
            original_layout_info: Thông tin layout từ layout analyzer
        """
        self.original_layout = original_layout_info or {}
        self.formatting_rules: Dict[str, Any] = {}
    
    def analyze_formatting(self, original_text: str) -> Dict[str, Any]:
        """
        Phân tích formatting của text gốc.
        
        Args:
            original_text: Text gốc
        
        Returns:
            Dict chứa thông tin formatting:
            {
                "has_bold": bool,
                "has_italic": bool,
                "has_code": bool,
                "has_subscript": bool,
                "has_superscript": bool,
                "formula_count": int,
            }
        """
        return {
            "has_bold": "**" in original_text or "__" in original_text,
            "has_italic": "*" in original_text or "_" in original_text,
            "has_code": "`" in original_text,
            "has_subscript": "_" in original_text,  # Rough heuristic
            "has_superscript": "^" in original_text,
            "formula_count": original_text.count("$"),
        }
    
    def preserve_formatting(
        self,
        original_text: str,
        translated_text: str
    ) -> str:
        """
        Áp dụng formatting từ original sang translated text.
        
        Lưu ý: Đây là implementation đơn giản.
        Trong thực tế cần xử lý phức tạp hơn để bảo toàn:
        - Markdown formatting
        - LaTeX formulas
        - Special characters
        
        Args:
            original_text: Text gốc (có formatting)
            translated_text: Text dịch (cần thêm formatting)
        
        Returns:
            Text dịch với formatting preserve tốt nhất có thể
        """
        # Placeholder: hiện tại chỉ trả về text dịch as-is
        logger.warning("⚠️ Formatting preservation is simplified")
        
        return translated_text
    
    def extract_formulas(self, text: str) -> List[str]:
        """
        Trích xuất công thức toán (LaTeX format).
        
        Ví dụ: "The equation $E=mc^2$ is famous" → ["E=mc^2"]
        
        Args:
            text: Text có chứa formulas
        
        Returns:
            Danh sách formulas
        """
        formulas = []
        
        # Heuristic: tìm text giữa $ ... $
        parts = text.split("$")
        for i in range(1, len(parts), 2):
            if i < len(parts):
                formulas.append(parts[i])
        
        return formulas
    
    def protect_formulas(self, text: str) -> tuple[str, Dict[str, str]]:
        """
        Protect formulas bằng cách thay thế bằng placeholders.
        
        Phòng khi translator dịch công thức, ta có thể restore sau.
        
        Args:
            text: Text có chứa formulas
        
        Returns:
            (text_with_placeholders, formula_map)
        """
        formula_map = {}
        protected_text = text
        
        formulas = self.extract_formulas(text)
        
        for i, formula in enumerate(formulas):
            placeholder = f"__FORMULA_{i}__"
            protected_text = protected_text.replace(f"${formula}$", placeholder, 1)
            formula_map[placeholder] = f"${formula}$"
        
        logger.info(f"✅ Protected {len(formulas)} formulas")
        
        return protected_text, formula_map
    
    def restore_formulas(
        self,
        translated_text: str,
        formula_map: Dict[str, str]
    ) -> str:
        """
        Restore formulas từ placeholders.
        
        Args:
            translated_text: Text dịch với placeholders
            formula_map: Map placeholder → formula
        
        Returns:
            Text với formulas restored
        """
        restored_text = translated_text
        
        for placeholder, formula in formula_map.items():
            restored_text = restored_text.replace(placeholder, formula)
        
        logger.info(f"✅ Restored {len(formula_map)} formulas")
        
        return restored_text
    
    def preserve_special_chars(
        self,
        original_text: str,
        translated_text: str
    ) -> str:
        """
        Preserve đặc biệt characters (quotes, dashes, bullets, etc.).
        
        Placeholder - có thể implement pattern matching.
        """
        # Đơn giản: trả về translated text
        return translated_text
