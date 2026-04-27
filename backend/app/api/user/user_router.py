"""
api/user/user_router.py
------------------------
Router hồ sơ người dùng.
Tất cả endpoint đều yêu cầu đăng nhập (require_user).
"""
from fastapi import APIRouter, Depends

from ...middleware.auth import require_user
from ...schemas.schemas import ChangePasswordRequest, UserResponse, UserUpdateRequest
from ...services.user.profile_service import UserProfileService, get_user_profile_service

router = APIRouter(prefix="/user", tags=["User - Hồ sơ cá nhân"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    info=Depends(require_user),
    service: UserProfileService = Depends(get_user_profile_service),
):
    """Xem thông tin hồ sơ cá nhân."""
    user_id = str(info["user"].id)
    return await service.get_profile(user_id)


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    payload: UserUpdateRequest,
    info=Depends(require_user),
    service: UserProfileService = Depends(get_user_profile_service),
):
    """Cập nhật họ tên và / hoặc ngôn ngữ mặc định. Chỉ truyền trường cần thay đổi."""
    user_id = str(info["user"].id)
    return await service.update_profile(user_id, payload)


@router.patch("/password")
async def change_password(
    payload: ChangePasswordRequest,
    info=Depends(require_user),
    service: UserProfileService = Depends(get_user_profile_service),
):
    """Đổi mật khẩu khi đang đăng nhập. Yêu cầu nhập mật khẩu hiện tại để xác nhận."""
    user_id = str(info["user"].id)
    return await service.change_password(user_id, payload)