# Đường dẫn: backend/app/services/common/upload_service.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ...utils.minio_utils import minio_handler
from ...models.models import MediaAsset


class UploadService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_pdf_stream(self, file_name: str, file_stream, file_size: int, content_type: str,
                                user_id: str) -> dict:
        try:
            # 1. Upload file lên MinIO (MinIO SDK là đồng bộ, cứ để nguyên)
            file_path = minio_handler.upload_file(
                file_name=file_name,
                file_stream=file_stream,
                file_size=file_size,
                content_type=content_type
            )

            # 2. Lưu thông tin file vào Database (Dùng AsyncSession)
            new_asset = MediaAsset(
                user_id=user_id,
                org_filename=file_name,
                file_path=file_path,
                file_type="document"
            )
            self.db.add(new_asset)
            await self.db.commit()
            await self.db.refresh(new_asset)  # Lấy UUID vừa sinh ra

            return {
                "id": str(new_asset.id),
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size
            }
        except Exception as e:
            await self.db.rollback()
            print(f"Lỗi upload file (Kèm DB): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể lưu trữ file và cập nhật dữ liệu. Vui lòng thử lại sau."
            )