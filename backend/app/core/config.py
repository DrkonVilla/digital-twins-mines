import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BASE_DIR / "m11_db.db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "M-11 Sistema de Alerta Temprana"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = ""
    M11_DATABASE_URL: str = ""

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        raw_url = (self.DATABASE_URL or self.M11_DATABASE_URL or os.getenv("DATABASE_URL") or "").strip()
        if not raw_url:
            return f"sqlite+aiosqlite:///{DB_FILE.as_posix()}"

        # Standardize PostgreSQL URLs for SQLAlchemy asyncpg driver
        if raw_url.startswith("postgres://"):
            raw_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif raw_url.startswith("postgresql://"):
            raw_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif raw_url.startswith("sqlite://"):
            raw_url = raw_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

        # For asyncpg, strip unsupported query parameters like channel_binding (added by Neon)
        if "postgresql+asyncpg://" in raw_url:
            try:
                from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
                parsed = urlparse(raw_url)
                qs = parse_qs(parsed.query)
                # Keep ssl=require if sslmode or ssl is present, or if connecting to cloud providers
                new_qs = {}
                if "sslmode" in qs or "ssl" in qs or "neon.tech" in raw_url:
                    new_qs["ssl"] = "require"
                new_query = urlencode(new_qs)
                raw_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
            except Exception:
                pass

        return raw_url

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
