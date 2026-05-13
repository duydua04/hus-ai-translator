import json
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from ...config.db import get_db
from ...schemas.common.translation import FileTranslationStartRequest, WebhookTranslationDone
from ...models.models import Translation, MediaAsset
from ...services.sse_manager import sse_manager

QUEUE_NAME = "translation_tasks_queue"


class TranslationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_file_translation_task(
            self,
            client_id: str,
            payload: FileTranslationStartRequest,
            user_id: str
    ) -> Dict[str, Any]:
        """
        Khởi tạo tiến trình dịch file: Lưu DB, đẩy Queue, bắn SSE
        """
        # 1. Kiểm tra file gốc bằng cú pháp Async
        result = await self.db.execute(
            select(MediaAsset).where(MediaAsset.id == payload.input_file_id)
        )
        input_asset = result.scalar_one_or_none()

        if not input_asset:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu gốc.")

        # Kiểm tra quyền (Optional)
        # if str(input_asset.user_id) != str(user_id):
        #     raise HTTPException(status_code=403, detail="Không có quyền truy cập file này.")

        try:
            # 2. Tạo bản ghi Translation
            new_translation = Translation(
                user_id=user_id,
                source_lang_id=payload.source_lang_id,
                target_lang_id=payload.target_lang_id,
                type="document_pdf",
                input_file_id=input_asset.id,
                status="processing"
            )
            self.db.add(new_translation)
            await self.db.commit()
            await self.db.refresh(new_translation)

            # 3. Đóng gói Task cho AI Worker
            task_data = {
                "translation_id": str(new_translation.id),
                "client_id": client_id,
                "file_path": input_asset.file_path,
                "action": "translate_file"
            }

            # 4. Đẩy vào Redis Queue
            await sse_manager.redis_client.lpush(QUEUE_NAME, json.dumps(task_data))

            # 5. Bắn SSE
            await sse_manager.publish_message(
                client_id=client_id,
                message={"status": "processing", "progress": 0,
                         "message": "Đã tạo phiên dịch. Đang đưa vào hàng đợi AI..."}
            )

            return {
                "success": True,
                "message": "Đã bắt đầu tiến trình dịch",
                "translation_id": new_translation.id
            }

        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Lỗi khởi tạo dịch thuật: {e}")

    async def handle_webhook_result(self, payload: WebhookTranslationDone) -> Dict[str, bool]:
        """
        Xử lý khi AI Worker làm xong: Cập nhật DB, tạo MediaAsset kết quả
        """
        # 1. Tìm bản dịch bằng cú pháp Async
        trans_result = await self.db.execute(
            select(Translation).where(Translation.id == payload.translation_id)
        )
        translation = trans_result.scalar_one_or_none()

        if not translation:
            raise HTTPException(status_code=404, detail="Không tìm thấy phiên dịch này.")

        try:
            if payload.status == "success" and payload.result_path:
                # 2. AI báo xong -> Tìm MediaAsset gốc để lấy tên
                asset_result = await self.db.execute(
                    select(MediaAsset).where(MediaAsset.id == translation.input_file_id)
                )
                original_asset = asset_result.scalar_one_or_none()

                new_filename = f"Translated_{original_asset.org_filename}" if original_asset else "Translated_Document.pdf"

                # 3. Tạo MediaAsset mới cho file kết quả
                result_asset = MediaAsset(
                    user_id=translation.user_id,
                    org_filename=new_filename,
                    file_path=payload.result_path,
                    file_type="document"
                )
                self.db.add(result_asset)
                await self.db.flush()  # Lấy ID của result_asset trước khi commit

                # 4. Móc vào Translation
                translation.result_file_id = result_asset.id
                translation.status = "success"
            else:
                # 5. AI báo lỗi
                translation.status = "failed"

            await self.db.commit()
            return {"success": True}

        except Exception as e:
            await self.db.rollback()
            print(f"Lỗi xử lý Webhook: {e}")
            raise HTTPException(status_code=500, detail="Lỗi khi lưu kết quả vào Database")


# Dependency Injection để dùng trong Router
def get_translation_service(db: AsyncSession = Depends(get_db)) -> TranslationService:
    return TranslationService(db)