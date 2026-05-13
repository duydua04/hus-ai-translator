import uuid
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error
from ..config.settings import settings

class MinioHandler:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )

        self.external_client = Minio(
            settings.MINIO_PUBLIC_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
            region="us-east-1"
        )

        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Đã tạo bucket thành công: {self.bucket_name}")
        except S3Error as e:
            print(f"Lỗi khởi tạo bucket MinIO: {e}")

    def upload_file(
            self,
            file_name: str,
            file_stream,
            file_size: int,
            content_type: str = "application/pdf"
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        month_folder = datetime.now().strftime("%Y/%m")

        object_name = f"uploads/{month_folder}/{timestamp}_{unique_id}.pdf"

        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_stream,
                length=file_size,
                content_type=content_type
            )
            return f"{self.bucket_name}/{object_name}"
        except S3Error as e:
            raise Exception(f"S3Error: {e}")

    def get_presigned_url(self, file_path: str, expires_in_hours: int = 1) -> str:
        try:
            clean_path = file_path.lstrip('/')
            parts = clean_path.split("/", 1)

            if len(parts) != 2:
                raise ValueError("Đường dẫn file không hợp lệ")

            bucket_name, object_name = parts

            url = self.external_client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=timedelta(hours=expires_in_hours)
            )
            return url
        except Exception as e:
            raise Exception(f"Lỗi khi tạo link truy cập: {e}")

minio_handler = MinioHandler()