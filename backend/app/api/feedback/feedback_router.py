"""
api/feedback/feedback_router.py
---------------------------------
Router đánh giá bản dịch.
Tất cả endpoint đều yêu cầu đăng nhập (require_user).
"""
from fastapi import APIRouter, Depends, status

from ...middleware.auth import require_user
from ...schemas.user.feedback_schema import FeedbackCreateRequest, FeedbackResponse
from ...services.user.feedback_service import FeedbackService, get_feedback_service

router = APIRouter(prefix="/feedback", tags=["Feedback - Đánh giá bản dịch"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    payload: FeedbackCreateRequest,
    info=Depends(require_user),
    service: FeedbackService = Depends(get_feedback_service),
):
    """
    Gửi đánh giá và / hoặc bản dịch sửa tay cho một bản dịch.
    Mỗi người dùng chỉ được đánh giá một lần cho mỗi bản dịch.
    """
    user_id = str(info["user"].id)
    return await service.create_feedback(user_id, payload)


@router.get("/my")
async def get_my_feedbacks(
    limit: int = 20,
    offset: int = 0,
    info=Depends(require_user),
    service: FeedbackService = Depends(get_feedback_service),
):
    """Xem danh sách tất cả đánh giá mà người dùng đã gửi."""
    user_id = str(info["user"].id)
    return await service.get_my_feedbacks(user_id, limit=limit, offset=offset)


@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    info=Depends(require_user),
    service: FeedbackService = Depends(get_feedback_service),
):
    """Xóa một đánh giá. Sau đó có thể gửi lại đánh giá mới cho cùng bản dịch đó."""
    user_id = str(info["user"].id)
    return await service.delete_feedback(user_id, feedback_id)