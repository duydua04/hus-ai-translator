from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.db import get_db
from app.config.settings import settings
from app.models.models import Admin
from app.schemas.common.auth_schemas import RegisterRequest
from app.schemas.admin.admin_schema import AdminResponse
from app.utils.security import hash_password

router = APIRouter(
    prefix="/api/internal",
    tags=["Setup Admin"]
)


@router.post(
    "/setup-admin",
    response_model=AdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Khởi tạo tài khoản Admin hệ thống"
)
async def create_initial_admin(
        payload: RegisterRequest,
        db: AsyncSession = Depends(get_db),
        x_admin_secret: str = Header(None, alias="X-Admin-Secret")
):
    """
    API tao Admin.
    """
    master_secret = settings.FIRST_ADMIN_SECRET
    if not x_admin_secret or x_admin_secret != master_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mã bí mật (Secret Key) không chính xác."
        )

    # 2. Kiểm tra Email đã tồn tại chưa
    stmt = select(Admin).where(Admin.email == payload.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Admin này đã tồn tại trong hệ thống."
        )

    # 3. Tạo Admin mới
    new_admin = Admin(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        is_active=True
    )

    db.add(new_admin)
    try:
        await db.commit()
        await db.refresh(new_admin)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lưu Admin: {str(e)}"
        )

    return new_admin