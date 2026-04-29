"""
services/user/translation_service.py
--------------------------------------
Logic nghiệp vụ dịch thuật — tính năng cốt lõi của hệ thống:
  - Dịch văn bản thuần (text)
  - Dịch tài liệu (document đã upload)
  - Lấy lịch sử dịch thuật của người dùng
  - Xem chi tiết một bản dịch
  - Xóa một bản dịch khỏi lịch sử
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import get_db
from app.models.models import Language, MediaAsset, Translation
from app.schemas.user.translation_schema import (
    TranslateDocumentRequest,
    TranslateTextRequest,
    TranslationListResponse,
    TranslationResponse,
)


# =========================================================
# STUB GỌI LLM — thay bằng utils/llm_client.py thực tế
# =========================================================
async def _call_llm(
    text: str,
    source_lang_code: str,
    target_lang_code: str,
    model: str,
) -> str:
    """
    Stub gọi LLM API.
    Thay thế bằng openai.AsyncOpenAI() hoặc google.generativeai
    khi tích hợp thật.

    Ví dụ với OpenAI:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"Translate from {source_lang_code} to {target_lang_code}. Return only the translated text."},
                {"role": "user", "content": text},
            ]
        )
        return response.choices[0].message.content
    """
    return f"[Bản dịch stub từ {source_lang_code} → {target_lang_code}]: {text}"


class TranslationService:
    """
    Tất cả logic dịch thuật: tạo yêu cầu, gọi AI, lưu kết quả,
    truy vấn lịch sử, xóa bản ghi.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------
    # KIỂM TRA NGÔN NGỮ TỒN TẠI (dùng nội bộ)
    # --------------------------------------------------
    async def _get_language_or_404(self, lang_id) -> Language:
        stmt = select(Language).where(
            Language.id == lang_id,
            Language.is_active == True,
        )
        result = await self.db.execute(stmt)
        lang = result.scalar_one_or_none()
        if not lang:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ngôn ngữ không tồn tại hoặc đang bị tắt.",
            )
        return lang

    # --------------------------------------------------
    # DỊCH VĂN BẢN THUẦN (text)
    # --------------------------------------------------
    async def translate_text(
        self, user_id: str, payload: TranslateTextRequest
    ) -> TranslationResponse:
        """
        Luồng xử lý:
          1. Kiểm tra cả hai ngôn ngữ tồn tại và active
          2. Kiểm tra không dịch cùng một ngôn ngữ (source == target)
          3. Tạo bản ghi translation với status=pending
          4. Gọi LLM API lấy kết quả
          5. Cập nhật translated_content và status=success (hoặc failed)
          6. Trả về TranslationResponse
        """
        source_lang = await self._get_language_or_404(payload.source_lang_id)
        target_lang = await self._get_language_or_404(payload.target_lang_id)

        # Không cho phép dịch từ ngôn ngữ sang chính nó
        if str(payload.source_lang_id) == str(payload.target_lang_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ngôn ngữ nguồn và đích không được giống nhau.",
            )

        # Tạo bản ghi với trạng thái ban đầu là pending
        translation = Translation(
            user_id=user_id,
            source_lang_id=payload.source_lang_id,
            target_lang_id=payload.target_lang_id,
            type="text",
            input_content=payload.input_content,
            llm_model=payload.llm_model or "gpt-4o",
            status="pending",
        )
        self.db.add(translation)
        await self.db.commit()
        await self.db.refresh(translation)

        # Cập nhật trạng thái sang processing
        translation.status = "processing"
        await self.db.commit()

        # Gọi LLM
        try:
            result_text = await _call_llm(
                text=payload.input_content,
                source_lang_code=source_lang.language_code,
                target_lang_code=target_lang.language_code,
                model=translation.llm_model,
            )
            translation.translated_content = result_text
            translation.status = "success"
        except Exception as e:
            # Ghi nhận lỗi nhưng không xóa bản ghi để tiện debug
            translation.status = "failed"
            translation.translated_content = f"Lỗi: {str(e)}"

        await self.db.commit()
        await self.db.refresh(translation)
        return TranslationResponse.model_validate(translation)

    # --------------------------------------------------
    # DỊCH TÀI LIỆU (document đã upload)
    # --------------------------------------------------
    async def translate_document(
        self, user_id: str, payload: TranslateDocumentRequest
    ) -> TranslationResponse:
        """
        Dịch tài liệu đã được upload vào media_assets.
        Luồng:
          1. Kiểm tra file tồn tại và thuộc về user đang đăng nhập
          2. Kiểm tra ngôn ngữ
          3. Tạo bản ghi translation gắn input_file_id
          4. Gọi LLM với nội dung file (thực tế cần đọc file từ storage)
          5. Lưu kết quả và cập nhật status
        """
        source_lang = await self._get_language_or_404(payload.source_lang_id)
        target_lang = await self._get_language_or_404(payload.target_lang_id)

        if str(payload.source_lang_id) == str(payload.target_lang_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ngôn ngữ nguồn và đích không được giống nhau.",
            )

        # Kiểm tra file thuộc về user
        file_stmt = select(MediaAsset).where(
            MediaAsset.id == payload.input_file_id,
            MediaAsset.user_id == user_id,
        )
        file_result = await self.db.execute(file_stmt)
        media = file_result.scalar_one_or_none()

        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tệp không tồn tại hoặc không thuộc về tài khoản của bạn.",
            )

        translation = Translation(
            user_id=user_id,
            source_lang_id=payload.source_lang_id,
            target_lang_id=payload.target_lang_id,
            type="document_pdf",
            input_file_id=payload.input_file_id,
            llm_model=payload.llm_model or "gpt-4o",
            status="pending",
        )
        self.db.add(translation)
        await self.db.commit()
        await self.db.refresh(translation)

        translation.status = "processing"
        await self.db.commit()

        try:
            # TODO: Đọc nội dung file từ storage (file_storage.py)
            # file_content = await read_file_from_storage(media.file_path)
            file_content = f"[Nội dung file: {media.org_filename}]"

            result_text = await _call_llm(
                text=file_content,
                source_lang_code=source_lang.language_code,
                target_lang_code=target_lang.language_code,
                model=translation.llm_model,
            )
            translation.translated_content = result_text
            translation.status = "success"
        except Exception as e:
            translation.status = "failed"
            translation.translated_content = f"Lỗi: {str(e)}"

        await self.db.commit()
        await self.db.refresh(translation)
        return TranslationResponse.model_validate(translation)

    # --------------------------------------------------
    # LỊCH SỬ DỊCH THUẬT
    # --------------------------------------------------
    async def get_history(
        self,
        user_id: str,
        type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> TranslationListResponse:
        """
        Lấy lịch sử dịch của người dùng với bộ lọc:
          - type  : 'text' | 'document_pdf' | 'audio'
          - status: 'pending' | 'processing' | 'success' | 'failed'
        Sắp xếp mới nhất lên đầu.
        """
        stmt = select(Translation).where(Translation.user_id == user_id)

        if type:
            stmt = stmt.where(Translation.type == type)
        if status:
            stmt = stmt.where(Translation.status == status)

        # Đếm tổng trước khi phân trang
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Translation.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        translations = result.scalars().all()

        return TranslationListResponse(
            total=total,
            limit=limit,
            offset=offset,
            data=[TranslationResponse.model_validate(t) for t in translations],
        )

    # --------------------------------------------------
    # XEM CHI TIẾT MỘT BẢN DỊCH
    # --------------------------------------------------
    async def get_detail(self, user_id: str, translation_id: str) -> TranslationResponse:
        """
        Lấy chi tiết một bản dịch.
        Kiểm tra bản dịch thuộc về người dùng đang đăng nhập
        để tránh người dùng này xem bản dịch của người dùng khác.
        """
        stmt = select(Translation).where(
            Translation.id == translation_id,
            Translation.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        translation = result.scalar_one_or_none()

        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản dịch không tồn tại hoặc không thuộc về tài khoản của bạn.",
            )
        return TranslationResponse.model_validate(translation)

    # --------------------------------------------------
    # XÓA MỘT BẢN DỊCH KHỎI LỊCH SỬ
    # --------------------------------------------------
    async def delete_translation(self, user_id: str, translation_id: str) -> dict:
        """
        Xóa bản dịch khỏi lịch sử của người dùng.
        Chỉ xóa được bản dịch của chính mình.
        Nếu có feedback liên kết thì cascade xóa luôn (đã cấu hình trong model).
        """
        stmt = select(Translation).where(
            Translation.id == translation_id,
            Translation.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        translation = result.scalar_one_or_none()

        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản dịch không tồn tại hoặc không thuộc về tài khoản của bạn.",
            )

        await self.db.delete(translation)
        await self.db.commit()
        return {"message": "Đã xóa bản dịch khỏi lịch sử."}


def get_translation_service(db: AsyncSession = Depends(get_db)) -> TranslationService:
    return TranslationService(db)