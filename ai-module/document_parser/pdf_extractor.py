"""
PDF Extractor

Trích xuất text, metadata, và layout information từ PDF files.

Sử dụng:
    - pymupdf (fitz): Đọc PDF
    - pdfminer: Parsing chi tiết
    - pikepdf: Manipulate PDF
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Trích xuất text & metadata từ PDF files.
    
    Ví dụ:
        extractor = PDFExtractor("/path/to/document.pdf")
        
        # Lấy thông tin chung
        print(f"Pages: {extractor.page_count}")
        print(f"Title: {extractor.title}")
        
        # Trích xuất text từ trang đầu
        text = extractor.extract_text(page_number=0)
        
        # Trích xuất từ tất cả trang
        all_texts = extractor.extract_all_text()
    """
    
    def __init__(self, pdf_path: str):
        """
        Khởi tạo extractor.
        
        Args:
            pdf_path: Đường dẫn đến PDF file
        
        Raises:
            FileNotFoundError: Nếu file không tồn tại
        """
        self.pdf_path = Path(pdf_path)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        try:
            import pymupdf
            self.doc = pymupdf.open(str(self.pdf_path))
            logger.info(f"✅ Opened PDF: {self.pdf_path.name} ({self.page_count} pages)")
        except ImportError:
            logger.error("❌ pymupdf not installed. Install with: pip install pymupdf")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to open PDF: {e}")
            raise
    
    @property
    def page_count(self) -> int:
        """Số trang trong PDF."""
        return len(self.doc)
    
    @property
    def title(self) -> str:
        """Tiêu đề tài liệu (nếu có)."""
        try:
            metadata = self.doc.metadata
            return metadata.get("title", "") if metadata else ""
        except:
            return ""
    
    @property
    def author(self) -> str:
        """Tác giả tài liệu (nếu có)."""
        try:
            metadata = self.doc.metadata
            return metadata.get("author", "") if metadata else ""
        except:
            return ""
    
    def extract_text(self, page_number: int) -> str:
        """
        Trích xuất text từ một trang.
        
        Args:
            page_number: Số trang (0-indexed)
        
        Returns:
            Text từ trang
        """
        if page_number < 0 or page_number >= self.page_count:
            raise IndexError(f"Invalid page number: {page_number}")
        
        try:
            page = self.doc[page_number]
            text = page.get_text()
            logger.debug(f"✅ Extracted text from page {page_number} ({len(text)} chars)")
            return text
        except Exception as e:
            logger.error(f"❌ Failed to extract text from page {page_number}: {e}")
            return ""
    
    def extract_all_text(self) -> List[str]:
        """
        Trích xuất text từ tất cả trang.
        
        Returns:
            Danh sách texts, mỗi phần tử là text từ một trang
        """
        texts = []
        for page_num in range(self.page_count):
            text = self.extract_text(page_num)
            texts.append(text)
        
        logger.info(f"✅ Extracted text from all {self.page_count} pages")
        return texts
    
    def extract_images(self, page_number: int, output_dir: Optional[str] = None) -> List[str]:
        """
        Trích xuất images từ một trang.
        
        Args:
            page_number: Số trang (0-indexed)
            output_dir: Thư mục output (nếu None, trả về in-memory)
        
        Returns:
            Danh sách đường dẫn hoặc data images
        """
        # Placeholder - cần implement
        logger.warning("⚠️ Image extraction not yet implemented")
        return []
    
    def get_page_metadata(self, page_number: int) -> Dict[str, Any]:
        """
        Lấy metadata của một trang.
        
        Args:
            page_number: Số trang
        
        Returns:
            Dictionary chứa metadata
        """
        if page_number < 0 or page_number >= self.page_count:
            raise IndexError(f"Invalid page number: {page_number}")
        
        try:
            page = self.doc[page_number]
            return {
                "page_number": page_number,
                "width": page.rect.width,
                "height": page.rect.height,
                "rotation": page.rotation,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get page metadata: {e}")
            return {}
    
    def close(self) -> None:
        """Đóng PDF document."""
        if hasattr(self, "doc"):
            self.doc.close()
            logger.info("✅ PDF closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __del__(self):
        try:
            self.close()
        except:
            pass
