from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.services.sse_manager import sse_manager
from app.schemas.sse import TranslationMessage # <--- Import Schema ở đây
import asyncio

router = APIRouter()

# 1. API lắng nghe (GET) - Giữ nguyên code của bạn
@router.get("/stream/{client_id}", tags=["SSE"])
async def sse_endpoint(client_id: str, request: Request):
    """API để Front-end kết nối và lắng nghe dữ liệu trả về liên tục"""
    async def event_generator():
        queue = await sse_manager.connect(client_id)
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        except Exception as e:
            print(f"Lỗi SSE generator: {e}")
        finally:
            sse_manager.disconnect(client_id)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# 2. API gửi tin nhắn (POST) - Thêm mới và sử dụng Schema
@router.post("/send-translation/{client_id}", tags=["SSE"])
async def trigger_translation_result(
    client_id: str, 
    payload: TranslationMessage # <--- Sử dụng Schema để kiểm tra dữ liệu đầu vào
):
    """API để server (hoặc một dịch vụ khác) đẩy kết quả dịch xuống client qua SSE"""
    # Lấy text từ payload đã được validate bởi Pydantic
    await sse_manager.send_message(client_id, payload.text)
    
    return {"status": "success", "message": f"Đã gửi tin nhắn tới {client_id}"}