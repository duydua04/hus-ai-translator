"""
services/admin/admin_service.py
--------------------------------
Toàn bộ logic nghiệp vụ của admin:
  - Đăng nhập admin
  - Quản lý tài khoản người dùng (xem, khóa, đổi tier)
  - Tạo tài khoản admin mới
  - Thống kê phiên làm việc (chat sessions)
"""
from typing import Optional

from fastapi import Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...models.models import Admin, ChatSession, User
from ...schemas.schemas import (
    AdminCreateRequest,
    AdminResponse,
    ChangeUserTierRequest,
    LoginRequest,
    OAuth2Token,
    UserListResponse,
    UserResponse,
)
from ...utils.security import (
    delete_auth_cookies,
    hash_password,
    issue_token_pair,
    verify_password,
)


class AdminService:
    """
    Chứa toàn bộ logic nghiệp vụ admin.
    API layer chỉ gọi đến service này, không chứa logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------
    # ĐĂNG NHẬP ADMIN
    # --------------------------------------------------
    async def login(self, payload: LoginRequest) -> OAuth2Token:
        """
        Đăng nhập admin: xác thực email + mật khẩu.
        Chỉ cho phép tài khoản admin đang hoạt động.
        """
        stmt = select(Admin).where(Admin.email == payload.email)
        result = await self.db.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin or not verify_password(payload.password, admin.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu admin không đúng.",
            )

        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản admin đã bị vô hiệu hóa.",
            )

        return issue_token_pair(email=admin.email, role="admin")

    # --------------------------------------------------
    # ĐĂNG XUẤT ADMIN
    # --------------------------------------------------
    @staticmethod
    def logout(response: Response) -> dict:
        """Xóa cookie admin. Static method - không cần DB."""
        delete_auth_cookies(response, role="admin")
        return {"message": "Admin đăng xuất thành công."}

    # --------------------------------------------------
    # TẠO TÀI KHOẢN ADMIN MỚI
    # --------------------------------------------------
    async def create_admin(self, payload: AdminCreateRequest) -> AdminResponse:
        """
        Tạo tài khoản admin mới.
        Kiểm tra email chưa bị trùng trong bảng admins.
        """
        stmt = select(Admin).where(Admin.email == payload.email)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email admin đã tồn tại.",
            )

        new_admin = Admin(
            email=payload.email,
            full_name=payload.full_name.strip(),
            hashed_password=hash_password(payload.password),
            is_active=True,
        )
        self.db.add(new_admin)
        await self.db.commit()
        await self.db.refresh(new_admin)

        return AdminResponse.model_validate(new_admin)

    # --------------------------------------------------
    # DANH SÁCH NGƯỜI DÙNG (có tìm kiếm + phân trang)
    # --------------------------------------------------
    async def list_users(
        self,
        search: Optional[str] = None,
        tier: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> UserListResponse:
        """
        Lấy danh sách người dùng với bộ lọc:
        - search: tìm theo email hoặc full_name (LIKE)
        - tier   : lọc theo gói dịch vụ
        - is_active: lọc theo trạng thái
        Hỗ trợ phân trang qua limit + offset.
        """
        stmt = select(User)

        # --- Điều kiện lọc ---
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                (User.email.ilike(pattern)) | (User.full_name.ilike(pattern))
            )
        if tier:
            stmt = stmt.where(User.tier == tier)
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        # --- Đếm tổng (cho pagination) ---
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        # --- Lấy dữ liệu theo trang ---
        stmt = stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        users = result.scalars().all()

        return UserListResponse(
            total=total,
            limit=limit,
            offset=offset,
            data=[UserResponse.model_validate(u) for u in users],
        )

    # --------------------------------------------------
    # XEM CHI TIẾT NGƯỜI DÙNG
    # --------------------------------------------------
    async def get_user_detail(self, user_id: str) -> UserResponse:
        """Lấy chi tiết một người dùng theo UUID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng.",
            )

        return UserResponse.model_validate(user)

    # --------------------------------------------------
    # KHÓA / MỞ KHÓA TÀI KHOẢN
    # --------------------------------------------------
    async def toggle_user_active(self, user_id: str, is_active: bool) -> dict:
        """
        Khóa (is_active=False) hoặc mở khóa (is_active=True) tài khoản.
        Khi khóa, token hiện tại của user sẽ bị từ chối ở middleware
        (middleware kiểm tra is_active khi query DB).
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng.",
            )

        user.is_active = is_active
        await self.db.commit()

        action = "mở khóa" if is_active else "khóa"
        return {"message": f"Đã {action} tài khoản {user.email} thành công."}

    # --------------------------------------------------
    # ĐỔI GÓI DỊCH VỤ (TIER)
    # --------------------------------------------------
    async def change_user_tier(self, user_id: str, payload: ChangeUserTierRequest) -> UserResponse:
        """Admin thay đổi gói dịch vụ của người dùng."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng.",
            )

        user.tier = payload.tier
        await self.db.commit()
        await self.db.refresh(user)

        return UserResponse.model_validate(user)

    # --------------------------------------------------
    # THỐNG KÊ CHAT SESSION
    # --------------------------------------------------
    async def get_session_stats(self, user_id: Optional[str] = None) -> dict:
        """
        Thống kê phiên trò chuyện:
        - Tổng số session
        - Số session được ghim
        - Nếu truyền user_id thì lọc theo user đó
        """
        stmt_total = select(func.count(ChatSession.id))
        stmt_pinned = select(func.count(ChatSession.id)).where(ChatSession.is_pinned == True)

        if user_id:
            stmt_total = stmt_total.where(ChatSession.user_id == user_id)
            stmt_pinned = stmt_pinned.where(ChatSession.user_id == user_id)

        total_result = await self.db.execute(stmt_total)
        pinned_result = await self.db.execute(stmt_pinned)

        return {
            "total_sessions": total_result.scalar_one(),
            "pinned_sessions": pinned_result.scalar_one(),
        }

    # --------------------------------------------------
    # XEM DANH SÁCH PHIÊN CHAT CỦA MỘT USER
    # --------------------------------------------------
    async def list_user_sessions(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """Admin xem toàn bộ phiên chat của một user cụ thể."""
        # Kiểm tra user tồn tại
        user_stmt = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng.",
            )

        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()

        count_stmt = select(func.count(ChatSession.id)).where(ChatSession.user_id == user_id)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        return {
            "user_id": user_id,
            "total": total,
            "limit": limit,
            "offset": offset,
            "sessions": [
                {
                    "id": str(s.id),
                    "title": s.title,
                    "is_pinned": s.is_pinned,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                }
                for s in sessions
            ],
        }


# Factory để FastAPI Depends inject
def get_admin_service(db: AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(db)