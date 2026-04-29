"""
schemas/user/user_schema.py
-----------------------------
Schemas dành riêng cho người dùng thường.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class UserResponse(BaseModel):
    """Schema for returning user information (excluding password)."""
    id: uuid.UUID
    email: str
    full_name: str
    tier: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
class UserUpdateRequest(BaseModel):
    """Partial update — chỉ truyền trường muốn thay đổi."""
    full_name: Optional[str] = None
    default_language_id: Optional[uuid.UUID] = None

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Họ tên không được để trống")
        return v.strip() if v else v


class ChangePasswordRequest(BaseModel):
    """Đổi mật khẩu khi đang đăng nhập — yêu cầu nhập mật khẩu hiện tại."""
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu mới phải có ít nhất 8 ký tự")
        return v