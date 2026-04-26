from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import uuid


# =========================================================
# AUTH SCHEMAS
# =========================================================

class RegisterRequest(BaseModel):
    """Schema đăng ký tài khoản người dùng mới."""
    email: EmailStr
    full_name: str
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Họ tên không được để trống")
        return v.strip()


class LoginRequest(BaseModel):
    """Schema đăng nhập."""
    email: EmailStr
    password: str


class OAuth2Token(BaseModel):
    """Schema token trả về sau khi đăng nhập thành công."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int          # Giây
    scope: str               # Role: user / admin


class ForgotPasswordRequest(BaseModel):
    """Schema yêu cầu đặt lại mật khẩu."""
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    """Schema xác thực mã OTP."""
    otp: str


class ResetPasswordRequest(BaseModel):
    """Schema đặt mật khẩu mới."""
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
        return v


# =========================================================
# USER SCHEMAS
# =========================================================

class UserResponse(BaseModel):
    """Schema trả về thông tin người dùng (không trả password)."""
    id: uuid.UUID
    email: str
    full_name: str
    tier: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """Schema cập nhật thông tin cá nhân."""
    full_name: Optional[str] = None
    default_language_id: Optional[uuid.UUID] = None


# =========================================================
# ADMIN SCHEMAS
# =========================================================

class AdminCreateRequest(BaseModel):
    """Schema admin tạo tài khoản admin mới."""
    email: EmailStr
    full_name: str
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
        return v


class AdminResponse(BaseModel):
    """Schema trả về thông tin admin."""
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Schema danh sách người dùng có phân trang."""
    total: int
    limit: int
    offset: int
    data: list[UserResponse]


class ChangeUserTierRequest(BaseModel):
    """Schema admin thay đổi gói dịch vụ của người dùng."""
    tier: str

    @field_validator("tier")
    @classmethod
    def tier_valid(cls, v: str) -> str:
        allowed = {"free", "pro", "enterprise"}
        if v not in allowed:
            raise ValueError(f"Tier phải là một trong: {allowed}")
        return v