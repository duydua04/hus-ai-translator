"""
schemas/user/translation_schema.py
------------------------------------
Schemas dành riêng cho tính năng dịch thuật của user.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator


class TranslateTextRequest(BaseModel):
    source_lang_id: uuid.UUID
    target_lang_id: uuid.UUID
    input_content: str
    llm_model: Optional[str] = "gpt-4o"

    @field_validator("input_content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nội dung dịch không được để trống")
        if len(v) > 10000:
            raise ValueError("Nội dung quá dài, tối đa 10.000 ký tự")
        return v


class TranslateDocumentRequest(BaseModel):
    source_lang_id: uuid.UUID
    target_lang_id: uuid.UUID
    input_file_id: uuid.UUID
    llm_model: Optional[str] = "gpt-4o"


class TranslationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    source_lang_id: uuid.UUID
    target_lang_id: uuid.UUID
    type: str
    input_content: Optional[str]
    translated_content: Optional[str]
    input_file_id: Optional[uuid.UUID]
    result_file_id: Optional[uuid.UUID]
    llm_model: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TranslationListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[TranslationResponse]