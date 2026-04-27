from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ...schemas.auth_schemas import (
    RegisterRequest,
    UserResponse,
    LoginRequest,
    OAuth2Token
)
from ...services.common.auth_service import AuthService, get_auth_service

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Create a new user account
    """
    new_user = await auth_service.register_user(payload)
    return new_user


@router.post(
    "/token",
    response_model=OAuth2Token,
    summary="Login (OAuth2 Form Standard)"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login using the OAuth2
    """
    role = form_data.scopes[0] if form_data.scopes else "user"
    token_data = await auth_service.authenticate_user(
        email=form_data.username,
        password=form_data.password,
        role=role
    )
    return token_data


@router.post(
    "/login",
    response_model=OAuth2Token,
    summary="Login (JSON Body)"
)
async def login_json(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login using a JSON Body.
    """
    token_data = await auth_service.authenticate_user(
        email=payload.email,
        password=payload.password,
        role="user"
    )
    return token_data