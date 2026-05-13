"""
PDF Builder

Xây dựng PDF từ translated content.

Phiên bản này dùng PyMuPDF để:
- Xóa vùng text gốc bằng redaction
- Chèn text đã dịch vào đúng vị trí bbox
- Giữ nguyên phần còn lại của PDF
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFBuilder:
    """
    Xây dựng PDF đã dịch từ translated content.
    
    Ví dụ:
        builder = PDFBuilder(original_pdf_path="/path/to/original.pdf")
        
        # Thêm translated text
        builder.add_translated_text(
            page=0,
            original_text="Hello",
            translated_text="Xin chào"
        )
        
        # Xây dựng PDF
        builder.build("/path/to/output.pdf")
    """
    
    def __init__(self, original_pdf_path: str):
        """
        Khởi tạo builder.
        
        Args:
            original_pdf_path: Đường dẫn đến PDF gốc
        """
        self.original_pdf_path = Path(original_pdf_path)
        self.translations: List[Dict[str, Any]] = []
        
        if not self.original_pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {original_pdf_path}")
        
        logger.info(f"Initialized PDF builder for {self.original_pdf_path.name}")
    
    def add_translated_text(
        self,
        page: int,
        original_text: str,
        translated_text: str,
        bbox: Optional[List[float]] = None
    ) -> None:
        """
        Thêm translated text vào danh sách để xây dựng.
        
        Args:
            page: Số trang (0-indexed)
            original_text: Text gốc
            translated_text: Text dịch
            bbox: Bounding box [x0, y0, x1, y1] (nếu có)
        """
        self.translations.append({
            "page": page,
            "original_text": original_text,
            "translated_text": translated_text,
            "bbox": bbox,
        })
        
        logger.debug(
            f"Added translation for page {page}: "
            f"{len(original_text)} chars → {len(translated_text)} chars"
        )
    
    def build(self, output_path: str) -> bool:
        """
        Xây dựng PDF đã dịch.
        
        Args:
            output_path: Đường dẫn output PDF
        
        Returns:
            True nếu thành công
        
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import pymupdf

            doc = pymupdf.open(str(self.original_pdf_path))
            font_file = self._resolve_unicode_font()

            # Nhóm translations theo trang
            grouped: Dict[int, List[Dict[str, Any]]] = {}
            for item in self.translations:
                grouped.setdefault(item["page"], []).append(item)

            for page_num, items in grouped.items():
                if page_num < 0 or page_num >= len(doc):
                    continue

                page = doc[page_num]
                image_rects = self._collect_image_rects(page)

                # Che vùng text cũ bằng nền trắng, nhưng tránh đè lên vùng ảnh.
                for item in items:
                    bbox = item.get("bbox")
                    translated_text = item.get("translated_text", "").strip()

                    if not bbox or not translated_text:
                        continue

                    rect = pymupdf.Rect(bbox)
                    if not self._overlaps_any(rect, image_rects):
                        page.draw_rect(
                            rect,
                            color=None,
                            fill=1,
                            overlay=True,
                        )

                # Chèn text mới vào cùng vùng
                for item in items:
                    bbox = item.get("bbox")
                    translated_text = item.get("translated_text", "").strip()

                    if not bbox or not translated_text:
                        continue

                    rect = pymupdf.Rect(bbox)
                    font_size = 11
                    inserted = False

                    for _ in range(8):
                        result = page.insert_textbox(
                            rect,
                            translated_text,
                            fontsize=font_size,
                            fontname="translated_font",
                            fontfile=font_file,
                            color=(0, 0, 0),
                            align=0,
                        )
                        if result >= 0:
                            inserted = True
                            break
                        font_size -= 1

                    if not inserted:
                        page.insert_textbox(
                            rect,
                            translated_text,
                            fontsize=max(font_size, 6),
                            fontname="translated_font",
                            fontfile=font_file,
                            color=(0, 0, 0),
                            align=0,
                        )

            doc.save(str(output_path), deflate=True, garbage=4)
            doc.close()
            
            logger.info(f"Built PDF: {output_path}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to build PDF: {e}")
            return False

    def _resolve_unicode_font(self) -> Optional[str]:
        """Chọn một font có hỗ trợ Unicode để hiển thị tiếng Việt."""
        candidates = []

        if os.name == "nt":
            windows_font_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
            candidates.extend(
                [
                    windows_font_dir / "arial.ttf",
                    windows_font_dir / "calibri.ttf",
                    windows_font_dir / "times.ttf",
                    windows_font_dir / "segoeui.ttf",
                ]
            )
        else:
            candidates.extend(
                [
                    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
                    Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
                ]
            )

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        return None

    def _collect_image_rects(self, page) -> List["pymupdf.Rect"]:
        """Lấy danh sách bbox của ảnh trên một trang."""
        import pymupdf

        rects: List[pymupdf.Rect] = []
        try:
            blocks = page.get_text("dict").get("blocks", [])
            for block in blocks:
                if block.get("type") == 1 and "bbox" in block:
                    rects.append(pymupdf.Rect(block["bbox"]))
        except Exception as e:
            logger.debug(f"Failed to collect image rects: {e}")
        return rects

    def _overlaps_any(self, rect, rects) -> bool:
        """Kiểm tra một bbox có chồng lên bbox ảnh nào không."""
        for other in rects:
            if rect.intersects(other):
                return True
        return False
    
    def get_translation_summary(self) -> Dict[str, Any]:
        """Lấy tóm tắt các translations."""
        total_original_chars = sum(
            len(t["original_text"]) for t in self.translations
        )
        total_translated_chars = sum(
            len(t["translated_text"]) for t in self.translations
        )
        
        return {
            "total_translations": len(self.translations),
            "total_original_chars": total_original_chars,
            "total_translated_chars": total_translated_chars,
            "by_page": self._group_by_page(),
        }
    
    def _group_by_page(self) -> Dict[int, int]:
        """Nhóm translations theo trang."""
        by_page = {}
        for t in self.translations:
            page = t["page"]
            by_page[page] = by_page.get(page, 0) + 1
        return by_page
