"""
schemas/user/chat_schema.py
-----------------------------
Schemas dành riêng cho tính năng trò chuyện AI của user.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator


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