# Đường dẫn: app/schemas/sse.py
from pydantic import BaseModel
from typing import Optional

class TranslationMessage(BaseModel):
    job_id: str
    status: str            # "processing", "completed", "failed"
    step: str              # VD: "Đang bóc tách Layout", "Đang dịch thuật"
    progress: int          # 0 đến 100
    result_url: Optional[str] = None   # Link tải file (chỉ có khi status="completed")
    error_detail: Optional[str] = None # Chi tiết lỗi (chỉ có khi status="failed")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "12345",
                "status": "processing",
                "step": "Đang nhận diện ký tự (OCR)...",
                "progress": 45
            }
        }