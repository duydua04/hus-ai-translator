from __future__ import annotations
from datetime import datetime
from typing import Optional, List
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
    full_name: Optional[str] = None
    default_language_id: Optional[uuid.UUID] = None
 
    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Họ tên không được để trống")
        return v.strip() if v else v
 
 
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
 
    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu mới phải có ít nhất 8 ký tự")
        return v
 

# =========================================================
# LANGUAGE SCHEMAS
# =========================================================
 
class LanguageResponse(BaseModel):
    id: uuid.UUID
    language_code: str
    language_name: str
    is_active: bool
 
    model_config = {"from_attributes": True}
 
 
class LanguageCreateRequest(BaseModel):
    language_code: str
    language_name: str
 
    @field_validator("language_code")
    @classmethod
    def code_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("Mã ngôn ngữ không được để trống")
        return v
 
 
# =========================================================
# TRANSLATION SCHEMAS
# =========================================================
 
class TranslateTextRequest(BaseModel):
    source_lang_id: uuid.UUID
    target_lang_id: uuid.UUID
    input_content: str
    llm_model: Optional[str] = "gpt-4o"
 
    @field_validator("input_content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nội dung dịch không được để trống")
        if len(v) > 10000:
            raise ValueError("Nội dung quá dài, tối đa 10.000 ký tự")
        return v
 
 
class TranslateDocumentRequest(BaseModel):
    source_lang_id: uuid.UUID
    target_lang_id: uuid.UUID
    input_file_id: uuid.UUID
    llm_model: Optional[str] = "gpt-4o"
 
 
class TranslationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    source_lang_id: uuid.UUID
    target_lang_id: uuid.UUID
    type: str
    input_content: Optional[str]
    translated_content: Optional[str]
    input_file_id: Optional[uuid.UUID]
    result_file_id: Optional[uuid.UUID]
    llm_model: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
 
    model_config = {"from_attributes": True}
 
 
class TranslationListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[TranslationResponse]
 
 
# =========================================================
# FEEDBACK SCHEMAS
# =========================================================
 
class FeedbackCreateRequest(BaseModel):
    translation_id: uuid.UUID
    rating: int
    corrected_content: Optional[str] = None
    feedback_note: Optional[str] = None
 
    @field_validator("rating")
    @classmethod
    def rating_range(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Điểm đánh giá phải từ 1 đến 5 sao")
        return v
 
 
class FeedbackResponse(BaseModel):
    id: uuid.UUID
    translation_id: uuid.UUID
    user_id: uuid.UUID
    rating: int
    corrected_content: Optional[str]
    feedback_note: Optional[str]
    created_at: datetime
 
    model_config = {"from_attributes": True}
 
 
# =========================================================
# CHAT SCHEMAS
# =========================================================
 
class ChatSessionCreateRequest(BaseModel):
    title: Optional[str] = None
 
 
class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: Optional[str]
    is_pinned: bool
    created_at: datetime
    updated_at: Optional[datetime]
 
    model_config = {"from_attributes": True}
 
 
class ChatSessionListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[ChatSessionResponse]
 
 
class SendMessageRequest(BaseModel):
    content: str
 
    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Tin nhắn không được để trống")
        if len(v) > 8000:
            raise ValueError("Tin nhắn quá dài, tối đa 8.000 ký tự")
        return v
 
 
class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    translation_id: Optional[uuid.UUID]
    token_count: int
    created_at: datetime
 
    model_config = {"from_attributes": True}
 
 
class ChatHistoryResponse(BaseModel):
    session: ChatSessionResponse
    messages: List[ChatMessageResponse]
 
 
class PinSessionRequest(BaseModel):
    is_pinned: bool



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