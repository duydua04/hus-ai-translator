"""
api/translation/translation_router.py
---------------------------------------
Router dịch thuật — tính năng cốt lõi của hệ thống.
Tất cả endpoint đều yêu cầu đăng nhập (require_user).
"""
from typing import Optional

from fastapi import APIRouter, Depends, status

from ...middleware.auth import require_user
from ...schemas.user.translation_schema import (
    TranslateDocumentRequest,
    TranslateTextRequest,
    TranslationListResponse,
    TranslationResponse,
)
from ...services.user.translation_service import TranslationService, get_translation_service

router = APIRouter(prefix="/translate", tags=["Translation - Dịch thuật"])


@router.post("/text", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
async def translate_text(
    payload: TranslateTextRequest,
    info=Depends(require_user),
    service: TranslationService = Depends(get_translation_service),
):
    """
    Dịch văn bản thuần.
    Kết quả lưu vào lịch sử và trả về ngay trong response.
    """
    user_id = str(info["user"].id)
    return await service.translate_text(user_id, payload)


@router.post("/document", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
async def translate_document(
    payload: TranslateDocumentRequest,
    info=Depends(require_user),
    service: TranslationService = Depends(get_translation_service),
):
    """
    Dịch tài liệu đã upload (input_file_id lấy từ /upload sau khi upload file).
    Kết quả trả về có result_file_id để tải file đã dịch.
    """
    user_id = str(info["user"].id)
    return await service.translate_document(user_id, payload)


@router.get("/history", response_model=TranslationListResponse)
async def get_history(
    type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    info=Depends(require_user),
    service: TranslationService = Depends(get_translation_service),
):
    """
    Lịch sử dịch thuật của người dùng.
    Lọc theo type (text/document_pdf/audio) và status (pending/processing/success/failed).
    """
    user_id = str(info["user"].id)
    return await service.get_history(
        user_id=user_id,
        type=type,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get("/{translation_id}", response_model=TranslationResponse)
async def get_translation_detail(
    translation_id: str,
    info=Depends(require_user),
    service: TranslationService = Depends(get_translation_service),
):
    """Xem chi tiết một bản dịch cụ thể."""
    user_id = str(info["user"].id)
    return await service.get_detail(user_id, translation_id)


@router.delete("/{translation_id}")
async def delete_translation(
    translation_id: str,
    info=Depends(require_user),
    service: TranslationService = Depends(get_translation_service),
):
    """Xóa một bản dịch khỏi lịch sử."""
    user_id = str(info["user"].id)
    return await service.delete_translation(user_id, translation_id)