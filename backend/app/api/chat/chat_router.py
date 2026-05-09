"""
api/chat/chat_router.py
------------------------
Router trò chuyện với AI.
Tất cả endpoint đều yêu cầu đăng nhập (require_user).
"""
from fastapi import APIRouter, Depends, status

from ...middleware.auth import require_user
from ...schemas.user.chat_schema import (
    ChatHistoryResponse,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionListResponse,
    ChatSessionResponse,
    PinSessionRequest,
    SendMessageRequest,
)
from ...services.user.chat_service import ChatService, get_chat_service

router = APIRouter(prefix="/chat", tags=["Chat - Trò chuyện AI"])


# =========================================================
# QUẢN LÝ PHIÊN HỘI THOẠI
# =========================================================

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: ChatSessionCreateRequest,
    info=Depends(require_user),
    service: ChatService = Depends(get_chat_service),
):
    """Tạo phiên hội thoại mới. Title có thể để trống, AI sẽ tự đặt sau tin nhắn đầu tiên."""
    user_id = str(info["user"].id)
    return await service.create_session(user_id, payload)


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(
    limit: int = 20,
    offset: int = 0,
    info=Depends(require_user),
    service: ChatService = Depends(get_chat_service),
):
    """Danh sách phiên hội thoại. Phiên ghim lên đầu, rồi mới nhất."""
    user_id = str(info["user"].id)
    return await service.list_sessions(user_id, limit=limit, offset=offset)


@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
async def get_session_history(
    session_id: str,
    info=Depends(require_user),
    service: ChatService = Depends(get_chat_service),
):
    """Lấy toàn bộ lịch sử tin nhắn của một phiên hội thoại."""
    user_id = str(info["user"].id)
    return await service.get_session_history(user_id, session_id)


@router.patch("/sessions/{session_id}/pin", response_model=ChatSessionResponse)
async def pin_session(
    session_id: str,
    payload: PinSessionRequest,
    info=Depends(require_user),
    service: ChatService = Depends(get_chat_service),
):
    """Ghim hoặc bỏ ghim phiên hội thoại. Truyền is_pinned: true/false."""
    user_id = str(info["user"].id)
    return await service.pin_session(user_id, session_id, payload)


@router.patch("/sessions/{session_id}/rename", response_model=ChatSessionResponse)
async def rename_session(
    session_id: str,
    body: dict,
    info=Depends(require_user),
    service: ChatService = Depends(get_chat_service),
):
    """Đổi tiêu đề phiên hội thoại. Body: { 'title': 'Tiêu đề mới' }"""
    user_id = str(info["user"].id)
    new_title = body.get("title", "")
    return await service.rename_session(user_id, session_id, new_title)


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    info=Depends(require_user),
    service: ChatService = Depends(get_chat_service),
):
    """Xóa phiên hội thoại và toàn bộ tin nhắn bên trong."""
    user_id = str(info["user"].id)
    return await service.delete_session(user_id, session_id)


# =========================================================
# TIN NHẮN
# =========================================================

@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    session_id: str,
    payload: SendMessageRequest,
    info=Depends(require_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Gửi tin nhắn vào một phiên hội thoại.
    AI trả lời dựa trên toàn bộ ngữ cảnh hội thoại trước đó.
    Response là tin nhắn của AI.
    """
    user_id = str(info["user"].id)
    return await service.send_message(user_id, session_id, payload)