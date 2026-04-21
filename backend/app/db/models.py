from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"

    # Dựa trên tài liệu thiết kế: Định danh duy nhất, email, và mật khẩu băm 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    tier = Column(String, default="free")
    default_language_id = Column(UUID(as_uuid=True), nullable=True)