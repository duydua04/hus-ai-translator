# Đường dẫn: app/services/sse_manager.py
import json
import redis.asyncio as redis
from typing import Union, Dict, Any
import os

# Lấy cấu hình Redis từ biến môi trường (hoặc dùng localhost nếu chạy local)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class RedisSSEManager:
    def __init__(self):
        # Khởi tạo kết nối dùng chung. decode_responses=True để tự động parse bytes thành string
        self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        print(f"✅ Đã khởi tạo Redis SSE Manager kết nối tới {REDIS_URL}")

    async def publish_message(self, client_id: str, message: Union[str, Dict[str, Any]]):
        """
        Hàm xuất bản tin nhắn.
        Backend hay Worker AI đều gọi hàm này để đẩy % tiến độ.
        """
        channel_name = f"sse_{client_id}"

        # Nếu payload truyền vào là một Dictionary, tự động ép kiểu thành JSON string
        if isinstance(message, dict):
            message = json.dumps(message, ensure_ascii=False)

        await self.redis_client.publish(channel_name, message)

    def get_pubsub_instance(self):
        """
        Hàm tạo ra một instance lắng nghe (Subscriber) mới.
        Dành riêng cho API GET stream.
        """
        return self.redis_client.pubsub()


# Tạo một instance duy nhất (Singleton pattern) để sử dụng toàn cục
sse_manager = RedisSSEManager()