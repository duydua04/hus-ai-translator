import math
import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import get_db
from app.models.models import Translation, TranslationFeedback, User
from app.schemas.admin.admin_user_schema import UserDetailResponse, UserListResponse

class AdminUserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        tier: Optional[str] = None,
    ) -> UserListResponse:
        offset = (page - 1) * limit
        stmt = select(User)

        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(User.email.ilike(search_term),
                    User.full_name.ilike(search_term)
                )
            )
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        if tier:
            stmt = stmt.where(User.tier == tier)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.db.scalar(count_stmt)

        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        users = result.scalars().all()

        total_pages = math.ceil(total / limit) if total > 0 else 1
        return UserListResponse(
            total=total, page=page,
            limit=limit, total_pages=total_pages,
            data=users
        )

    async def get_user_detail(self, user_id: str) -> UserDetailResponse:
        user_uuid = uuid.UUID(user_id)
        user = await self.db.get(User, user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )

        total_trans = await self.db.scalar(
            select(func.count(Translation.id))
            .where(Translation.user_id == user_uuid)
        )
        total_fb = await self.db.scalar(
            select(func.count(TranslationFeedback.id))
            .where(TranslationFeedback.user_id == user_uuid)
        )

        response_data = UserDetailResponse.model_validate(user)
        response_data.total_translations = total_trans or 0
        response_data.total_feedbacks = total_fb or 0
        return response_data

    async def toggle_user_status(self, user_id: str, is_active: bool) -> dict:
        user = await self.db.get(User, uuid.UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )

        user.is_active = is_active
        await self.db.commit()
        return {"message": f"Tài khoản {user.email} đã được {'mở khóa' if is_active else 'khóa'}."}

    async def delete_user(self, user_id: str) -> dict:
        user = await self.db.get(User, uuid.UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )

        await self.db.delete(user)
        await self.db.commit()
        return {"message": "Tài khoản và toàn bộ dữ liệu liên quan đã bị xóa vĩnh viễn."}

def get_admin_user_service(db: AsyncSession = Depends(get_db)) -> AdminUserService:
    return AdminUserService(db)