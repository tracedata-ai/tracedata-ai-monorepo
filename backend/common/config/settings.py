from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
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
        "AI-powered vehicle telematics and driver advocacy platform."
    )

    # ── Database ────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/tracedata"

    # ── Redis ────────────────────────────────────────────────────────────────
    redis_url: str = "redis://redis:6379/0"
    
    # ── Queues ──────────────────────────────────────────────────────────────
    ingestion_queue: str = "td:ingestion:events"
    orchestrator_queue: str = "td:orchestrator:events"
    safety_queue: str = "td:agent:safety"
    scoring_queue: str = "td:agent:scoring"
    support_queue: str = "td:agent:support"
    sentiment_queue: str = "td:agent:sentiment"
    
    # ── Security ────────────────────────────────────────────────────────────
    secret_key: str = "changeme"
    
    # ── AI ──────────────────────────────────────────────────────────────────
    google_api_key: str = ""
    openai_api_key: str = ""

@lru_cache
def get_settings() -> Settings:
    return Settings()
