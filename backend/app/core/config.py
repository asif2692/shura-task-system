from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "Shura Task & Follow-up Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Default: local SQLite (no Supabase needed)
    # For PostgreSQL later: postgresql+asyncpg://user:pass@host:5432/dbname
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BACKEND_DIR / 'shura.db'}"
    DATABASE_URL_SYNC: str = f"sqlite:///{BACKEND_DIR / 'shura.db'}"

    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    JWT_SECRET_KEY: str = "shura-task-dev-secret-key-change-in-production-32"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "Shura Task System"

    CORS_ORIGINS: list[str] = ["http://localhost:4200", "http://127.0.0.1:4200"]

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    print(f"Loading .env from: {ENV_FILE} (exists={ENV_FILE.exists()})")
    print(f"Database: {s.DATABASE_URL[:60]}...")
    return s


settings = get_settings()
