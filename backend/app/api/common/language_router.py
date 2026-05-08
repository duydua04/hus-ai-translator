"""
api/language/language_router.py
---------------------------------
Router danh mục ngôn ngữ.
- GET /languages        : user xem danh sách ngôn ngữ đang active (public)
- POST /languages       : admin thêm ngôn ngữ mới
- PATCH /languages/{id}/activate   : admin bật ngôn ngữ
- PATCH /languages/{id}/deactivate : admin tắt ngôn ngữ
"""
from typing import List

from fastapi import APIRouter, Depends, status

from ...middleware.auth import require_admin
from ...schemas.common.language_schema import LanguageCreateRequest, LanguageResponse
from ...services.common.language_service import LanguageService, get_language_service

router = APIRouter(prefix="/languages", tags=["Languages - Ngôn ngữ"])


@router.get("", response_model=List[LanguageResponse])
async def get_active_languages(
    service: LanguageService = Depends(get_language_service),
):
    """Lấy danh sách ngôn ngữ đang hoạt động. Dùng để hiển thị dropdown chọn ngôn ngữ."""
    return await service.get_active_languages()


@router.get("/all", response_model=List[LanguageResponse])
async def get_all_languages(
    service: LanguageService = Depends(get_language_service),
    _=Depends(require_admin),
):
    """Admin xem toàn bộ ngôn ngữ kể cả đã tắt."""
    return await service.get_all_languages()


@router.post("", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
async def create_language(
    payload: LanguageCreateRequest,
    service: LanguageService = Depends(get_language_service),
    _=Depends(require_admin),
):
    """Admin thêm ngôn ngữ mới vào danh mục."""
    return await service.create_language(payload)


@router.patch("/{language_id}/activate", response_model=LanguageResponse)
async def activate_language(
    language_id: str,
    service: LanguageService = Depends(get_language_service),
    _=Depends(require_admin),
):
    """Admin bật lại một ngôn ngữ đã bị tắt."""
    return await service.toggle_language_active(language_id, is_active=True)


@router.patch("/{language_id}/deactivate", response_model=LanguageResponse)
async def deactivate_language(
    language_id: str,
    service: LanguageService = Depends(get_language_service),
    _=Depends(require_admin),
):
    """Admin tắt một ngôn ngữ. Ngôn ngữ sẽ không xuất hiện trong dropdown người dùng."""
    return await service.toggle_language_active(language_id, is_active=False)
    