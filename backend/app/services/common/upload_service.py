from fastapi import HTTPException, status
from ...utils.minio_utils import minio_handler

class UploadService:
    def upload_pdf_stream(self, file_name: str, file_stream, file_size: int, content_type: str) -> dict:
        try:
            file_path = minio_handler.upload_file(
                file_name=file_name,
                file_stream=file_stream,
                file_size=file_size,
                content_type=content_type
            )
            return {
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size
            }
        except Exception as e:
            print(f"Lỗi upload file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể lưu trữ file lúc này. Vui lòng thử lại sau."
            )

def get_upload_service() -> UploadService:
    return UploadService()