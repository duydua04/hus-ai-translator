"""
api/auth/auth_router.py
------------------------
Router xác thực người dùng thường.
Không chứa logic nghiệp vụ - chỉ gọi AuthService.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from ...middleware.auth import require_admin, require_user
from ...schemas.admin.admin_schema import AdminResponse
from ...schemas.common.auth_schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    OAuth2Token,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
    VerifyOTPRequest,
)
from ...services.common.auth_service import AuthService, get_auth_service
from ...services.admin.admin_service import AdminService, get_admin_service
from ...utils.security import set_auth_cookies
from ...config.settings import settings

router = APIRouter(prefix="/auth", tags=["Auth - Người dùng"])


# =========================================================
# THÔNG TIN CÁ NHÂN (dùng để kiểm tra session)
# =========================================================

@router.get("/me", response_model=UserResponse)
def get_me(info=Depends(require_user)):
    """Trả về thông tin người dùng đang đăng nhập từ session hiện tại."""
    return UserResponse.model_validate(info["user"])


# =========================================================
# ĐĂNG KÝ
# =========================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Đăng ký tài khoản người dùng mới."""
    return await service.register(payload)


# =========================================================
# ĐĂNG NHẬP
# =========================================================

@router.post("/login", response_model=OAuth2Token)
async def login(
    payload: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """
    Đăng nhập và nhận cặp token.
    Token được đặt vào HttpOnly Cookie tự động.
    """
    token_data = await service.login(payload)
    set_auth_cookies(response, token_data.access_token, token_data.refresh_token, role="user")
    return token_data


# =========================================================
# LÀM MỚI TOKEN
# =========================================================

@router.post("/refresh", response_model=OAuth2Token)
async def refresh_token(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """
    Cấp lại access token từ refresh token trong Cookie.
    Client không cần gửi token thủ công.
    """
    refresh_token = request.cookies.get("refresh_token_user")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy refresh token trong cookie.",
        )

    new_token = await service.refresh_token(refresh_token)
    set_auth_cookies(response, new_token.access_token, new_token.refresh_token, role="user")
    return new_token


# =========================================================
# ĐĂNG XUẤT
# =========================================================

@router.post("/logout")
def logout(
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """Đăng xuất: xóa tất cả auth cookie."""
    return service.logout(response)


# =========================================================
# QUÊN MẬT KHẨU - BƯỚC 1: Gửi OTP
# =========================================================

@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """
    Bước 1: Nhận email, gửi OTP và set reset_token vào Cookie.
    Luôn trả về thành công dù email có tồn tại hay không (bảo mật).
    """
    result = await service.forgot_password_request(payload.email)

    if "reset_token" in result:
        response.set_cookie(
            key="reset_token",
            value=result["reset_token"],
            httponly=True,
            samesite="lax",
            secure=settings.is_production,
            max_age=settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES * 60,
        )

    return {"message": result["message"], "_dev_otp": result.get("_dev_otp")}


# =========================================================
# QUÊN MẬT KHẨU - BƯỚC 2: Xác thực OTP
# =========================================================

@router.post("/verify-otp")
def verify_otp(
    payload: VerifyOTPRequest,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """
    Bước 2: Xác thực OTP. Nếu đúng, đổi cookie thành permission_token.
    permission_token có hiệu lực 5 phút để đặt mật khẩu mới.
    """
    reset_token = request.cookies.get("reset_token")
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phiên đặt lại mật khẩu không tồn tại hoặc đã hết hạn.",
        )

    result = service.verify_otp(payload.otp, reset_token)

    # Đổi cookie sang permission_token
    response.set_cookie(
        key="reset_token",
        value=result["permission_token"],
        httponly=True,
        samesite="lax",
        secure=settings.is_production,
        max_age=5 * 60,
    )

    return {"message": result["message"]}


# =========================================================
# QUÊN MẬT KHẨU - BƯỚC 3: Đặt mật khẩu mới
# =========================================================

@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """
    Bước 3: Đặt lại mật khẩu mới.
    Yêu cầu permission_token hợp lệ trong Cookie (nhận từ bước 2).
    """
    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu xác nhận không khớp.",
        )

    permission_token = request.cookies.get("reset_token")
    if not permission_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phiên đặt lại mật khẩu không hợp lệ.",
        )

    result = await service.reset_password(payload.new_password, permission_token)
    response.delete_cookie("reset_token")

    return result

# =========================================================
# ADMIN — ĐĂNG NHẬP / REFRESH / LOGOUT / ME
# =========================================================
 
@router.post("/admin/login", response_model=OAuth2Token)
async def admin_login(
    payload: LoginRequest,
    response: Response,
    service: AdminService = Depends(get_admin_service),
):
    """Đăng nhập admin. Token đặt vào HttpOnly Cookie tự động."""
    token_data = await service.login(payload)
    set_auth_cookies(response, token_data.access_token, token_data.refresh_token, role="admin")
    return token_data
 
 
@router.post("/admin/refresh", response_model=OAuth2Token)
async def admin_refresh_token(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """Cấp lại access token admin từ refresh token trong Cookie."""
    token = request.cookies.get("refresh_token_admin")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy refresh token trong cookie.",
        )
    new_token = await service.refresh_token(token)
    set_auth_cookies(response, new_token.access_token, new_token.refresh_token, role="admin")
    return new_token
 
 
@router.post("/admin/logout")
def admin_logout(
    response: Response,
    service: AdminService = Depends(get_admin_service),
    _=Depends(require_admin),
):
    """Đăng xuất admin: xóa cookie."""
    return service.logout(response)
 
 
@router.get("/admin/me", response_model=AdminResponse)
def admin_get_me(info=Depends(require_admin)):
    """Thông tin admin đang đăng nhập."""
    return AdminResponse.model_validate(info["user"])


# =========================================================
# SWAGGER UI — OAuth2 token endpoint
# Dùng riêng cho nút Authorize trên Swagger docs.
# Nhập username = email, password = mật khẩu.
# Chọn scope: "user" hoặc "admin".
# =========================================================
 
 
@router.post("/token", response_model=OAuth2Token, include_in_schema=False)
async def swagger_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Endpoint riêng cho Swagger Authorize.
    Chọn scope 'user' hoặc 'admin' để đăng nhập đúng vai trò.
    """
    role = form_data.scopes[0] if form_data.scopes else "user"
 
    if role == "admin":
        return await admin_service.login(
            LoginRequest(email=form_data.username, password=form_data.password)
        )
    return await service.authenticate_user(form_data.username, form_data.password, role="user")