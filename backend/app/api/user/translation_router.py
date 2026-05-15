"""
api/user/translation_router.py
-------------------------------
Router dịch thuật — tính năng cốt lõi của hệ thống.
Bao gồm: dịch file (async), webhook AI worker, dịch text trực tiếp.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...middleware.auth import require_user
from ...schemas.common.translation import (
    FileTranslationStartRequest,
    WebhookTranslationDone,
    TextTranslationRequest,
)
from ...services.user.text_translation_service import (
    TextTranslationService,
    get_text_translation_service,
)
from ...services.user.translation_service import TranslationService

translate_router = APIRouter(tags=["Translation - Dịch thuật"])


# Dependency Injection cho TranslationService (file translation)
def get_service(db: AsyncSession = Depends(get_db)) -> TranslationService:
    return TranslationService(db)


# ---------------------------------------------------------
# 1. Dịch file (async qua Redis Queue + SSE)
# ---------------------------------------------------------
@translate_router.post(
    "/api/translations/file/start/{client_id}",
    status_code=status.HTTP_200_OK,
)
async def start_file_translation(
    client_id: str,
    payload: FileTranslationStartRequest,
    service: TranslationService = Depends(get_service),
    auth_info: dict = Depends(require_user),
):
    """
    Khởi tạo tiến trình dịch file.
    Tạo bản ghi Translation (status=processing), đẩy task vào Redis Queue,
    và bắn SSE cho client biết.
    """
    current_user = auth_info["user"]
    result = await service.create_file_translation_task(
        client_id=client_id,
        payload=payload,
        user_id=current_user.id,
    )
    return result


# ---------------------------------------------------------
# 2. Webhook — AI Worker gọi khi dịch file xong
# ---------------------------------------------------------
@translate_router.post(
    "/api/webhook/translation-done",
    status_code=status.HTTP_200_OK,
)
async def translation_webhook(
    payload: WebhookTranslationDone,
    service: TranslationService = Depends(get_service),
):
    """
    API Webhook do AI Worker gọi về khi dịch xong file.
    Cập nhật Translation status → success/failed và gắn result_file_id.
    """
    result = await service.handle_webhook_result(payload)
    return result


# ---------------------------------------------------------
# 3. Dịch text trực tiếp (đồng bộ) — kết quả lưu DB
# ---------------------------------------------------------
@translate_router.post("/api/translations/text", status_code=status.HTTP_201_CREATED)
async def translate_raw_text(
    payload: TextTranslationRequest,
    service: TextTranslationService = Depends(get_text_translation_service),
    auth_info: dict = Depends(require_user),
):
    """
    API Dịch văn bản trực tiếp.
    Gọi AI Model, lưu kết quả vào bảng translations, trả response.
    """
    current_user = auth_info["user"]
    result = await service.translate_and_save(
        user_id=str(current_user.id),
        text=payload.text,
        source_lang_code=payload.source_lang_code,
        target_lang_code=payload.target_lang_code,
    )
    return result