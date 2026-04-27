from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator

class RegisterRequest(BaseModel):
    """Schema for new user registration."""
    email: EmailStr
    full_name: str
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip()


class LoginRequest(BaseModel):
    """Schema for JSON-based login."""
    email: EmailStr
    password: str


class OAuth2Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """Schema for returning user information (excluding password)."""
    id: uuid.UUID
    email: str
    full_name: str
    tier: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class ForgotPasswordRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema for setting a new password."""
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters long")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v