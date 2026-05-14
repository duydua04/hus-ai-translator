"""
schemas/user/feedback_schema.py
---------------------------------
Pydantic schemas cho tính năng đánh giá bản dịch (TranslationFeedback).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# =========================================================
# REQUEST SCHEMAS
# =========================================================

class FeedbackCreateRequest(BaseModel):
    """Tạo đánh giá mới cho một bản dịch."""
    translation_id: uuid.UUID = Field(..., description="ID bản dịch cần đánh giá")
    rating: int = Field(..., ge=1, le=5, description="Điểm đánh giá từ 1 đến 5 sao")
    corrected_content: Optional[str] = Field(
        None,
        max_length=50000,
        description="Bản dịch người dùng tự sửa lại (nếu có)"
    )
    feedback_note: Optional[str] = Field(
        None,
        max_length=1000,
        description="Ghi chú bổ sung về chất lượng bản dịch"
    )

    @field_validator("corrected_content")
    @classmethod
    def corrected_content_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Nội dung sửa không được để trống nếu đã gửi")
        return v


class FeedbackUpdateRequest(BaseModel):
    """Cập nhật đánh giá đã gửi."""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Điểm đánh giá mới")
    corrected_content: Optional[str] = Field(
        None,
        max_length=50000,
        description="Bản dịch sửa lại"
    )
    feedback_note: Optional[str] = Field(
        None,
        max_length=1000,
        description="Ghi chú bổ sung"
    )


# =========================================================
# RESPONSE SCHEMAS
# =========================================================

class FeedbackResponse(BaseModel):
    """Response cho một đánh giá."""
    id: uuid.UUID
    translation_id: uuid.UUID
    user_id: uuid.UUID
    rating: int
    corrected_content: Optional[str]
    feedback_note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackListResponse(BaseModel):
    """Response phân trang cho danh sách đánh giá."""
    total: int
    limit: int
    offset: int
    data: List[FeedbackResponse]
