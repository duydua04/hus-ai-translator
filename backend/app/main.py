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
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --- Import các API router ---
# auth_api_router là router chính (services/common/auth_service.py)

from .api.common.auth_api import router as auth_api_router
from .api.admin.admin_user_router import router as admin_user_router
from .api.admin.admin_feedback_router import router as admin_feedback_router
from .api.admin.setup_admin import router as setup_admin_router
from .api.common.language_router import router as language_router
from .api.user.user_router import router as user_router
from .api.translation.translation_router import router as translation_router
from .api.feedback.feedback_router import router as feedback_router
from .api.chat.chat_router import router as chat_router
from .api import sse_route
from .services.sse_manager import sse_manager
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

app.include_router(auth_api_router)         # /auth/...   (login, register, refresh, logout, forgot-password...)
app.include_router(setup_admin_router)      # /api/internal/...
app.include_router(admin_user_router)       # /api/admin/users/...
app.include_router(admin_feedback_router)   # /api/admin/feedback/...
app.include_router(language_router)         # /languages/...
app.include_router(user_router)             # /user/...
app.include_router(translation_router)      # /translate/...
app.include_router(feedback_router)         # /feedback/...
app.include_router(chat_router)             # /chat/...
app.include_router(sse_route.router)   # /stream/...

# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/", tags=["Health"])
def health_check():
    """Kiểm tra API đang chạy."""
    return {"status": "ok", "app": "AI Translator API", "version": "1.0.0"}
