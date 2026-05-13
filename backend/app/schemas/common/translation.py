from pydantic import BaseModel, UUID4
from typing import Optional

class FileTranslationStartRequest(BaseModel):
    input_file_id: UUID4          # ID của file gốc trong bảng media_assets
    source_lang_id: UUID4         # ID của ngôn ngữ nguồn
    target_lang_id: UUID4         # ID của ngôn ngữ đích

class WebhookTranslationDone(BaseModel):
    translation_id: UUID4         # ID của bản dịch để Backend tìm và update
    client_id: str
    status: str                   # "success" hoặc "failed"
    result_path: Optional[str] = None  # Link MinIO của file sau khi dịch
    error_message: Optional[str] = None