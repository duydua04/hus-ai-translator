"""
services/user/text_translation_service.py
------------------------------------------
Service dịch văn bản trực tiếp qua AI Model.
Kết quả được lưu vào bảng translations (type="text").
"""
import httpx
from fastapi import HTTPException, status
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...config.settings import settings
from ...models.models import Translation, Language
from ...services.admin.admin_dashboard_service import AdminDashboardService

TRANSLATE_MODEL_URL = settings.TRANSLATE_MODEL_URL


class TextTranslationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # PUBLIC: Dịch text + lưu DB
    # ------------------------------------------------------------------
    async def translate_and_save(
        self,
        user_id: str,
        text: str,
        source_lang_code: str,
        target_lang_code: str,
    ) -> dict:
        """
        1. Resolve language codes → language IDs
        2. Tạo bản ghi Translation (status=processing)
        3. Gọi AI Model
        4. Cập nhật translated_content + status=success (hoặc failed)
        5. Trả về response
        """
        # --- 1. Resolve language codes ---
        source_lang = await self._get_language_by_code(source_lang_code)
        target_lang = await self._get_language_by_code(target_lang_code)

        # --- 2. Tạo bản ghi Translation ---
        new_translation = Translation(
            user_id=user_id,
            source_lang_id=source_lang.id,
            target_lang_id=target_lang.id,
            type="text",
            input_content=text,
            status="processing",
        )
        self.db.add(new_translation)
        await self.db.commit()
        await self.db.refresh(new_translation)

        # --- 3. Gọi AI Model ---
        try:
            translated_text = await self._call_ai_model(text, source_lang_code, target_lang_code)

            # --- 4a. Thành công → cập nhật DB ---
            new_translation.translated_content = translated_text
            new_translation.status = "success"
            await self.db.commit()
            await self.db.refresh(new_translation)

            # Notify admin dashboard
            try:
                admin_svc = AdminDashboardService(self.db)
                await admin_svc.invalidate_on_translation()
                await AdminDashboardService.notify_admin(
                    event_type="new_translation",
                    message="Có bản dịch text mới.",
                    data={"translation_id": str(new_translation.id)},
                )
            except Exception:
                pass

            return {
                "success": True,
                "data": {
                    "translation_id": str(new_translation.id),
                    "original_text": text,
                    "translated_text": translated_text,
                    "source_lang_code": source_lang_code,
                    "target_lang_code": target_lang_code,
                    "status": "success",
                },
            }

        except HTTPException:
            # --- 4b. Thất bại → đánh dấu failed ---
            new_translation.status = "failed"
            await self.db.commit()
            raise

        except Exception as e:
            new_translation.status = "failed"
            await self.db.commit()
            print(f"❌ Lỗi nội bộ khi dịch text: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Đã xảy ra lỗi khi dịch văn bản.",
            )

    # ------------------------------------------------------------------
    # PRIVATE: Gọi AI Model
    # ------------------------------------------------------------------
    async def _call_ai_model(self, text: str, source_lang: str, target_lang: str) -> str:
        """Gửi request tới Translate Model service và trả về kết quả."""
        direction = f"{source_lang}-{target_lang}"
        if direction not in ["en-vi", "vi-en"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dịch vụ hiện tại chỉ hỗ trợ dịch Anh-Việt hoặc Việt-Anh.",
            )

        payload = {"text": text, "direction": direction}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{TRANSLATE_MODEL_URL}/api/v1/translate",
                    json=payload,
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("translated_text", "")

        except httpx.ConnectError:
            print("❌ Lỗi kết nối: Translate Model service có thể chưa được bật.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Dịch vụ AI dịch thuật hiện đang offline.",
            )
        except httpx.TimeoutException:
            print("❌ Lỗi timeout: Dịch quá lâu.")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="AI Model phản hồi quá lâu.",
            )
        except httpx.HTTPStatusError as e:
            print(f"❌ AI Model trả lỗi HTTP: {e.response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI Model trả về lỗi.",
            )

    # ------------------------------------------------------------------
    # PRIVATE: Resolve language code → Language record
    # ------------------------------------------------------------------
    async def _get_language_by_code(self, code: str) -> Language:
        """Tìm Language entity theo language_code, raise 400 nếu không tìm thấy."""
        result = await self.db.execute(
            select(Language).where(Language.language_code == code, Language.is_active == True)
        )
        lang = result.scalar_one_or_none()
        if not lang:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ngôn ngữ '{code}' không được hỗ trợ hoặc chưa được kích hoạt.",
            )
        return lang


# ------------------------------------------------------------------
# Dependency Injection
# ------------------------------------------------------------------
def get_text_translation_service(db: AsyncSession = Depends(get_db)) -> TextTranslationService:
    return TextTranslationService(db)