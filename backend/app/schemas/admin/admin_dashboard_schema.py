"""
schemas/admin/admin_dashboard_schema.py
-----------------------------------------
Pydantic schemas cho Admin Dashboard.
Thiết kế khớp 1:1 với UI mockup.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# =========================================================
# 1. OVERVIEW CARDS — 4 thẻ tổng quan trên cùng
# =========================================================

class OverviewCard(BaseModel):
    """Một thẻ số liệu trong row tổng quan."""
    value: int | float
    change: float = Field(0, description="% thay đổi so với kỳ trước")
    change_label: str = Field("", description="Mô tả kỳ so sánh: 'so với hôm qua', 'so với tuần trước'")
    extra: Optional[str] = Field(None, description="Thông tin bổ sung, VD: 'avg ★ 4.3 / 5'")


class DashboardOverviewResponse(BaseModel):
    """4 thẻ tổng quan: tổng user, đăng ký mới, lượt dịch, đánh giá mới."""
    total_users: OverviewCard
    new_registrations: OverviewCard
    translations_today: OverviewCard
    new_feedbacks: OverviewCard


# =========================================================
# 2. BIỂU ĐỒ — Lượt dịch theo ngày (7 ngày) + theo giờ
# =========================================================

class DailyTranslationPoint(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    count: int


class HourlyTranslationPoint(BaseModel):
    hour: int = Field(..., ge=0, le=23, description="Giờ (0-23)")
    text_count: int = Field(0, description="Số lượt dịch text")
    file_count: int = Field(0, description="Số lượt dịch file")


class WeeklyChartResponse(BaseModel):
    """Dữ liệu biểu đồ 7 ngày qua."""
    data: List[DailyTranslationPoint]


class HourlyChartResponse(BaseModel):
    """Dữ liệu biểu đồ theo giờ hôm nay."""
    data: List[HourlyTranslationPoint]
    peak_morning: Optional[str] = Field(None, description="Giờ cao điểm sáng, VD: '8-10h'")
    peak_evening: Optional[str] = Field(None, description="Giờ cao điểm tối, VD: '20-22h'")


# =========================================================
# 3. PHÂN BỔ ĐÁNH GIÁ SAO
# =========================================================

class RatingDistributionResponse(BaseModel):
    total_feedbacks: int
    avg_rating: float
    distribution: Dict[int, int] = Field(
        ..., description="Key 1-5 (sao), value: số lượng"
    )


# =========================================================
# 4. CHIỀU DỊCH EN ↔ VI
# =========================================================

class DirectionStatsResponse(BaseModel):
    """Thống kê theo chiều dịch."""
    en_to_vi_count: int = 0
    vi_to_en_count: int = 0
    en_to_vi_pct: float = 0
    vi_to_en_pct: float = 0
    en_to_vi_avg_rating: Optional[float] = None
    vi_to_en_avg_rating: Optional[float] = None


# =========================================================
# 5. NGƯỜI DÙNG HOẠT ĐỘNG GẦN ĐÂY
# =========================================================

class RecentActiveUser(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    tier: str
    is_active: bool
    translation_count: int = Field(0, description="Số lượt dịch gần đây")
    last_active: Optional[str] = Field(None, description="'hôm nay', 'hôm qua', '2 ngày trước'")


# =========================================================
# 6. FEEDBACK GẦN ĐÂY
# =========================================================

class RecentFeedbackItem(BaseModel):
    id: uuid.UUID
    rating: int
    feedback_note: Optional[str] = None
    corrected_content: Optional[str] = None
    user_name: str
    direction: str = Field("", description="VD: 'EN→VI'")
    created_at: datetime
    time_ago: str = Field("", description="VD: '10 phút trước'")


# =========================================================
# 7. FULL DASHBOARD RESPONSE — Tất cả trong 1 request
# =========================================================

class FullDashboardResponse(BaseModel):
    """
    Response tổng hợp toàn bộ dashboard trong 1 API call.
    Frontend có thể gọi 1 lần duy nhất thay vì nhiều API.
    """
    overview: DashboardOverviewResponse
    weekly_chart: WeeklyChartResponse
    hourly_chart: HourlyChartResponse
    rating_distribution: RatingDistributionResponse
    direction_stats: DirectionStatsResponse
    recent_users: List[RecentActiveUser]
    recent_feedbacks: List[RecentFeedbackItem]


# =========================================================
# 8. SSE EVENT — Admin real-time notification
# =========================================================

class AdminSSEEvent(BaseModel):
    """Event push qua SSE cho admin dashboard."""
    event_type: str = Field(
        ..., description="Loại event: 'new_translation', 'new_feedback', 'new_user'"
    )
    message: str
    data: Optional[dict] = None
    timestamp: Optional[datetime] = None
