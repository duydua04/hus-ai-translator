from pydantic import BaseModel, Field

class TranslationMessage(BaseModel):
    # Khai báo trường dữ liệu 'text' bắt buộc phải có
    text: str = Field(
        ..., # Dấu ... có nghĩa đây là trường bắt buộc (required)
        min_length=1, # Độ dài tối thiểu là 1 ký tự (không cho phép gửi chuỗi rỗng)
        description="Nội dung kết quả dịch thuật muốn gửi xuống client",
        json_schema_extra={
            "example": "AI đang dịch câu thứ nhất..." # Ví dụ hiển thị trên Swagger UI
        }
    )