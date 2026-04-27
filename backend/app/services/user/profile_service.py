"""
services/user/profile_service.py
----------------------------------
Logic nghiệp vụ hồ sơ người dùng:
  - Xem thông tin cá nhân
  - Cập nhật họ tên, ngôn ngữ mặc định
  - Đổi mật khẩu khi đã đăng nhập (khác với reset-password)
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...models.models import Language, User
from ...schemas.schemas import (
    ChangePasswordRequest,
    UserResponse,
    UserUpdateRequest,
)
from ...utils.security import hash_password, verify_password


class UserProfileService:
    """
    Quản lý hồ sơ cá nhân người dùng.
    Tất cả method đều nhận user_id lấy từ session (middleware đã xác thực).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------
    # LẤY THÔNG TIN CÁ NHÂN
    # --------------------------------------------------
    async def get_profile(self, user_id: str) -> UserResponse:
        """
        Trả về thông tin hồ sơ của người dùng đang đăng nhập.
        Không trả về hashed_password.
        """
        stmt = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản không tồn tại.",
            )
        return UserResponse.model_validate(user)

    # --------------------------------------------------
    # CẬP NHẬT THÔNG TIN CÁ NHÂN
    # --------------------------------------------------
    async def update_profile(self, user_id: str, payload: UserUpdateRequest) -> UserResponse:
        """
        Cập nhật họ tên và / hoặc ngôn ngữ mặc định.
        - Nếu trường nào là None thì giữ nguyên giá trị cũ (partial update).
        - Kiểm tra default_language_id tồn tại và đang active trước khi lưu.
        """
        stmt = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản không tồn tại.",
            )

        # Cập nhật họ tên nếu có truyền vào
        if payload.full_name is not None:
            user.full_name = payload.full_name

        # Kiểm tra và cập nhật ngôn ngữ mặc định nếu có truyền vào
        if payload.default_language_id is not None:
            lang_stmt = select(Language).where(
                Language.id == payload.default_language_id,
                Language.is_active == True,
            )
            lang_result = await self.db.execute(lang_stmt)
            lang = lang_result.scalar_one_or_none()

            if not lang:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ngôn ngữ không tồn tại hoặc đang bị tắt.",
                )
            user.default_language_id = payload.default_language_id

        await self.db.commit()
        await self.db.refresh(user)
        return UserResponse.model_validate(user)

    # --------------------------------------------------
    # ĐỔI MẬT KHẨU (khi đã đăng nhập)
    # --------------------------------------------------
    async def change_password(self, user_id: str, payload: ChangePasswordRequest) -> dict:
        """
        Đổi mật khẩu khi người dùng đang đăng nhập.
        Khác với reset_password: yêu cầu nhập mật khẩu hiện tại để xác nhận danh tính.
        Điều kiện:
          1. Mật khẩu hiện tại phải đúng
          2. Mật khẩu mới và xác nhận phải khớp nhau
          3. Mật khẩu mới không được trùng mật khẩu cũ
        """
        stmt = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản không tồn tại.",
            )

        # Kiểm tra mật khẩu hiện tại
        if not verify_password(payload.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu hiện tại không đúng.",
            )

        # Kiểm tra mật khẩu mới và xác nhận khớp nhau
        if payload.new_password != payload.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu xác nhận không khớp.",
            )

        # Kiểm tra mật khẩu mới không trùng mật khẩu cũ
        if verify_password(payload.new_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu mới không được trùng mật khẩu hiện tại.",
            )

        user.hashed_password = hash_password(payload.new_password)
        await self.db.commit()

        return {"message": "Đổi mật khẩu thành công."}


def get_user_profile_service(db: AsyncSession = Depends(get_db)) -> UserProfileService:
    return UserProfileService(db)