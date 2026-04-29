"""
services/user/chat_service.py
------------------------------
Logic nghiệp vụ trò chuyện với AI:
  - Tạo phiên hội thoại mới
  - Gửi tin nhắn, nhận phản hồi từ AI (có nhớ ngữ cảnh)
  - Lấy lịch sử tin nhắn của một phiên
  - Liệt kê tất cả phiên của người dùng
  - Ghim / bỏ ghim phiên
  - Đổi tên phiên
  - Xóa phiên
"""
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import get_db
from app.models.models import ChatMessage, ChatSession
from app.schemas.user.chat_schema import (
    ChatHistoryResponse,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionListResponse,
    ChatSessionResponse,
    PinSessionRequest,
    SendMessageRequest,
)


# =========================================================
# STUB GỌI LLM — thay bằng utils/llm_client.py thực tế
# =========================================================
async def _call_llm_chat(messages: List[dict], model: str = "gpt-4o") -> str:
    """
    Stub gọi LLM với lịch sử hội thoại.
    Thực tế dùng OpenAI:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=model,
            messages=messages   # [{"role": "user"/"assistant"/"system", "content": "..."}]
        )
        return response.choices[0].message.content
    """
    last_user_msg = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
    )
    return f"[Phản hồi stub của AI cho: '{last_user_msg[:50]}...']"


def _estimate_tokens(text: str) -> int:
    """Ước tính số token (1 token ≈ 4 ký tự tiếng Anh, tiếng Việt thường nhiều hơn)."""
    return max(1, len(text) // 4)


class ChatService:
    """
    Quản lý toàn bộ vòng đời phiên hội thoại và tin nhắn.
    Mỗi phiên lưu lịch sử để AI có ngữ cảnh trả lời chính xác hơn.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------
    # TẠO PHIÊN MỚI
    # --------------------------------------------------
    async def create_session(
        self, user_id: str, payload: ChatSessionCreateRequest
    ) -> ChatSessionResponse:
        """
        Tạo phiên hội thoại mới.
        Title có thể truyền hoặc để AI tự tóm tắt sau khi có tin nhắn đầu tiên.
        """
        session = ChatSession(
            user_id=user_id,
            title=payload.title or "Phiên hội thoại mới",
            is_pinned=False,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return ChatSessionResponse.model_validate(session)

    # --------------------------------------------------
    # DANH SÁCH PHIÊN CỦA NGƯỜI DÙNG
    # --------------------------------------------------
    async def list_sessions(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> ChatSessionListResponse:
        """
        Lấy danh sách phiên hội thoại của người dùng.
        Sắp xếp: pinned lên đầu, rồi mới nhất.
        """
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.is_pinned.desc(), ChatSession.updated_at.desc())
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()

        return ChatSessionListResponse(
            total=total,
            limit=limit,
            offset=offset,
            data=[ChatSessionResponse.model_validate(s) for s in sessions],
        )

    # --------------------------------------------------
    # LẤY LỊCH SỬ TIN NHẮN CỦA MỘT PHIÊN
    # --------------------------------------------------
    async def get_session_history(
        self, user_id: str, session_id: str
    ) -> ChatHistoryResponse:
        """
        Lấy toàn bộ lịch sử tin nhắn của một phiên.
        Kiểm tra phiên thuộc về người dùng đang đăng nhập.
        """
        session = await self._get_session_or_404(session_id, user_id)

        msg_stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())   # Cũ → mới, đúng thứ tự hội thoại
        )
        msg_result = await self.db.execute(msg_stmt)
        messages = msg_result.scalars().all()

        return ChatHistoryResponse(
            session=ChatSessionResponse.model_validate(session),
            messages=[ChatMessageResponse.model_validate(m) for m in messages],
        )

    # --------------------------------------------------
    # GỬI TIN NHẮN VÀ NHẬN PHẢN HỒI AI
    # --------------------------------------------------
    async def send_message(
        self, user_id: str, session_id: str, payload: SendMessageRequest
    ) -> ChatMessageResponse:
        """
        Luồng xử lý gửi tin nhắn:
          1. Kiểm tra phiên tồn tại và thuộc về user
          2. Lưu tin nhắn của user vào DB
          3. Tải toàn bộ lịch sử hội thoại (để AI có ngữ cảnh)
          4. Gọi LLM với lịch sử đầy đủ
          5. Lưu phản hồi AI vào DB
          6. Cập nhật updated_at của session để sort đúng thứ tự
          7. Tự động cập nhật title phiên nếu đang là mặc định
          8. Trả về tin nhắn AI vừa tạo
        """
        session = await self._get_session_or_404(session_id, user_id)

        # Lưu tin nhắn của user
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=payload.content,
            token_count=_estimate_tokens(payload.content),
        )
        self.db.add(user_msg)
        await self.db.flush()   # flush để có id nhưng chưa commit

        # Tải toàn bộ lịch sử để gửi lên LLM
        history_stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        history_result = await self.db.execute(history_stmt)
        all_messages = history_result.scalars().all()

        # Chuyển lịch sử thành format OpenAI messages
        llm_messages = [
            {"role": m.role, "content": m.content}
            for m in all_messages
        ]

        # Gọi LLM
        try:
            ai_content = await _call_llm_chat(llm_messages)
        except Exception as e:
            ai_content = f"Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn: {str(e)}"

        # Lưu phản hồi AI
        ai_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=ai_content,
            token_count=_estimate_tokens(ai_content),
        )
        self.db.add(ai_msg)

        # Cập nhật updated_at của session và tự đặt title nếu chưa có
        from datetime import datetime, timezone
        session.updated_at = datetime.now(timezone.utc)

        if session.title == "Phiên hội thoại mới":
            # Tóm tắt tiêu đề từ 6 từ đầu của tin nhắn user
            words = payload.content.split()
            session.title = " ".join(words[:6]) + ("..." if len(words) > 6 else "")

        await self.db.commit()
        await self.db.refresh(ai_msg)
        return ChatMessageResponse.model_validate(ai_msg)

    # --------------------------------------------------
    # GHIM / BỎ GHIM PHIÊN
    # --------------------------------------------------
    async def pin_session(
        self, user_id: str, session_id: str, payload: PinSessionRequest
    ) -> ChatSessionResponse:
        """Ghim hoặc bỏ ghim phiên. Phiên ghim luôn hiển thị đầu danh sách."""
        session = await self._get_session_or_404(session_id, user_id)
        session.is_pinned = payload.is_pinned
        await self.db.commit()
        await self.db.refresh(session)
        return ChatSessionResponse.model_validate(session)

    # --------------------------------------------------
    # ĐỔI TÊN PHIÊN
    # --------------------------------------------------
    async def rename_session(
        self, user_id: str, session_id: str, new_title: str
    ) -> ChatSessionResponse:
        """Đổi tiêu đề phiên hội thoại."""
        if not new_title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tiêu đề phiên không được để trống.",
            )
        session = await self._get_session_or_404(session_id, user_id)
        session.title = new_title.strip()
        await self.db.commit()
        await self.db.refresh(session)
        return ChatSessionResponse.model_validate(session)

    # --------------------------------------------------
    # XÓA PHIÊN
    # --------------------------------------------------
    async def delete_session(self, user_id: str, session_id: str) -> dict:
        """
        Xóa phiên và toàn bộ tin nhắn bên trong.
        Cascade delete đã cấu hình trong model ChatSession → ChatMessage.
        """
        session = await self._get_session_or_404(session_id, user_id)
        await self.db.delete(session)
        await self.db.commit()
        return {"message": "Đã xóa phiên hội thoại thành công."}

    # --------------------------------------------------
    # HELPER NỘI BỘ
    # --------------------------------------------------
    async def _get_session_or_404(self, session_id: str, user_id: str) -> ChatSession:
        """Lấy session và đảm bảo thuộc về user đang đăng nhập."""
        stmt = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phiên hội thoại không tồn tại hoặc không thuộc về tài khoản của bạn.",
            )
        return session


def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(db)