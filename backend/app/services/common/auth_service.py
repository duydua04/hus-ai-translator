from fastapi import Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...models.models import Admin, User
from ...schemas.common.auth_schemas import LoginRequest, RegisterRequest, OAuth2Token
from ...utils.security import (
    delete_auth_cookies,
    hash_password,
    verify_password,
    issue_token_pair,
    verify_refresh_token,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------
    # Alias methods (dùng bởi auth_api.py / auth_router.py)
    # --------------------------------------------------
    async def register(self, payload: RegisterRequest) -> User:
        """Alias của register_user — dùng bởi router."""
        return await self.register_user(payload)

    async def login(self, payload: LoginRequest) -> OAuth2Token:
        """Đăng nhập user và trả về cặp token."""
        return await self.authenticate_user(payload.email, payload.password, role="user")

    @staticmethod
    def logout(response: Response) -> dict:
        """Xóa cookie đăng nhập."""
        delete_auth_cookies(response, role="user")
        return {"message": "Đăng xuất thành công."}

    async def forgot_password_request(self, email: str) -> dict:
        """Stub — cần tích hợp gửi email OTP thực tế."""
        return {"message": "Nếu email tồn tại, OTP đã được gửi."}

    def verify_otp(self, otp: str, reset_token: str) -> dict:
        """Stub — cần tích hợp logic xác thực OTP thực tế."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Chức năng xác thực OTP chưa được triển khai.",
        )

    async def reset_password(self, new_password: str, permission_token: str) -> dict:
        """Stub — cần tích hợp logic reset mật khẩu thực tế."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Chức năng đặt lại mật khẩu chưa được triển khai.",
        )

    # --------------------------------------------------
    # Core methods
    # --------------------------------------------------
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


# Alias class dùng cho auth_router.py (services/user/auth_service.py)
UserAuthService = AuthService


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)
