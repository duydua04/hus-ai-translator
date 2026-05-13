import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from ..services.sse_manager import sse_manager
from ..schemas.sse import TranslationMessage

router = APIRouter()


# ---------------------------------------------------------
# 1. API SUBSCRIBER (Frontend gọi vào đây để mở kết nối nghe)
# ---------------------------------------------------------
@router.get("/stream/{client_id}", tags=["SSE"])
async def sse_endpoint(client_id: str, request: Request):
    """
    API mở luồng sự kiện (Server-Sent Events).
    Frontend dùng EventSource(url) để kết nối vào đây.
    """

    async def event_generator():
        # Lấy một chiếc "đài radio" từ Manager
        pubsub = sse_manager.get_pubsub_instance()
        channel_name = f"sse_{client_id}"

        # Dò đúng kênh của client này
        await pubsub.subscribe(channel_name)
        print(f"🌐 Client {client_id} đã kết nối SSE.")

        try:
            while True:
                # Phát hiện nếu user tắt trình duyệt hoặc chuyển trang
                if await request.is_disconnected():
                    print(f"🚫 Client {client_id} đã đóng trình duyệt.")
                    break

                # Chờ tin nhắn từ Redis (timeout 1s để vòng lặp tiếp tục kiểm tra disconnect)
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

                if message is not None:
                    # Chuẩn format SSE bắt buộc phải có chữ 'data: ' và kết thúc bằng '\n\n'
                    yield f"data: {message['data']}\n\n"
                else:
                    # Gửi Ping rỗng để giữ cho các Proxy Server (như Nginx) không ngắt kết nối vì timeout
                    yield ": keep-alive\n\n"

        except Exception as e:
            print(f"Lỗi luồng SSE của client {client_id}: {e}")
        finally:
            # Sống còn: Phải hủy đăng ký và đóng pubsub để tránh rò rỉ RAM trên server
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ---------------------------------------------------------
# 2. API PUBLISHER (Dùng để test hoặc cho các Module khác gọi tới)
# ---------------------------------------------------------
@router.post("/send-translation/{client_id}", tags=["SSE"])
async def trigger_translation_result(client_id: str, payload: TranslationMessage):
    """
    API dùng để đẩy thông báo xuống Frontend đang mở kết nối.
    Nhận payload chuẩn theo Schema TranslationMessage.
    """
    # Chuyển Pydantic model thành Dictionary và gửi cho Redis Manager
    await sse_manager.publish_message(client_id, payload.model_dump())

    return {
        "status": "success",
        "message": f"Đã publish tiến độ vào kênh sse_{client_id}",
        "data_sent": payload.model_dump()
    }