"""
Application configuration — reads from .env via pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Central config — all values read from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── App ───
    app_name: str = "HealthBridge AI"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "change-me"
    allowed_origins: str = "http://localhost:8081,exp://"

    # ─── Database ───
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/healthbridge"
    database_echo: bool = False

    # ─── Redis ───
    redis_url: str = "redis://localhost:6379/0"

    # ─── LLM APIs ───
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    llm_timeout: int = 15
    llm_max_retries: int = 3

    # ─── JWT Auth ───
    jwt_secret_key: str = "change-me-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 1440  # 24 hours

    # ─── External APIs ───
    google_maps_api_key: Optional[str] = None
    esanjeevani_api_url: str = "https://esanjeevani.mohfw.gov.in/api"

    # ─── Rate Limiting ───
    rate_limit_per_minute: int = 60

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


# Singleton instance — import this everywhere
settings = Settings()
