"""
Package utils/security.py
--------------------------
Tập hợp các hàm tiện ích bảo mật:
  - Băm mật khẩu (hash / verify)
  - Tạo & giải mã JWT token (access, refresh, reset)
  - Set / xóa HttpOnly Cookie
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
import jwt
from fastapi import Response
from jwt import ExpiredSignatureError, InvalidTokenError

from ..config.settings import settings
from ..schemas.schemas import OAuth2Token


# =========================================================
# MẬT KHẨU
# =========================================================

def hash_password(plain: str) -> str:
    """Băm mật khẩu thô bằng bcrypt trước khi lưu vào DB."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """So khớp mật khẩu người dùng nhập với hash đã lưu trong DB."""
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# =========================================================
# JWT TOKEN
# =========================================================

def create_access_token(
    sub: str,
    role: str,
    expires_minutes: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None
) -> str:
    """
    Tạo JWT access token.
    - sub   : email của người dùng
    - role  : 'user' hoặc 'admin'
    - extra : payload bổ sung (dùng cho reset-password token)
    """
    if expires_minutes is None:
        expires_minutes = settings.OAUTH2_ACCESS_TOKEN_EXPIRE_MINUTES

    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "type": "access_token",
    }
    if extra:
        payload.update(extra)

    return jwt.encode(payload, settings.OAUTH2_SECRET_KEY, algorithm=settings.OAUTH2_ALGORITHM)


def create_refresh_token(sub: str, role: str, expires_days: Optional[int] = None) -> str:
    """
    Tạo JWT refresh token dùng để cấp lại access token khi hết hạn.
    Có thêm jti (JWT ID) để hỗ trợ thu hồi token sau này.
    """
    if expires_days is None:
        expires_days = settings.OAUTH2_REFRESH_TOKEN_EXPIRE_DAYS

    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=expires_days)).timestamp()),
        "type": "refresh_token",
        "jti": secrets.token_urlsafe(16),   # JWT unique ID
    }

    return jwt.encode(payload, settings.OAUTH2_SECRET_KEY, algorithm=settings.OAUTH2_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Giải mã JWT token và trả về payload.
    Ném ExpiredSignatureError hoặc InvalidTokenError nếu token không hợp lệ.
    """
    try:
        return jwt.decode(
            token,
            settings.OAUTH2_SECRET_KEY,
            algorithms=[settings.OAUTH2_ALGORITHM]
        )
    except ExpiredSignatureError:
        raise
    except InvalidTokenError:
        raise


def verify_access_token(token: str) -> Dict[str, Any]:
    """Giải mã và kiểm tra type của access token."""
    payload = decode_token(token)
    if payload.get("type") != "access_token":
        raise InvalidTokenError("Không phải access token hợp lệ")
    return payload


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """Giải mã và kiểm tra type của refresh token."""
    payload = decode_token(token)
    if payload.get("type") != "refresh_token":
        raise InvalidTokenError("Không phải refresh token hợp lệ")
    return payload


def issue_token_pair(email: str, role: str) -> OAuth2Token:
    """
    Tạo cặp (access_token, refresh_token) và đóng gói vào OAuth2Token.
    Dùng sau khi đăng nhập thành công.
    """
    access_token = create_access_token(sub=email, role=role)
    refresh_token = create_refresh_token(sub=email, role=role)

    return OAuth2Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.OAUTH2_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=role
    )


# =========================================================
# COOKIE
# =========================================================

def _cookie_params() -> Dict[str, Any]:
    """Tham số cookie dùng chung: httponly, samesite, secure theo môi trường."""
    return {
        "httponly": True,
        "samesite": "lax",
        "secure": settings.is_production,
    }


def set_auth_cookies(response: Response, access_token: str, refresh_token: str, role: str) -> None:
    """
    Đặt access_token và refresh_token vào HttpOnly Cookie.
    Tên cookie được gắn theo role để tránh xung đột (vd: access_token_user).
    """
    params = _cookie_params()

    response.set_cookie(
        key=f"access_token_{role}",
        value=access_token,
        path="/",
        max_age=settings.OAUTH2_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **params
    )
    response.set_cookie(
        key=f"refresh_token_{role}",
        value=refresh_token,
        path="/auth/refresh",
        max_age=settings.OAUTH2_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        **params
    )


def delete_auth_cookies(response: Response, role: Optional[str] = None) -> None:
    """
    Xóa cookie khi đăng xuất.
    Nếu role=None thì xóa tất cả role đã biết.
    """
    params = _cookie_params()
    known_roles = ["user", "admin"]

    targets = [role] if role else known_roles
    for r in targets:
        response.delete_cookie(key=f"access_token_{r}", path="/", **params)
        response.delete_cookie(key=f"refresh_token_{r}", path="/auth/refresh", **params)