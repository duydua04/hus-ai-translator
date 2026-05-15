"""
services/user/feedback_service.py
-----------------------------------
Service xử lý đánh giá bản dịch.

Quy tắc nghiệp vụ:
  - Chỉ được đánh giá bản dịch đã hoàn thành (status = "success").
  - Bản dịch phải thuộc về chính người dùng đang đánh giá.
  - Mỗi người dùng chỉ được gửi một đánh giá cho mỗi bản dịch.
  - Người dùng có thể cập nhật hoặc xóa đánh giá đã gửi.
"""
from fastapi import HTTPException, status
from fastapi.params import Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...models.models import Translation, TranslationFeedback
from ...services.admin.admin_dashboard_service import AdminDashboardService
from ...schemas.user.feedback_schema import (
    FeedbackCreateRequest,
    FeedbackUpdateRequest,
    FeedbackResponse,
    FeedbackListResponse,
)


class FeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # 1. Tạo đánh giá
    # ------------------------------------------------------------------
    async def create_feedback(
        self, user_id: str, payload: FeedbackCreateRequest
    ) -> FeedbackResponse:
        """
        Tạo đánh giá cho một bản dịch.
        - Bản dịch phải tồn tại, thuộc user, và có status = "success".
        - Mỗi user chỉ được 1 feedback / translation.
        """
        # 1. Kiểm tra bản dịch tồn tại + thuộc user
        translation = await self._get_user_translation(user_id, str(payload.translation_id))

        # 2. Kiểm tra bản dịch đã hoàn thành
        if translation.status != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ có thể đánh giá bản dịch đã hoàn thành (status = success).",
            )

        # 3. Kiểm tra đã đánh giá chưa
        existing = await self.db.execute(
            select(TranslationFeedback).where(
                and_(
                    TranslationFeedback.translation_id == payload.translation_id,
                    TranslationFeedback.user_id == user_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bạn đã đánh giá bản dịch này rồi. Hãy cập nhật thay vì tạo mới.",
            )

        # 4. Tạo feedback
        new_feedback = TranslationFeedback(
            translation_id=payload.translation_id,
            user_id=user_id,
            rating=payload.rating,
            corrected_content=payload.corrected_content,
            feedback_note=payload.feedback_note,
        )
        self.db.add(new_feedback)
        await self.db.commit()
        await self.db.refresh(new_feedback)

        # Notify admin dashboard
        try:
            admin_svc = AdminDashboardService(self.db)
            await admin_svc.invalidate_on_feedback()
            await AdminDashboardService.notify_admin(
                event_type="new_feedback",
                message=f"Có đánh giá mới: {payload.rating}★",
                data={"feedback_id": str(new_feedback.id), "rating": payload.rating},
            )
        except Exception:
            pass

        return FeedbackResponse.model_validate(new_feedback)

    # ------------------------------------------------------------------
    # 2. Cập nhật đánh giá
    # ------------------------------------------------------------------
    async def update_feedback(
        self, user_id: str, feedback_id: str, payload: FeedbackUpdateRequest
    ) -> FeedbackResponse:
        """Cập nhật đánh giá đã gửi. Chỉ chủ nhân mới được sửa."""
        feedback = await self._get_own_feedback(user_id, feedback_id)

        # Cập nhật các trường được gửi lên (bỏ qua None)
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không có trường nào để cập nhật.",
            )

        for field, value in update_data.items():
            setattr(feedback, field, value)

        await self.db.commit()
        await self.db.refresh(feedback)

        return FeedbackResponse.model_validate(feedback)

    # ------------------------------------------------------------------
    # 3. Xóa đánh giá
    # ------------------------------------------------------------------
    async def delete_feedback(self, user_id: str, feedback_id: str) -> dict:
        """Xóa đánh giá. Sau đó user có thể gửi lại đánh giá mới."""
        feedback = await self._get_own_feedback(user_id, feedback_id)

        await self.db.delete(feedback)
        await self.db.commit()

        return {"success": True, "message": "Đã xóa đánh giá thành công."}

    # ------------------------------------------------------------------
    # 4. Xem chi tiết một đánh giá
    # ------------------------------------------------------------------
    async def get_feedback_detail(self, user_id: str, feedback_id: str) -> FeedbackResponse:
        """Xem chi tiết một đánh giá của chính user."""
        feedback = await self._get_own_feedback(user_id, feedback_id)
        return FeedbackResponse.model_validate(feedback)

    # ------------------------------------------------------------------
    # 5. Lấy đánh giá theo bản dịch
    # ------------------------------------------------------------------
    async def get_feedback_by_translation(
        self, user_id: str, translation_id: str
    ) -> FeedbackResponse:
        """
        Lấy đánh giá của user cho một bản dịch cụ thể.
        Trả 404 nếu chưa đánh giá.
        """
        # Kiểm tra bản dịch thuộc user
        await self._get_user_translation(user_id, translation_id)

        result = await self.db.execute(
            select(TranslationFeedback).where(
                and_(
                    TranslationFeedback.translation_id == translation_id,
                    TranslationFeedback.user_id == user_id,
                )
            )
        )
        feedback = result.scalar_one_or_none()
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bạn chưa đánh giá bản dịch này.",
            )
        return FeedbackResponse.model_validate(feedback)

    # ------------------------------------------------------------------
    # 6. Danh sách đánh giá của user (phân trang)
    # ------------------------------------------------------------------
    async def get_my_feedbacks(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> FeedbackListResponse:
        """Lấy tất cả đánh giá mà user đã gửi, mới nhất lên đầu."""
        # Đếm tổng
        count_result = await self.db.execute(
            select(func.count()).select_from(TranslationFeedback).where(
                TranslationFeedback.user_id == user_id
            )
        )
        total = count_result.scalar() or 0

        # Lấy danh sách
        result = await self.db.execute(
            select(TranslationFeedback)
            .where(TranslationFeedback.user_id == user_id)
            .order_by(TranslationFeedback.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        feedbacks = result.scalars().all()

        return FeedbackListResponse(
            total=total,
            limit=limit,
            offset=offset,
            data=[FeedbackResponse.model_validate(fb) for fb in feedbacks],
        )

    # ==================================================================
    # PRIVATE HELPERS
    # ==================================================================

    async def _get_user_translation(self, user_id: str, translation_id: str) -> Translation:
        """Tìm Translation thuộc user, raise 404 nếu không tìm thấy."""
        result = await self.db.execute(
            select(Translation).where(
                and_(
                    Translation.id == translation_id,
                    Translation.user_id == user_id,
                )
            )
        )
        translation = result.scalar_one_or_none()
        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy bản dịch hoặc bạn không có quyền truy cập.",
            )
        return translation

    async def _get_own_feedback(self, user_id: str, feedback_id: str) -> TranslationFeedback:
        """Tìm Feedback thuộc user, raise 404 nếu không tìm thấy."""
        result = await self.db.execute(
            select(TranslationFeedback).where(
                and_(
                    TranslationFeedback.id == feedback_id,
                    TranslationFeedback.user_id == user_id,
                )
            )
        )
        feedback = result.scalar_one_or_none()
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy đánh giá hoặc bạn không có quyền truy cập.",
            )
        return feedback


# ------------------------------------------------------------------
# Dependency Injection
# ------------------------------------------------------------------
def get_feedback_service(db: AsyncSession = Depends(get_db)) -> FeedbackService:
    return FeedbackService(db)
