
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ...middleware.auth import require_user
from sqlalchemy.ext.asyncio import AsyncSession
from ...config.db import get_db
from ...schemas.common.translation import FileTranslationStartRequest, WebhookTranslationDone
from ...services.user.translation_service import TranslationService

# Hàm lấy DB có thể đưa thẳng vào tham số dependency
def get_service(db: Session = Depends(get_db)) -> TranslationService:
    return TranslationService(db)

translate_router = APIRouter(tags=["File Translation (Async)"])

# Giả lập hàm lấy auth token
# def get_current_user_id(...) -> str: return "uuid-cua-user"

@translate_router.post("/api/translations/file/start/{client_id}", status_code=status.HTTP_200_OK)
async def start_file_translation(
    client_id: str,
    payload: FileTranslationStartRequest,
    db: AsyncSession = Depends(get_db),
    service: TranslationService = Depends(get_service),
    auth_info: dict = Depends(require_user) # BẮT BUỘC ĐĂNG NHẬP
):
    # Lấy đối tượng user đang thực hiện request
    current_user = auth_info["user"]

    # Chuyền ID của user thật vào service xử lý
    result = await service.create_file_translation_task(
        client_id=client_id,
        payload=payload,
        user_id=current_user.id
    )
    return result


@translate_router.post("/api/webhook/translation-done", status_code=status.HTTP_200_OK)
async def translation_webhook(
    payload: WebhookTranslationDone,
    service: TranslationService = Depends(get_service)
):
    """
    API Webhook do AI Worker gọi về khi dịch xong file.
    """
    result = service.handle_webhook_result(payload)
    return result