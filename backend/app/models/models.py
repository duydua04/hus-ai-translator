import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Integer, Text, DateTime, ForeignKey, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..config.db import Base


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


# =========================================================
# 1. BẢNG LANGUAGES - Danh mục ngôn ngữ hỗ trợ
# =========================================================
class Language(Base):
    __tablename__ = "languages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    language_code = Column(String(10), unique=True, nullable=False)   # en, vi, ja
    language_name = Column(String(100), nullable=False)               # English, Tiếng Việt
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users_default = relationship("User", back_populates="default_language", foreign_keys="User.default_language_id")
    translations_source = relationship("Translation", back_populates="source_lang", foreign_keys="Translation.source_lang_id")
    translations_target = relationship("Translation", back_populates="target_lang", foreign_keys="Translation.target_lang_id")


# =========================================================
# 2. BẢNG USERS - Tài khoản người dùng
# =========================================================
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    tier = Column(
        Enum("free", "pro", "enterprise", name="user_tier_enum"),
        default="free",
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    default_language_id = Column(UUID(as_uuid=True), ForeignKey("languages.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    # Relationships
    default_language = relationship("Language", back_populates="users_default", foreign_keys=[default_language_id])
    media_assets = relationship("MediaAsset", back_populates="user")
    translations = relationship("Translation", back_populates="user")
    feedbacks = relationship("TranslationFeedback", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")


# =========================================================
# 3. BẢNG ADMINS - Tài khoản quản trị viên (tách riêng)
# =========================================================
class Admin(Base):
    __tablename__ = "admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)


# =========================================================
# 4. BẢNG MEDIA_ASSETS - Quản lý tệp tài liệu
# =========================================================
class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    org_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)   # AWS S3 / Cloud Storage path
    file_type = Column(
        Enum("document", "audio", "video", name="file_type_enum"),
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="media_assets")


# =========================================================
# 5. BẢNG TRANSLATIONS - Lịch sử dịch thuật (bảng trung tâm)
# =========================================================
class Translation(Base):
    __tablename__ = "translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_lang_id = Column(UUID(as_uuid=True), ForeignKey("languages.id"), nullable=False)
    target_lang_id = Column(UUID(as_uuid=True), ForeignKey("languages.id"), nullable=False)
    type = Column(
        Enum("text", "document_pdf", "audio", name="translation_type_enum"),
        nullable=False
    )
    input_content = Column(Text, nullable=True)         # Dùng khi dịch text thuần
    translated_content = Column(Text, nullable=True)    # Kết quả AI trả về
    input_file_id = Column(UUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=True)
    result_file_id = Column(UUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=True)
    llm_model = Column(String(100), nullable=True)      # gpt-4o, gemini-1.5, ...
    status = Column(
        Enum("pending", "processing", "success", "failed", name="translation_status_enum"),
        default="pending",
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    # Relationships
    user = relationship("User", back_populates="translations")
    source_lang = relationship("Language", back_populates="translations_source", foreign_keys=[source_lang_id])
    target_lang = relationship("Language", back_populates="translations_target", foreign_keys=[target_lang_id])
    feedbacks = relationship("TranslationFeedback", back_populates="translation")


# =========================================================
# 6. BẢNG TRANSLATION_FEEDBACKS - Đánh giá bản dịch
# =========================================================
class TranslationFeedback(Base):
    __tablename__ = "translation_feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    translation_id = Column(UUID(as_uuid=True), ForeignKey("translations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)             # 1-5 sao
    corrected_content = Column(Text, nullable=True)      # Bản dịch người dùng sửa lại
    feedback_note = Column(String(1000), nullable=True)  # Ghi chú thêm
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # Relationships
    translation = relationship("Translation", back_populates="feedbacks")
    user = relationship("User", back_populates="feedbacks")


# =========================================================
# 7. BẢNG CHAT_SESSIONS - Phiên trò chuyện với AI
# =========================================================
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=True)           # AI tự tóm tắt
    is_pinned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


# =========================================================
# 8. BẢNG CHAT_MESSAGES - Chi tiết tin nhắn trong phiên
# =========================================================
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(
        Enum("user", "assistant", "system", name="message_role_enum"),
        nullable=False
    )
    content = Column(Text, nullable=False)
    translation_id = Column(UUID(as_uuid=True), ForeignKey("translations.id"), nullable=True)
    token_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")