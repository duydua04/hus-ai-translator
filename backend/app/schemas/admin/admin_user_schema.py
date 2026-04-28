import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel

from ..common.pagination_schema import PaginatedResponse

class UserResponseAdmin(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    tier: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class UserDetailResponse(UserResponseAdmin):
    """Chi tiết User, bổ sung thống kê hoạt động"""
    total_translations: int = 0
    total_feedbacks: int = 0

class UserListResponse(PaginatedResponse):
    data: List[UserResponseAdmin]