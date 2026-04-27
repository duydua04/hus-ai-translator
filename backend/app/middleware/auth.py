from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.db import get_db
from ..models.models import Admin, User
from ..utils.security import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",  # Đường dẫn này phải khớp với router đăng nhập của bạn
    scopes={
        "user": "User Role",
        "admin": "Admin Role"
    }
)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Dependency chính để xác thực qua Header"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    try:
        payload = verify_access_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token đã hết hạn. Vui lòng làm mới token.",
            headers={"WWW-Authenticate": authenticate_value},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token không hợp lệ.",
            headers={"WWW-Authenticate": authenticate_value},
        )

    role: str = payload.get("role", "")
    sub: str = payload.get("sub", "")

    if security_scopes.scopes and role not in security_scopes.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Bạn không có quyền truy cập. Yêu cầu quyền: {security_scopes.scope_str}",
        )

    # Truy vấn DB
    db_user = None
    if role == "admin":
        result = await db.execute(select(Admin).where(Admin.email == sub))
        db_user = result.scalar_one_or_none()
    elif role == "user":
        result = await db.execute(select(User).where(User.email == sub, User.is_active == True))
        db_user = result.scalar_one_or_none()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị vô hiệu hóa.",
            headers={"WWW-Authenticate": authenticate_value},
        )

    return {"role": role, "sub": sub, "user": db_user}

def require_user(info=Security(get_current_user, scopes=["user"])):
    return info

def require_admin(info=Security(get_current_user, scopes=["admin"])):
    return info