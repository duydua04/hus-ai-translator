"""
services/user/auth_service.py
------------------------------
Toàn bộ logic nghiệp vụ xác thực cho người dùng thường:
  - Đăng ký
  - Đăng nhập
  - Làm mới token
  - Đăng xuất
  - Quên / đặt lại mật khẩu (OTP)
"""
from fastapi import Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...config.settings import settings
from ...models.models import User
from ...schemas.schemas import (
    LoginRequest,
    OAuth2Token,
    RegisterRequest,
    UserResponse,
)
from ...utils.security import (
    create_access_token,
    decode_token,
    delete_auth_cookies,
    hash_password,
    issue_token_pair,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)


class UserAuthService:
    """
    Chứa toàn bộ logic nghiệp vụ xác thực của người dùng.
    Tất cả truy vấn DB và xử lý điều kiện đều ở đây.
    API layer chỉ gọi service này.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------
    # ĐĂNG KÝ
    # --------------------------------------------------
    async def register(self, payload: RegisterRequest) -> UserResponse:
        """
        Đăng ký tài khoản mới.
        - Kiểm tra email chưa được đăng ký
        - Băm mật khẩu trước khi lưu
        """
        # Kiểm tra email tồn tại
        stmt = select(User).where(User.email == payload.email)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được đăng ký. Vui lòng sử dụng email khác.",
            )

        # Tạo user mới với mật khẩu đã được băm
        new_user = User(
            email=payload.email,
            full_name=payload.full_name.strip(),
            hashed_password=hash_password(payload.password),
            tier="free",
            is_active=True,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return UserResponse.model_validate(new_user)

    # --------------------------------------------------
    # ĐĂNG NHẬP
    # --------------------------------------------------
    async def login(self, payload: LoginRequest) -> OAuth2Token:
        """
        Đăng nhập: xác thực email + mật khẩu, trả về cặp token.
        - Kiểm tra tài khoản tồn tại và đang hoạt động
        - So khớp mật khẩu với hash trong DB
        """
        stmt = select(User).where(User.email == payload.email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        # Không phân biệt "email sai" hay "mật khẩu sai" để tránh enumeration attack
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không đúng.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ quản trị viên.",
            )

        return issue_token_pair(email=user.email, role="user")

    # --------------------------------------------------
    # LÀM MỚI TOKEN
    # --------------------------------------------------
    async def refresh_token(self, refresh_token: str) -> OAuth2Token:
        """
        Cấp lại access token từ refresh token còn hợp lệ.
        Kiểm tra user vẫn còn trong DB trước khi cấp token mới.
        """
        try:
            payload = verify_refresh_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token không hợp lệ hoặc đã hết hạn.",
            )

        email = payload.get("sub")
        role = payload.get("role")

        # Kiểm tra user vẫn tồn tại và đang hoạt động
        stmt = select(User).where(User.email == email, User.is_active == True)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản không tồn tại hoặc đã bị vô hiệu hóa.",
            )

        return issue_token_pair(email=email, role=role)

    # --------------------------------------------------
    # ĐĂNG XUẤT
    # --------------------------------------------------
    @staticmethod
    def logout(response: Response) -> dict:
        """
        Đăng xuất: xóa tất cả auth cookie phía client.
        Static method vì không cần gọi DB.
        """
        delete_auth_cookies(response, role="user")
        return {"message": "Đăng xuất thành công."}

    # --------------------------------------------------
    # QUÊN MẬT KHẨU (bước 1: gửi OTP)
    # --------------------------------------------------
    async def forgot_password_request(self, email: str) -> dict:
        """
        Kiểm tra email tồn tại, tạo OTP và đóng gói vào reset_token.
        Trong thực tế: gửi OTP qua email (tích hợp SMTP/SES).
        Trả về reset_token để lưu vào cookie (httponly).
        """
        stmt = select(User).where(User.email == email, User.is_active == True)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            # Trả về thành công giả để không lộ email tồn tại hay không
            return {"message": "Nếu email tồn tại, OTP đã được gửi."}

        # Tạo OTP 6 số
        import random
        otp_code = str(random.randint(100000, 999999))
        otp_hash = hash_password(otp_code)  # Băm OTP trước khi lưu vào token

        # TODO: Gửi otp_code qua email thực tế
        # send_otp_email(email, otp_code)

        # Tạo reset_token chứa otp_hash (dạng special access_token)
        reset_token = create_access_token(
            sub=email,
            role="user",
            expires_minutes=settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES,
            extra={"type": "reset_waiting", "otp_hash": otp_hash},
        )

        # Trả về reset_token để controller set vào cookie
        return {
            "message": "Nếu email tồn tại, OTP đã được gửi.",
            "reset_token": reset_token,
            # Chỉ dùng cho môi trường dev/test:
            "_dev_otp": otp_code if not settings.is_production else None,
        }

    # --------------------------------------------------
    # QUÊN MẬT KHẨU (bước 2: xác thực OTP)
    # --------------------------------------------------
    @staticmethod
    def verify_otp(otp_input: str, reset_token: str) -> dict:
        """
        Xác thực OTP người dùng nhập so với OTP hash trong reset_token.
        Nếu đúng, cấp permission_token để đặt mật khẩu mới.
        Static method: không gọi DB, tính toán thuần túy.
        """
        try:
            payload = decode_token(reset_token)
            if payload.get("type") != "reset_waiting":
                raise ValueError("Sai loại token")
            if not verify_password(otp_input, payload.get("otp_hash", "")):
                raise ValueError("OTP không đúng")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP không đúng hoặc phiên đã hết hạn.",
            )

        # Cấp permission_token (có hiệu lực 5 phút) để đặt mật khẩu
        permission_token = create_access_token(
            sub=payload.get("sub"),
            role="user",
            expires_minutes=5,
            extra={"type": "reset_allowed"},
        )

        return {"message": "OTP hợp lệ.", "permission_token": permission_token}

    # --------------------------------------------------
    # QUÊN MẬT KHẨU (bước 3: đặt mật khẩu mới)
    # --------------------------------------------------
    async def reset_password(self, new_password: str, permission_token: str) -> dict:
        """
        Đặt lại mật khẩu sau khi đã xác thực OTP thành công.
        Kiểm tra permission_token hợp lệ trước khi cập nhật DB.
        """
        try:
            payload = decode_token(permission_token)
            if payload.get("type") != "reset_allowed":
                raise ValueError("Sai loại token")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phiên đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.",
            )

        email = payload.get("sub")
        stmt = select(User).where(User.email == email, User.is_active == True)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản không tồn tại.",
            )

        user.hashed_password = hash_password(new_password)
        await self.db.commit()

        return {"message": "Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại."}


# Factory để FastAPI Depends inject
def get_user_auth_service(db: AsyncSession = Depends(get_db)) -> UserAuthService:
    return UserAuthService(db)