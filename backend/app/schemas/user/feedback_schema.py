"""
schemas/user/feedback_schema.py
---------------------------------
Schemas dành riêng cho tính năng đánh giá bản dịch của user.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class FeedbackCreateRequest(BaseModel):
    translation_id: uuid.UUID
    rating: int
    corrected_content: Optional[str] = None
    feedback_note: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Điểm đánh giá phải từ 1 đến 5 sao")
        return v


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    translation_id: uuid.UUID
    user_id: uuid.UUID
    rating: int
    corrected_content: Optional[str]
    feedback_note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}