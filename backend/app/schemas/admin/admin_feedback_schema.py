"""
schemas/admin/admin_feedback_schema.py
----------------------------------------
Pydantic schemas cho các response của admin_feedback_router.
Cấu trúc khớp chính xác với dict mà AdminFeedbackService trả về.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# SCHEMA CON — dùng lại trong nhiều response
# ---------------------------------------------------------------------------

class FeedbackItem(BaseModel):
    """Ánh xạ với _to_dict() trong AdminFeedbackService."""
    id: uuid.UUID
    translation_id: uuid.UUID
    user_id: uuid.UUID
    rating: int
    corrected_content: Optional[str] = None
    feedback_note: Optional[str] = None
    created_at: datetime


class TranslationSummary(BaseModel):
    """Thông tin bản dịch tóm tắt — dùng trong FeedbackDetailResponse."""
    id: Optional[uuid.UUID] = None
    type: Optional[str] = None
    input_content: Optional[str] = None
    translated_content: Optional[str] = None
    llm_model: Optional[str] = None
    status: Optional[str] = None


class UserSummary(BaseModel):
    """Thông tin user tóm tắt — dùng trong FeedbackDetailResponse."""
    id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    tier: Optional[str] = None


# ---------------------------------------------------------------------------
# RESPONSE SCHEMAS CHÍNH
# ---------------------------------------------------------------------------

class FeedbackListResponse(BaseModel):
    """Response của GET /admin/feedback — danh sách có phân trang."""
    total: int
    limit: int
    offset: int
    data: List[FeedbackItem]


class FeedbackDetailResponse(BaseModel):
    """Response của GET /admin/feedback/{id} — chi tiết kèm bản dịch và user."""
    feedback: FeedbackItem
    translation: TranslationSummary
    user: UserSummary


class RatingDistribution(BaseModel):
    """Phân bổ số lượng feedback theo từng mức sao."""
    star_1: int = 0
    star_2: int = 0
    star_3: int = 0
    star_4: int = 0
    star_5: int = 0

    @classmethod
    def from_dict(cls, d: Dict[str, int]) -> "RatingDistribution":
        return cls(
            star_1=d.get("1_star", 0),
            star_2=d.get("2_star", 0),
            star_3=d.get("3_star", 0),
            star_4=d.get("4_star", 0),
            star_5=d.get("5_star", 0),
        )


class FeedbackStatsResponse(BaseModel):
    """Response của GET /admin/feedback/stats — thống kê chất lượng."""
    llm_model: str
    total_feedbacks: int
    average_rating: float
    distribution: Dict[str, int]   # giữ nguyên key "1_star"..."5_star" từ service
    total_with_correction: int


class FeedbackDeleteResponse(BaseModel):
    """Response của DELETE /admin/feedback/{id}."""
    message: str