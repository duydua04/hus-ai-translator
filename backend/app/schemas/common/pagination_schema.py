from pydantic import BaseModel, Field

class PaginatedResponse(BaseModel):
    """"""
    total: int = Field(description="Tổng số lượng bản ghi")
    page: int = Field(description="Trang hiện tại")
    limit: int = Field(description="Số bản ghi trên mỗi trang")
    total_pages: int = Field(description="Tổng số trang")