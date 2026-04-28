from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ...schemas.common.auth_schemas import (
    RegisterRequest,
    UserResponse,
    LoginRequest,
    OAuth2Token,
    RefreshTokenRequest
)
from ...services.common.auth_service import AuthService, get_auth_service

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        payload: RegisterRequest,
        service: AuthService = Depends(get_auth_service)
):
    """Đăng ký tài khoản người dùng."""
    return await service.register_user(payload)

@router.post("/login", response_model=OAuth2Token, summary="User Login")
async def user_login(
        payload: LoginRequest,
        service: AuthService = Depends(get_auth_service)
):
    """Đăng nhập dành cho người dùng thông thường (JSON)."""
    return await service.authenticate_user(
        payload.email,
        payload.password,
        role="user"
    )

@router.post("/admin/login", response_model=OAuth2Token, summary="Admin Login")
async def admin_login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    """Đăng nhập dành cho quản trị viên (JSON)."""
    return await service.authenticate_user(
        payload.email,
        payload.password,
        role="admin"
    )

@router.post("/refresh", response_model=OAuth2Token)
async def refresh(
        payload: RefreshTokenRequest,
        service: AuthService = Depends(get_auth_service)
):
    """Làm mới Access Token."""
    return await service.refresh_token(payload.refresh_token)

@router.post("/token", response_model=OAuth2Token, include_in_schema=True)
async def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    """Cổng đăng nhập chuẩn OAuth2 để sử dụng nút Authorize trên Swagger UI."""
    role = form_data.scopes[0] if form_data.scopes else "user"
    return await service.authenticate_user(form_data.username, form_data.password, role=role)