"""
services/user/language_service.py
-----------------------------------
Logic nghiệp vụ danh mục ngôn ngữ:
  - Lấy danh sách ngôn ngữ đang hoạt động (cho user chọn khi dịch)
  - Admin thêm / bật / tắt ngôn ngữ
"""
from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...models.models import Language
from ...schemas.common.language_schema import LanguageCreateRequest, LanguageResponse


class LanguageService:
    """
    Quản lý danh mục ngôn ngữ.
    User chỉ được đọc danh sách is_active=True.
    Admin được thêm mới và bật/tắt ngôn ngữ.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------
    # LẤY DANH SÁCH NGÔN NGỮ ĐANG HOẠT ĐỘNG
    # --------------------------------------------------
    async def get_active_languages(self) -> List[LanguageResponse]:
        """
        Trả về tất cả ngôn ngữ có is_active=True.
        Dùng để hiển thị dropdown chọn ngôn ngữ nguồn / đích khi dịch.
        """
        stmt = (
            select(Language)
            .where(Language.is_active == True)
            .order_by(Language.language_name)
        )
        result = await self.db.execute(stmt)
        langs = result.scalars().all()
        return [LanguageResponse.model_validate(l) for l in langs]

    # --------------------------------------------------
    # LẤY TẤT CẢ NGÔN NGỮ (kể cả inactive - dành cho admin)
    # --------------------------------------------------
    async def get_all_languages(self) -> List[LanguageResponse]:
        """Admin xem toàn bộ ngôn ngữ, bao gồm cả những ngôn ngữ bị tắt."""
        stmt = select(Language).order_by(Language.language_name)
        result = await self.db.execute(stmt)
        langs = result.scalars().all()
        return [LanguageResponse.model_validate(l) for l in langs]

    # --------------------------------------------------
    # THÊM NGÔN NGỮ MỚI (admin)
    # --------------------------------------------------
    async def create_language(self, payload: LanguageCreateRequest) -> LanguageResponse:
        """
        Admin thêm ngôn ngữ mới vào danh mục.
        Kiểm tra language_code chưa tồn tại (phải là duy nhất, ví dụ: 'en', 'vi').
        """
        stmt = select(Language).where(Language.language_code == payload.language_code)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã ngôn ngữ '{payload.language_code}' đã tồn tại.",
            )

        new_lang = Language(
            language_code=payload.language_code,
            language_name=payload.language_name.strip(),
            is_active=True,
        )
        self.db.add(new_lang)
        await self.db.commit()
        await self.db.refresh(new_lang)
        return LanguageResponse.model_validate(new_lang)

    # --------------------------------------------------
    # BẬT / TẮT NGÔN NGỮ (admin)
    # --------------------------------------------------
    async def toggle_language_active(self, language_code: str, is_active: bool) -> LanguageResponse:
        """
        Admin bật (is_active=True) hoặc tắt (is_active=False) một ngôn ngữ.
        Khi tắt, ngôn ngữ đó sẽ không xuất hiện trong dropdown của người dùng nữa.
        Các bản dịch cũ dùng ngôn ngữ này vẫn giữ nguyên trong DB.
        """
        stmt = select(Language).where(Language.language_code == language_code)
        result = await self.db.execute(stmt)
        lang = result.scalar_one_or_none()

        if not lang:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ngôn ngữ không tồn tại.",
            )

        lang.is_active = is_active
        await self.db.commit()
        await self.db.refresh(lang)
        return LanguageResponse.model_validate(lang)


def get_language_service(db: AsyncSession = Depends(get_db)) -> LanguageService:
    return LanguageService(db)