"""
services/admin/feedback_service.py
------------------------------------
Logic nghiệp vụ admin quản lý feedback:
  - Xem toàn bộ feedback trên hệ thống (có lọc, phân trang)
  - Xem chi tiết một feedback
  - Thống kê chất lượng bản dịch theo rating
  - Xóa feedback vi phạm
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import Float, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...models.models import Translation, TranslationFeedback, User


class AdminFeedbackService:
    """
    Admin quản lý toàn bộ feedback của hệ thống.
    Khác với FeedbackService của user:
      - Không giới hạn theo user_id — admin thấy tất cả
      - Có thêm thống kê chất lượng theo rating, theo model AI
      - Có thể xóa bất kỳ feedback nào (vi phạm, spam)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------
    # DANH SÁCH TẤT CẢ FEEDBACK (có lọc + phân trang)
    # --------------------------------------------------
    async def list_feedbacks(
        self,
        rating: Optional[int] = None,
        user_id: Optional[str] = None,
        translation_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """
        Admin xem toàn bộ feedback trên hệ thống với bộ lọc:
          - rating        : lọc theo số sao (1-5)
          - user_id       : lọc feedback của một user cụ thể
          - translation_id: lọc feedback của một bản dịch cụ thể
        Sắp xếp mới nhất lên đầu.
        """
        stmt = select(TranslationFeedback)

        if rating is not None:
            if rating < 1 or rating > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rating phải từ 1 đến 5.",
                )
            stmt = stmt.where(TranslationFeedback.rating == rating)

        if user_id:
            stmt = stmt.where(TranslationFeedback.user_id == user_id)

        if translation_id:
            stmt = stmt.where(TranslationFeedback.translation_id == translation_id)

        # Đếm tổng cho phân trang
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(TranslationFeedback.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        feedbacks = result.scalars().all()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": [self._to_dict(f) for f in feedbacks],
        }

    # --------------------------------------------------
    # XEM CHI TIẾT MỘT FEEDBACK
    # --------------------------------------------------
    async def get_feedback_detail(self, feedback_id: str) -> dict:
        """
        Admin xem chi tiết một feedback, kèm thông tin bản dịch gốc
        và thông tin người dùng để dễ đánh giá ngữ cảnh.
        """
        # Lấy feedback
        fb_stmt = select(TranslationFeedback).where(TranslationFeedback.id == feedback_id)
        fb_result = await self.db.execute(fb_stmt)
        feedback = fb_result.scalar_one_or_none()

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback không tồn tại.",
            )

        # Lấy thông tin bản dịch liên quan
        trans_stmt = select(Translation).where(Translation.id == feedback.translation_id)
        trans_result = await self.db.execute(trans_stmt)
        translation = trans_result.scalar_one_or_none()

        # Lấy thông tin user gửi feedback
        user_stmt = select(User).where(User.id == feedback.user_id)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        return {
            "feedback": self._to_dict(feedback),
            "translation": {
                "id": str(translation.id) if translation else None,
                "type": translation.type if translation else None,
                "input_content": translation.input_content if translation else None,
                "translated_content": translation.translated_content if translation else None,
                "llm_model": translation.llm_model if translation else None,
                "status": translation.status if translation else None,
            },
            "user": {
                "id": str(user.id) if user else None,
                "email": user.email if user else None,
                "full_name": user.full_name if user else None,
                "tier": user.tier if user else None,
            },
        }

    # --------------------------------------------------
    # THỐNG KÊ CHẤT LƯỢNG THEO RATING
    # --------------------------------------------------
    async def get_quality_stats(self, llm_model: Optional[str] = None) -> dict:
        """
        Thống kê chất lượng bản dịch theo rating:
          - Điểm trung bình toàn hệ thống
          - Phân bổ số lượng theo từng mức sao (1★ → 5★)
          - Tổng số bản dịch đã có bản sửa tay (corrected_content)
          - Nếu truyền llm_model thì lọc thống kê cho model đó
        Dùng để so sánh chất lượng giữa các model AI.
        """
        # Base query — join với translations để lọc theo llm_model nếu cần
        base_stmt = select(TranslationFeedback)
        if llm_model:
            base_stmt = (
                base_stmt
                .join(Translation, TranslationFeedback.translation_id == Translation.id)
                .where(Translation.llm_model == llm_model)
            )

        # Điểm trung bình
        avg_stmt = select(func.avg(TranslationFeedback.rating).cast(Float))
        if llm_model:
            avg_stmt = (
                avg_stmt
                .select_from(TranslationFeedback)
                .join(Translation, TranslationFeedback.translation_id == Translation.id)
                .where(Translation.llm_model == llm_model)
            )
        avg_result = await self.db.execute(avg_stmt)
        avg_rating = avg_result.scalar_one()

        # Phân bổ theo từng mức sao
        distribution = {}
        for star in range(1, 6):
            star_stmt = select(func.count(TranslationFeedback.id)).where(
                TranslationFeedback.rating == star
            )
            if llm_model:
                star_stmt = (
                    select(func.count(TranslationFeedback.id))
                    .select_from(TranslationFeedback)
                    .join(Translation, TranslationFeedback.translation_id == Translation.id)
                    .where(
                        TranslationFeedback.rating == star,
                        Translation.llm_model == llm_model,
                    )
                )
            star_result = await self.db.execute(star_stmt)
            distribution[f"{star}_star"] = star_result.scalar_one()

        # Tổng số bản dịch có bản sửa tay
        corrected_stmt = select(func.count(TranslationFeedback.id)).where(
            TranslationFeedback.corrected_content.isnot(None)
        )
        if llm_model:
            corrected_stmt = (
                select(func.count(TranslationFeedback.id))
                .select_from(TranslationFeedback)
                .join(Translation, TranslationFeedback.translation_id == Translation.id)
                .where(
                    TranslationFeedback.corrected_content.isnot(None),
                    Translation.llm_model == llm_model,
                )
            )
        corrected_result = await self.db.execute(corrected_stmt)
        total_corrected = corrected_result.scalar_one()

        # Tổng số feedback
        total_stmt = select(func.count(TranslationFeedback.id))
        if llm_model:
            total_stmt = (
                select(func.count(TranslationFeedback.id))
                .select_from(TranslationFeedback)
                .join(Translation, TranslationFeedback.translation_id == Translation.id)
                .where(Translation.llm_model == llm_model)
            )
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar_one()

        return {
            "llm_model": llm_model or "all",
            "total_feedbacks": total,
            "average_rating": round(avg_rating, 2) if avg_rating else 0,
            "distribution": distribution,
            "total_with_correction": total_corrected,
        }

    # --------------------------------------------------
    # XÓA FEEDBACK (vi phạm, spam)
    # --------------------------------------------------
    async def delete_feedback(self, feedback_id: str) -> dict:
        """
        Admin xóa một feedback bất kỳ.
        Dùng khi feedback có nội dung vi phạm, spam hoặc không phù hợp.
        Khác với user xóa feedback: admin không cần kiểm tra user_id.
        """
        stmt = select(TranslationFeedback).where(TranslationFeedback.id == feedback_id)
        result = await self.db.execute(stmt)
        feedback = result.scalar_one_or_none()

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback không tồn tại.",
            )

        await self.db.delete(feedback)
        await self.db.commit()
        return {"message": f"Đã xóa feedback {feedback_id} thành công."}

    # --------------------------------------------------
    # HELPER NỘI BỘ
    # --------------------------------------------------
    @staticmethod
    def _to_dict(f: TranslationFeedback) -> dict:
        """Chuyển TranslationFeedback ORM object thành dict để trả về API."""
        return {
            "id": str(f.id),
            "translation_id": str(f.translation_id),
            "user_id": str(f.user_id),
            "rating": f.rating,
            "corrected_content": f.corrected_content,
            "feedback_note": f.feedback_note,
            "created_at": f.created_at,
        }


def get_admin_feedback_service(db: AsyncSession = Depends(get_db)) -> AdminFeedbackService:
    return AdminFeedbackService(db)