"""
TraceData Backend — Application Configuration.

Uses Pydantic v2 BaseSettings to read environment variables from an `.env` file
(or from the actual OS environment when running in Docker). This is the single
source of truth for all configuration — no hardcoded strings anywhere else.

Pattern: Dependency Injection via FastAPI's `Depends(get_settings)`.
"""

from functools import lru_cache

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All fields map 1-to-1 with keys in `.env.example`.
    `model_config` tells Pydantic where to find the `.env` file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── API ────────────────────────────────────────────────────────────────
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    debug: bool = True
    project_name: str = "TraceData Backend"
    project_version: str = "0.1.0"
    project_description: str = (
        "AI-powered vehicle telematics and driver advocacy platform. "
        "Provides REST APIs for Fleet, Drivers, Trips, and an AI Agent layer."
    )

    # ── Database ────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tracedata"

    # ── Security ────────────────────────────────────────────────────────────
    secret_key: str = "changeme"
    access_token_expire_minutes: int = 60

    # ── Seeding ─────────────────────────────────────────────────────────────
    reset_db: bool = False

    # ── AI ──────────────────────────────────────────────────────────────────
    google_api_key: str = ""
    openai_api_key: str = ""

    # ── Redis ────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    @property
    def is_production(self) -> bool:
        """Returns True if running in a production environment."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings singleton.

    Using @lru_cache means the .env file is only read once per process,
    not on every request. Use FastAPI's `Depends(get_settings)` to inject.
    """
    return Settings()
