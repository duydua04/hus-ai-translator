import asyncio
from typing import Dict

class SSEManager:
    def __init__(self):
        # Dictionary lưu trữ hàng đợi (Queue) tin nhắn của từng client đang kết nối
        self.active_connections: Dict[str, asyncio.Queue] = {}

    async def connect(self, client_id: str) -> asyncio.Queue:
        """Thêm client vào danh sách quản lý khi họ gọi API SSE"""
        queue = asyncio.Queue()
        self.active_connections[client_id] = queue
        print(f"Client {client_id} đã kết nối. Tổng số: {len(self.active_connections)}")
        return queue

    def disconnect(self, client_id: str):
        """Xóa client khỏi danh sách khi họ đóng trình duyệt/ngắt kết nối"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client {client_id} đã ngắt kết nối.")

    async def send_message(self, client_id: str, message: str):
        """Đẩy dữ liệu vào hàng đợi của một client cụ thể"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].put(message)
            
    async def broadcast(self, message: str):
        """Đẩy dữ liệu cho toàn bộ client đang online (nếu cần)"""
        for queue in self.active_connections.values():
            await queue.put(message)

# Khởi tạo một instance duy nhất để dùng chung cho toàn bộ dự án
sse_manager = SSEManager()