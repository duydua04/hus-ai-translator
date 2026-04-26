import asyncio
from app.config.db import engine, Base
from app.models.models import *   # import để Base "biết" tất cả model

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tất cả bảng đã được tạo thành công!")

if __name__ == "__main__":
    asyncio.run(init_db())