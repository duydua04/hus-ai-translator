# Đường dẫn: backend/app/api/common/upload_router.py
from fastapi import APIRouter, UploadFile, File, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...config.db import get_db
from ...services.common.upload_service import UploadService

# Sửa lại đường dẫn import đúng với vị trí file middleware auth.py của bạn
from ...middleware.auth import require_user

from ...utils.minio_utils import minio_handler

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

upload_router = APIRouter(tags=["Common - Uploads"])

# Dependency lấy service
def get_upload_service(db: AsyncSession = Depends(get_db)) -> UploadService:
    return UploadService(db)

@upload_router.post(
    "/api/upload/file",
    status_code=status.HTTP_201_CREATED
)
async def upload_pdf_file(
        file: UploadFile = File(...),
        service: UploadService = Depends(get_upload_service),
        auth_info: dict = Depends(require_user) # BẮT BUỘC ĐĂNG NHẬP
):
    """API Upload file (Bắt buộc đăng nhập). Nhận PDF <= 5MB."""

    # Lấy đối tượng User từ kết quả trả về của middleware
    current_user = auth_info["user"]

    # 1. Validate định dạng
    if not file.filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hệ thống chỉ chấp nhận định dạng file .pdf")

    # 2. Validate dung lượng
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kích thước file vượt quá 5MB.")

    # 3. Chạy service Upload (Sử dụng await vì service đã được đổi thành async)
    upload_result = await service.upload_pdf_stream(
        file_name=file.filename,
        file_stream=file.file,
        file_size=file.size,
        content_type=file.content_type,
        user_id=current_user.id # Trích xuất ID thật của User từ token
    )

    return {
        "success": True,
        "message": "Upload file thành công",
        "data": upload_result
    }

@upload_router.get(
    "/api/files/presigned-url",
    status_code=status.HTTP_200_OK
)
async def get_file_access_url(path: str = Query(..., description="Đường dẫn file trên MinIO")):
    try:
        url = minio_handler.get_presigned_url(path)
        return {
            "success": True,
            "data": {
                "url": url
            }
        }
    except Exception as e:
        print(f"Lỗi tạo presigned url: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tạo link truy cập file lúc này."
        )