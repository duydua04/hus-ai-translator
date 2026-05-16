import json
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from ...config.db import get_db
from ...schemas.common.translation import FileTranslationStartRequest, WebhookTranslationDone
from ...models.models import Translation, MediaAsset, Language
from ...services.sse_manager import sse_manager
from ...services.admin.admin_dashboard_service import AdminDashboardService

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

            # Resolve language codes for AI Worker
            lang_res = await self.db.execute(
                select(Language).where(Language.id.in_([payload.source_lang_id, payload.target_lang_id]))
            )
            langs = lang_res.scalars().all()
            lang_dict = {str(l.id): l.language_code for l in langs}
            source_lang_code = lang_dict.get(str(payload.source_lang_id), "en")
            target_lang_code = lang_dict.get(str(payload.target_lang_id), "vi")

            # 3. Đóng gói Task cho AI Worker
            task_data = {
                "translation_id": str(new_translation.id),
                "client_id": client_id,
                "file_path": input_asset.file_path,
                "action": "translate_file",
                "source_lang": source_lang_code,
                "target_lang": target_lang_code
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
        Xử lý khi AI Worker làm xong: Cập nhật DB, tạo MediaAsset kết quả,
        sau đó bắn SSE "completed" / "failed" cho Frontend.

        QUAN TRỌNG: SSE "completed" chỉ được bắn SAU KHI DB đã commit thành công.
        Điều này đảm bảo khi Frontend nhận "completed" → DB đã sẵn sàng để query.
        """
        # 1. Tìm bản dịch
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
                await self.db.flush()

                # 4. Móc vào Translation
                translation.result_file_id = result_asset.id
                translation.status = "success"
            else:
                # 5. AI báo lỗi
                translation.status = "failed"

            await self.db.commit()

            # 6. BẮN SSE SAU KHI DB ĐÃ COMMIT — Frontend nhận được = DB sẵn sàng
            if payload.status == "success":
                await sse_manager.publish_message(
                    client_id=payload.client_id,
                    message={
                        "status": "completed",
                        "progress": 100,
                        "message": "Hoàn tất! Bản dịch đã sẵn sàng.",
                        "translation_id": str(payload.translation_id),
                        "result_path": payload.result_path,
                    }
                )
            else:
                await sse_manager.publish_message(
                    client_id=payload.client_id,
                    message={
                        "status": "failed",
                        "progress": 0,
                        "message": payload.error_message or "Dịch tài liệu thất bại.",
                        "translation_id": str(payload.translation_id),
                    }
                )

            # 7. INVALIDATE ADMIN DASHBOARD CACHE + NOTIFY
            try:
                admin_svc = AdminDashboardService(self.db)
                await admin_svc.invalidate_on_translation()
                await AdminDashboardService.notify_admin(
                    event_type="new_translation",
                    message="Có bản dịch file mới hoàn thành.",
                    data={"translation_id": str(payload.translation_id)},
                )
            except Exception:
                pass  # Không để lỗi dashboard ảnh hưởng flow chính

            return {"success": True}

        except Exception as e:
            await self.db.rollback()
            # Bắn SSE lỗi để FE không bị treo
            try:
                await sse_manager.publish_message(
                    client_id=payload.client_id,
                    message={
                        "status": "failed",
                        "progress": 0,
                        "message": "Lỗi hệ thống khi lưu kết quả.",
                        "translation_id": str(payload.translation_id),
                    }
                )
            except Exception:
                pass
            print(f"Lỗi xử lý Webhook: {e}")
            raise HTTPException(status_code=500, detail="Lỗi khi lưu kết quả vào Database")


# Dependency Injection để dùng trong Router
def get_translation_service(db: AsyncSession = Depends(get_db)) -> TranslationService:
    return TranslationService(db)