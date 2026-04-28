from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...models.models import Admin, User
from ...schemas.auth_schemas import RegisterRequest, OAuth2Token
from ...utils.security import (
    hash_password,
    verify_password,
    issue_token_pair,
    verify_refresh_token
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, payload: RegisterRequest) -> User:
        """Đăng ký tài khoản người dùng mới."""
        stmt = select(User).where(User.email == payload.email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email này đã được đăng ký."
            )

        new_user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password)
        )
        self.db.add(new_user)
        try:
            await self.db.commit()
            await self.db.refresh(new_user)
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Lỗi hệ thống khi lưu dữ liệu."
            )
        return new_user

    async def authenticate_user(self, email: str, password: str, role: str = "user") -> OAuth2Token:
        """Xác thực người dùng/admin và cấp cặp token."""
        user_obj = None
        if role == "admin":
            stmt = select(Admin).where(Admin.email == email)
        else:
            stmt = select(User).where(User.email == email)

        result = await self.db.execute(stmt)
        user_obj = result.scalar_one_or_none()

        if not user_obj or not verify_password(password, user_obj.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not getattr(user_obj, "is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị vô hiệu hóa."
            )

        return issue_token_pair(email=email, role=role)

    async def refresh_token(self, refresh_token: str) -> OAuth2Token:
        """Làm mới Access Token từ Refresh Token."""
        try:
            payload = verify_refresh_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ hoặc đã hết hạn."
            )

        email = payload.get("sub")
        role = payload.get("role")

        if role == "admin":
            stmt = select(Admin).where(Admin.email == email, Admin.is_active == True)
        else:
            stmt = select(User).where(User.email == email, User.is_active == True)

        result = await self.db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản không tồn tại hoặc đã bị khóa."
            )

        return issue_token_pair(email=email, role=role)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)