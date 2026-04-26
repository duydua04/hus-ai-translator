"""
main.py
--------
Entry point của ứng dụng AI Translator.
File này CHỈ:
  - Khởi tạo FastAPI app
  - Gắn middleware
  - Import và include các router

Không được viết logic nghiệp vụ ở đây.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config.settings import settings

# --- Import các API router ---
from .api.auth.auth_router import router as auth_router
from .api.admin.admin_router import router as admin_router

# =========================================================
# KHỞI TẠO APP
# =========================================================
app = FastAPI(
    title="AI Translator API",
    description="Backend hệ thống dịch thuật AI với quản lý người dùng và admin.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# =========================================================
# MIDDLEWARE
# =========================================================

# Session middleware (dùng cho OAuth callback hoặc state tạm thời)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        settings.ADMIN_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# INCLUDE ROUTERS
# =========================================================

# Xác thực người dùng: /auth/...
app.include_router(auth_router)

# Quản trị admin: /admin/...
app.include_router(admin_router)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/", tags=["Health"])
def health_check():
    """Kiểm tra API đang chạy."""
    return {"status": "ok", "app": "AI Translator API", "version": "1.0.0"}