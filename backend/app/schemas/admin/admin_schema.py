import uuid
from datetime import datetime

from pydantic import BaseModel


class AdminResponse(BaseModel):
    """Schema trả về thông tin admin."""
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}