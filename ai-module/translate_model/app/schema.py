from pydantic import BaseModel, Field

class TranslateRequest(BaseModel):
    text: str = Field(..., description="Văn bản cần dịch (có thể chứa nhiều đoạn)")
    direction: str = Field(..., pattern="^(en-vi|vi-en)$", description="Chỉ nhận 'en-vi' hoặc 'vi-en'")

class TranslateResponse(BaseModel):
    translated_text: str