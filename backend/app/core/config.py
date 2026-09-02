import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BASE_DIR / "m11_db.db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "M-11 Sistema de Alerta Temprana"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Use a separate env var name to avoid conflict with system DATABASE_URL
    M11_DATABASE_URL: str = f"sqlite+aiosqlite:///{DB_FILE.as_posix()}"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.M11_DATABASE_URL

    # JWT Auth
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Gemini
    GEMINI_API_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
