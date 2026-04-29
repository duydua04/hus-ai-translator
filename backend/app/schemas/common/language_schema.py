import uuid
from pydantic import BaseModel


class LanguageResponse(BaseModel):
    id: uuid.UUID
    language_code: str
    language_name: str
    is_active: bool

    model_config = {"from_attributes": True}


class LanguageCreateRequest(BaseModel):
    language_code: str
    language_name: str