"""
api/admin/feedback_router.py
------------------------------
Router admin quản lý feedback.
Tất cả endpoint đều yêu cầu require_admin.
Không chứa logic — chỉ gọi AdminFeedbackService.
"""
from typing import Optional

from fastapi import APIRouter, Depends, status

from ...middleware.auth import require_admin
from ...schemas.admin.admin_feedback_schema import (
    FeedbackDeleteResponse,
    FeedbackDetailResponse,
    FeedbackListResponse,
    FeedbackStatsResponse,
)
from ...services.admin.admin_feedback_service import AdminFeedbackService, get_admin_feedback_service

router = APIRouter(prefix="/admin/feedback", tags=["Admin - Quản lý Feedback"])


@router.get("", response_model=FeedbackListResponse)
async def list_feedbacks(
    rating: Optional[int] = None,
    user_id: Optional[str] = None,
    translation_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    service: AdminFeedbackService = Depends(get_admin_feedback_service),
    _=Depends(require_admin),
):
    """
    Xem toàn bộ feedback trên hệ thống.
    Lọc theo: rating (1-5), user_id, translation_id.
    Phân trang qua limit + offset.
    """
    return await service.list_feedbacks(
        rating=rating,
        user_id=user_id,
        translation_id=translation_id,
        limit=limit,
        offset=offset,
    )


@router.get("/stats", response_model=FeedbackStatsResponse)
async def get_quality_stats(
    service: AdminFeedbackService = Depends(get_admin_feedback_service),
    _=Depends(require_admin),
):
    """
    Thống kê chất lượng bản dịch:
    - Điểm trung bình, phân bổ theo sao, số bản dịch có bản sửa tay.
    """
    return await service.get_quality_stats()


@router.get("/{feedback_id}", response_model=FeedbackDetailResponse)
async def get_feedback_detail(
    feedback_id: str,
    service: AdminFeedbackService = Depends(get_admin_feedback_service),
    _=Depends(require_admin),
):
    """Xem chi tiết một feedback kèm thông tin bản dịch gốc và người dùng."""
    return await service.get_feedback_detail(feedback_id)


@router.delete("/{feedback_id}", status_code=status.HTTP_200_OK, response_model=FeedbackDeleteResponse)
async def delete_feedback(
    feedback_id: str,
    service: AdminFeedbackService = Depends(get_admin_feedback_service),
    _=Depends(require_admin),
):
    """Xóa feedback vi phạm hoặc spam. Admin xóa được bất kỳ feedback nào."""
    return await service.delete_feedback(feedback_id)