from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.db import get_db
from ...models.models import Admin, User
from ...schemas.auth_schemas import RegisterRequest, OAuth2Token
from ...utils.security import hash_password, verify_password, issue_token_pair


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, payload: RegisterRequest) -> User:
        """
        Dang ky user
        """
        stmt = select(User).where(User.email == payload.email)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already registered."
            )

        hashed_pw = hash_password(payload.password)

        new_user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hashed_pw
        )

        self.db.add(new_user)
        try:
            await self.db.commit()
            await self.db.refresh(new_user)
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while saving to the database."
            )

        return new_user

    async def authenticate_user(self, email: str, password: str, role: str = "user") -> OAuth2Token:
        """
        Authenticate user and return a token pair (Access & Refresh).
        Supports both 'user' and 'admin' roles.
        """
        user_obj = None

        # 1. Find user by role
        if role == "admin":
            stmt = select(Admin).where(Admin.email == email)
            result = await self.db.execute(stmt)
            user_obj = result.scalar_one_or_none()
        else:
            stmt = select(User).where(User.email == email)
            result = await self.db.execute(stmt)
            user_obj = result.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not getattr(user_obj, "is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been disabled."
            )

        if not verify_password(password, user_obj.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return issue_token_pair(email=email, role=role)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)