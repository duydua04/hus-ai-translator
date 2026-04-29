from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.middleware.auth import require_admin
from app.schemas.admin.admin_user_schema import UserDetailResponse, UserListResponse
from app.services.admin.admin_user_service import AdminUserService, get_admin_user_service

router = APIRouter(
    prefix="/api/admin/users",
    tags=["Admin - Quản lý Người dùng"],
    dependencies=[Depends(require_admin)]
)

@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    tier: Optional[str] = Query(None),
    service: AdminUserService = Depends(get_admin_user_service)
):
    return await service.get_users(page, limit, search, is_active, tier)

@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(user_id: str, service: AdminUserService = Depends(get_admin_user_service)):
    return await service.get_user_detail(user_id)

@router.patch("/{user_id}/status")
async def toggle_user_status(
    user_id: str,
    is_active: bool = Query(..., description="True (mở khóa), False (khóa)"),
    service: AdminUserService = Depends(get_admin_user_service)
):
    return await service.toggle_user_status(user_id, is_active)

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: str, service: AdminUserService = Depends(get_admin_user_service)):
    return await service.delete_user(user_id)