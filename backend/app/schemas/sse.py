"""
schemas/sse.py
-----------------
Schema cho SSE (Server-Sent Events) messages.
Dùng cho endpoint test POST /send-translation/{client_id}.

Format này khớp với format thực tế mà Worker và Backend publish vào Redis Pub/Sub.
"""
from pydantic import BaseModel, Field
from typing import Optional


class TranslationMessage(BaseModel):
    """
    Schema chuẩn cho mọi SSE message trong flow dịch file.

    Các status hợp lệ:
      - "processing"  : Đang xử lý (progress 0-95)
      - "finalizing"  : Worker dịch xong, đang chờ Backend lưu DB (progress 98)
      - "completed"   : Backend đã lưu DB xong, FE có thể query (progress 100)
      - "failed"      : Lỗi xảy ra
      - "error"       : Lỗi ở phía Worker
    """
    status: str = Field(
        ...,
        description="Trạng thái: processing, finalizing, completed, failed, error",
        json_schema_extra={"example": "processing"},
    )
    progress: int = Field(
        ...,
        ge=0,
        le=100,
        description="Phần trăm tiến độ (0-100)",
        json_schema_extra={"example": 50},
    )
    message: str = Field(
        ...,
        description="Mô tả tiến độ hiện tại cho người dùng",
        json_schema_extra={"example": "Đang dịch trang 3/10..."},
    )
    translation_id: Optional[str] = Field(
        None,
        description="ID bản dịch (chỉ có trong completed/failed từ Backend)",
    )
    result_path: Optional[str] = Field(
        None,
        description="Đường dẫn file kết quả trên MinIO (chỉ có khi completed)",
    )