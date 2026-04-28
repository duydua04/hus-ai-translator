# IMPORT LIBRARIES
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware






# IMPORT CONFIGURATIONS
from .config.settings import settings






# IMPORT COMMON API
from .api.common.auth_api import router as auth_router






# IMPORT ADMIN API
from .api.admin.setup_admin import router as admin_router







# IMPORT USER API











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


# --- CALL COMMON API ---
app.include_router(auth_router)








# CALL ADMIN API
app.include_router(admin_router)







# CALL USER API