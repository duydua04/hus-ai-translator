"""
Middleware/auth.py
------------------
Quản lý session người dùng:
  - Đọc token từ Header Authorization hoặc Cookie
  - Giải mã, xác thực token
  - Kiểm tra role (scope) của người dùng
  - Query DB để trả về đối tượng User/Admin hiện tại
"""
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import SecurityScopes
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.db import get_db
from ..models.models import Admin, User
from ..utils.security import verify_access_token

KNOWN_ROLES = ["user", "admin"]


async def get_current_user(
    security_scopes: SecurityScopes,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency chính để xác thực người dùng.

    Thứ tự ưu tiên tìm token:
      1. Header: Authorization: Bearer <token>
      2. Cookie: access_token_<scope>  (theo scope yêu cầu)
      3. Cookie: access_token_<role>   (duyệt qua các role đã biết)

    Sau khi giải mã thành công sẽ kiểm tra scope rồi query DB
    để chắc chắn tài khoản vẫn tồn tại và đang hoạt động.
    """
    token: str | None = None

    # --- 1. Tìm token trong Authorization header ---
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]

    # --- 2. Tìm token trong Cookie theo scope được khai báo ---
    if not token and security_scopes.scopes:
        for scope in security_scopes.scopes:
            found = request.cookies.get(f"access_token_{scope}")
            if found:
                token = found
                break

    # --- 3. Fallback: thử tất cả role đã biết ---
    if not token:
        for role in KNOWN_ROLES:
            found = request.cookies.get(f"access_token_{role}")
            if found:
                token = found
                break

    # --- Không tìm thấy token ---
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thiếu access token. Vui lòng đăng nhập.",
            headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'},
        )

    # --- Giải mã token ---
    try:
        payload = verify_access_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token đã hết hạn. Vui lòng làm mới token.",
            headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token không hợp lệ.",
            headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'},
        )

    role: str = payload.get("role", "")
    sub: str = payload.get("sub", "")  # email

    # --- Kiểm tra scope (role) ---
    if security_scopes.scopes and role not in security_scopes.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Bạn không có quyền truy cập. Yêu cầu: {security_scopes.scope_str}",
        )

    # --- Query DB lấy đối tượng thực ---
    db_user = None
    if role == "admin":
        result = await db.execute(select(Admin).where(Admin.email == sub))
        db_user = result.scalar_one_or_none()
    elif role == "user":
        result = await db.execute(
            select(User).where(User.email == sub, User.is_active == True)
        )
        db_user = result.scalar_one_or_none()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị vô hiệu hóa.",
        )

    return {"role": role, "sub": sub, "user": db_user}


# =========================================================
# Dependency shortcut theo role
# =========================================================

def require_user(info=Security(get_current_user, scopes=["user"])):
    """Dependency: chỉ cho phép người dùng thường."""
    return info


def require_admin(info=Security(get_current_user, scopes=["admin"])):
    """Dependency: chỉ cho phép admin."""
    return info