"""
services/user/feedback_service.py
-----------------------------------
Logic nghiệp vụ đánh giá bản dịch:
  - Gửi đánh giá / sửa bản dịch
  - Xem danh sách feedback của bản thân
  - Xóa một feedback
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import get_db
from app.models.models import Translation, TranslationFeedback
from app.schemas.user.feedback_schema import FeedbackCreateRequest, FeedbackResponse


class FeedbackService:
    """
    Quản lý đánh giá bản dịch.
    Dữ liệu feedback dùng để fine-tune AI và đo lường chất lượng.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------
    # GỬI ĐÁNH GIÁ
    # --------------------------------------------------
    async def create_feedback(
        self, user_id: str, payload: FeedbackCreateRequest
    ) -> FeedbackResponse:
        """
        Người dùng gửi đánh giá cho một bản dịch.
        Điều kiện:
          1. Bản dịch phải tồn tại và thuộc về người dùng
          2. Bản dịch phải ở trạng thái success (không đánh giá bản dịch lỗi)
          3. Mỗi người dùng chỉ được đánh giá một lần cho mỗi bản dịch
        """
        # Kiểm tra bản dịch tồn tại và thuộc về user
        trans_stmt = select(Translation).where(
            Translation.id == payload.translation_id,
            Translation.user_id == user_id,
        )
        trans_result = await self.db.execute(trans_stmt)
        translation = trans_result.scalar_one_or_none()

        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản dịch không tồn tại hoặc không thuộc về tài khoản của bạn.",
            )

        if translation.status != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ có thể đánh giá bản dịch đã hoàn thành thành công.",
            )

        # Kiểm tra chưa đánh giá bản dịch này
        dup_stmt = select(TranslationFeedback).where(
            TranslationFeedback.translation_id == payload.translation_id,
            TranslationFeedback.user_id == user_id,
        )
        dup_result = await self.db.execute(dup_stmt)
        existing = dup_result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bạn đã đánh giá bản dịch này rồi. Vui lòng xóa đánh giá cũ trước khi gửi lại.",
            )

        feedback = TranslationFeedback(
            translation_id=payload.translation_id,
            user_id=user_id,
            rating=payload.rating,
            corrected_content=payload.corrected_content,
            feedback_note=payload.feedback_note,
        )
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return FeedbackResponse.model_validate(feedback)

    # --------------------------------------------------
    # DANH SÁCH FEEDBACK CỦA NGƯỜI DÙNG
    # --------------------------------------------------
    async def get_my_feedbacks(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """
        Lấy danh sách tất cả đánh giá mà người dùng đã gửi, mới nhất lên đầu.
        """
        stmt = (
            select(TranslationFeedback)
            .where(TranslationFeedback.user_id == user_id)
            .order_by(TranslationFeedback.created_at.desc())
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        feedbacks = result.scalars().all()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": [FeedbackResponse.model_validate(f) for f in feedbacks],
        }

    # --------------------------------------------------
    # XÓA FEEDBACK
    # --------------------------------------------------
    async def delete_feedback(self, user_id: str, feedback_id: str) -> dict:
        """
        Xóa một đánh giá.
        Chỉ xóa được đánh giá của chính mình.
        Sau khi xóa, người dùng có thể gửi lại đánh giá mới cho bản dịch đó.
        """
        stmt = select(TranslationFeedback).where(
            TranslationFeedback.id == feedback_id,
            TranslationFeedback.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        feedback = result.scalar_one_or_none()

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Đánh giá không tồn tại hoặc không thuộc về tài khoản của bạn.",
            )

        await self.db.delete(feedback)
        await self.db.commit()
        return {"message": "Đã xóa đánh giá thành công."}


def get_feedback_service(db: AsyncSession = Depends(get_db)) -> FeedbackService:
    return FeedbackService(db)