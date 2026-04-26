"""
api/admin/admin_router.py
--------------------------
Router quản trị admin.
Không chứa logic nghiệp vụ - chỉ gọi AdminService.
Tất cả endpoint (trừ login) đều yêu cầu require_admin dependency.
"""
from typing import Optional
import os
from fastapi import APIRouter, Depends, HTTPException, Response, status, Header
from dotenv import load_dotenv

load_dotenv()
from ...middleware.auth import require_admin
from ...schemas.schemas import (
    AdminCreateRequest,
    AdminResponse,
    ChangeUserTierRequest,
    LoginRequest,
    OAuth2Token,
    UserListResponse,
    UserResponse,
)
from ...services.admin.admin_service import AdminService, get_admin_service
from ...utils.security import set_auth_cookies

router = APIRouter(prefix="/admin", tags=["Admin"])


# =========================================================
# ĐĂNG NHẬP ADMIN (public - không cần token)
# =========================================================

@router.post("/login", response_model=OAuth2Token)
async def admin_login(
    payload: LoginRequest,
    response: Response,
    service: AdminService = Depends(get_admin_service),
):
    """Đăng nhập tài khoản admin."""
    token_data = await service.login(payload)
    set_auth_cookies(response, token_data.access_token, token_data.refresh_token, role="admin")
    return token_data


# =========================================================
# ĐĂNG XUẤT ADMIN
# =========================================================

@router.post("/logout")
def admin_logout(
    response: Response,
    service: AdminService = Depends(get_admin_service),
    _=Depends(require_admin),
):
    """Đăng xuất admin: xóa cookie."""
    return service.logout(response)


# =========================================================
# TẠO TÀI KHOẢN ADMIN MỚI (chỉ admin mới tạo được)
# =========================================================

@router.post("/create-admin", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
async def create_admin(
    payload: AdminCreateRequest,
    service: AdminService = Depends(get_admin_service),
    # Thêm Header 'X-Admin-Secret' vào tham số
    x_admin_secret: str = Header(None, alias="X-Admin-Secret")
):
    """
    Tạo tài khoản admin mới.
    Cho phép nếu: 
    1. Có X-Admin-Secret đúng trong Header.
    2. (Tùy chọn) Hoặc có token Admin hợp lệ (nếu bạn muốn giữ logic cũ).
    """
    
    # 1. Lấy mã bí mật từ file .env hoặc mặc định
    # Bạn nên đặt FIRST_ADMIN_SECRET trong file .env
    expected_secret = os.getenv("FIRST_ADMIN_SECRET", "admin_secret_key_123")

    # 2. Kiểm tra Secret Key
    if x_admin_secret and x_admin_secret == expected_secret:
        # Nếu mã bí mật khớp, tiến hành tạo luôn không cần check token
        return await service.create_admin(payload)

    # 3. Nếu Secret Key sai hoặc không gửi, trả về lỗi 403
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Bạn cần cung cấp X-Admin-Secret chính xác để thực hiện thao tác này."
    )

# =========================================================
# QUẢN LÝ TÀI KHOẢN NGƯỜI DÙNG
# =========================================================

@router.get("/users", response_model=UserListResponse)
async def list_users(
    search: Optional[str] = None,
    tier: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
    service: AdminService = Depends(get_admin_service),
    _=Depends(require_admin),
):
    """
    Lấy danh sách người dùng với bộ lọc:
    - search : tìm theo email hoặc họ tên
    - tier   : free | pro | enterprise
    - is_active: true | false
    Hỗ trợ phân trang: limit + offset.
    """
    return await service.list_users(
        search=search,
        tier=tier,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: str,
    service: AdminService = Depends(get_admin_service),
    _=Depends(require_admin),
):
    """Xem chi tiết một tài khoản người dùng."""
    return await service.get_user_detail(user_id)


@router.patch("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    service: AdminService = Depends(get_admin_service),
    _=Depends(require_admin),
):
    """Mở khóa tài khoản người dùng."""
    return await service.toggle_user_active(user_id, is_active=True)


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    service: AdminService = Depends(get_admin_service),
    _=Depends(require_admin),
):
    """Khóa tài khoản người dùng. Token hiện tại của user sẽ bị từ chối ngay."""
    return await service.toggle_user_active(user_id, is_active=False)


@router.patch("/users/{user_id}/tier", response_model=UserResponse)
async def change_user_tier(
    user_id: str,
    payload: ChangeUserTierRequest,
    service: AdminService = Depends(get_admin_service),
    _=Depends(require_admin),
):
    """Admin thay đổi gói dịch vụ của người dùng (free / pro / enterprise)."""
    return await service.change_user_tier(user_id, payload)


# =========================================================
# QUẢN LÝ PHIÊN CHAT (SESSION)
# =========================================================

@router.get("/sessions/stats")
async def session_stats(
    user_id: Optional[str] = None,
    service: AdminService = Depends(get_admin_service),
    _=Depends(require_admin),
):
    """
    Thống kê tổng số phiên chat trên toàn hệ thống.
    Nếu truyền user_id thì lọc theo user đó.
    """
    return await service.get_session_stats(user_id=user_id)


@router.get("/users/{user_id}/sessions")
async def list_user_sessions(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    service: AdminService = Depends(get_admin_service),
    _=Depends(require_admin),
):
    """Admin xem toàn bộ lịch sử phiên chat của một người dùng."""
    return await service.list_user_sessions(user_id=user_id, limit=limit, offset=offset)