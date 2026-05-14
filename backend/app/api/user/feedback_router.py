"""
api/user/feedback_router.py
-----------------------------
Router đánh giá bản dịch.
Tất cả endpoint yêu cầu đăng nhập (require_user).

Quy tắc:
  - Chỉ đánh giá bản dịch đã hoàn thành (status = "success").
  - Mỗi user chỉ được 1 đánh giá / bản dịch.
"""
from fastapi import APIRouter, Depends, status

from ...middleware.auth import require_user
from ...schemas.user.feedback_schema import (
    FeedbackCreateRequest,
    FeedbackUpdateRequest,
    FeedbackResponse,
    FeedbackListResponse,
)
from ...services.user.feedback_service import FeedbackService, get_feedback_service

router = APIRouter(prefix="/api/user/feedbacks", tags=["User - Đánh giá bản dịch"])


# ---------------------------------------------------------
# 1. Tạo đánh giá
# ---------------------------------------------------------
@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    payload: FeedbackCreateRequest,
    auth_info: dict = Depends(require_user),
    service: FeedbackService = Depends(get_feedback_service),
):
    """
    Gửi đánh giá cho một bản dịch.
    - Bản dịch phải có status = "success".
    - Mỗi user chỉ được đánh giá một lần cho mỗi bản dịch.
    """
    user_id = str(auth_info["user"].id)
    return await service.create_feedback(user_id, payload)


# ---------------------------------------------------------
# 2. Danh sách đánh giá của tôi
# ---------------------------------------------------------
@router.get("", response_model=FeedbackListResponse)
async def get_my_feedbacks(
    limit: int = 20,
    offset: int = 0,
    auth_info: dict = Depends(require_user),
    service: FeedbackService = Depends(get_feedback_service),
):
    """Xem tất cả đánh giá đã gửi, phân trang, mới nhất lên đầu."""
    user_id = str(auth_info["user"].id)
    return await service.get_my_feedbacks(user_id, limit=limit, offset=offset)


# ---------------------------------------------------------
# 3. Xem đánh giá theo bản dịch
# ---------------------------------------------------------
@router.get(
    "/by-translation/{translation_id}",
    response_model=FeedbackResponse,
)
async def get_feedback_by_translation(
    translation_id: str,
    auth_info: dict = Depends(require_user),
    service: FeedbackService = Depends(get_feedback_service),
):
    """Xem đánh giá của tôi cho một bản dịch cụ thể. Trả 404 nếu chưa đánh giá."""
    user_id = str(auth_info["user"].id)
    return await service.get_feedback_by_translation(user_id, translation_id)


# ---------------------------------------------------------
# 4. Xem chi tiết đánh giá
# ---------------------------------------------------------
@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_detail(
    feedback_id: str,
    auth_info: dict = Depends(require_user),
    service: FeedbackService = Depends(get_feedback_service),
):
    """Xem chi tiết một đánh giá của tôi."""
    user_id = str(auth_info["user"].id)
    return await service.get_feedback_detail(user_id, feedback_id)


# ---------------------------------------------------------
# 5. Cập nhật đánh giá
# ---------------------------------------------------------
@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: str,
    payload: FeedbackUpdateRequest,
    auth_info: dict = Depends(require_user),
    service: FeedbackService = Depends(get_feedback_service),
):
    """Cập nhật đánh giá đã gửi. Chỉ chủ nhân mới được sửa."""
    user_id = str(auth_info["user"].id)
    return await service.update_feedback(user_id, feedback_id, payload)


# ---------------------------------------------------------
# 6. Xóa đánh giá
# ---------------------------------------------------------
@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    auth_info: dict = Depends(require_user),
    service: FeedbackService = Depends(get_feedback_service),
):
    """Xóa đánh giá. Sau đó có thể gửi lại đánh giá mới cho bản dịch đó."""
    user_id = str(auth_info["user"].id)
    return await service.delete_feedback(user_id, feedback_id)
