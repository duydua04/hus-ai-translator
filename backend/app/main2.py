"""
Main entry point for the FastAPI application.
Simplified version without lifespan events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# IMPORT CONFIGURATIONS
from .config.settings import settings

# IMPORT CONTROLLERS (ROUTERS)
from .api.common.auth_api import router as auth_router

app = FastAPI(
    title="HUS AI Translator API",
    description="Scalable API for AI-powered document and text translation.",
    version="1.0.0"
)

# 1. SESSION MIDDLEWARE
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

# 2. CORS MIDDLEWARE
# Dynamically loaded from settings for production readiness
origins = [
    settings.FRONTEND_URL,
    settings.ADMIN_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# INCLUDE ROUTERS
# =========================================================

# --- COMMON ROUTERS ---
app.include_router(auth_router)

# Note: Add other routers here as the project grows
# app.include_router(translation_router)
# app.include_router(chat_router)

# =========================================================
# ROOT ENDPOINT
# =========================================================
@app.get("/", tags=["Health Check"])
async def root():
    """Health check endpoint to verify server status."""
    return {
        "status": "online",
        "app": "HUS AI Translator API",
        "environment": settings.APP_ENV,
        "version": "1.0.0"
    }