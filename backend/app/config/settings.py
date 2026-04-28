from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Cấu hình hệ thống, tất cả giá trị được nạp từ file .env.
    Không được hard-code bất kỳ key hoặc secret nào ngoài file này.
    """

    # --- DATABASE ---
    DATABASE_URL: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "localhost"

    # --- JWT / OAUTH2 ---
    OAUTH2_SECRET_KEY: str
    OAUTH2_ALGORITHM: str = "HS256"
    OAUTH2_ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    OAUTH2_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    #Secret Admin
    FIRST_ADMIN_SECRET: str = "VungOiMoRa123"

    # --- SESSION MIDDLEWARE ---
    SECRET_KEY: str

    # --- RESET PASSWORD ---
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int = 5

    # --- APP ---
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    ADMIN_URL: str = "http://localhost:3001"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()