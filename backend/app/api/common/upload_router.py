from fastapi import APIRouter, UploadFile, File, Depends, status, Query, HTTPException
from ...services.common.upload_service import UploadService, get_upload_service
from ...utils.minio_utils import minio_handler

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

upload_router = APIRouter(tags=["Common - Uploads"])

@upload_router.post(
    "/api/upload/file",
    status_code=status.HTTP_201_CREATED
)
async def upload_pdf_file(
        file: UploadFile = File(...),
        service: UploadService = Depends(get_upload_service)
):
    """API Upload luồng trực tiếp. Nhận PDF <= 5MB."""

    # 1. Validate loại file
    if not file.filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hệ thống chỉ chấp nhận định dạng file .pdf"
        )

    # 2. Validate kích thước
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kích thước file vượt quá 5MB. Vui lòng tải lên file nhỏ hơn."
        )

    # 3. Đẩy trực tiếp xuống Service
    upload_result = service.upload_pdf_stream(
        file_name=file.filename,
        file_stream=file.file,
        file_size=file.size,
        content_type=file.content_type
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