"""
TraceData Backend — FastAPI Application Factory.

This is the entry point of the entire backend. It:
  1. Initialises logging from logging.yaml (FIRST — so all startup logs are captured)
  2. Creates the FastAPI app with full OpenAPI/Swagger metadata
  3. Adds RequestIdMiddleware (correlation IDs for every request)
  4. Adds CORS middleware (allows the Next.js frontend at :3000)
  5. Creates all database tables on startup (dev mode — Alembic in prod)
  6. Mounts the /api/v1 router
  7. Exposes a /health endpoint for Docker healthchecks

Entry point for running:  uvicorn app.main:app --reload
Swagger UI: http://localhost:8000/docs
ReDoc:      http://localhost:8000/redoc
"""

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# Import all models so their metadata is registered with Base.
# Aliased as _models to prevent `app` name from being bound to the package
# module — which causes mypy to type `app = FastAPI(...)` as Module.
import api.models as _models  # noqa: F401
from api.api.v1.router import api_router
from api.core.middleware import RequestIdMiddleware
from api.models.base import Base
from common.config.settings import get_settings
from common.db.engine import engine
from core.logging import LogToken, get_logger, setup_logging

# Module-level logger — uses the module path (app.main) as the logger name
logger = get_logger(__name__)

settings = get_settings()


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """
    Runs code on startup and shutdown.

    ON STARTUP:
      1. Initialise logging (MUST be first — so all subsequent startup logs use the config).
      2. Create DB tables (idempotent — safe to call if tables already exist).

    ON SHUTDOWN:
      Dispose the engine to close all DB connections cleanly.

    In production, replace create_all with `alembic upgrade head` via entrypoint.sh.
    """
    # ── 1. Logging ─────────────────────────────────────────────────────────
    setup_logging()  # Reads backend/logging.yaml and wires handlers
    logger.info(f"{LogToken.STARTUP} TraceData Backend starting up...")

    # ── 2. Database ─────────────────────────────────────────────────────────
    async with engine.begin() as conn:
        # Public tables (SQLAlchemy models)
        await conn.run_sync(Base.metadata.create_all)
        # Agent-owned schemas and tables (not managed by SQLAlchemy ORM)
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS scoring_schema"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS safety_schema"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS coaching_schema"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS sentiment_schema"))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS safety_schema.harsh_events_analysis (
              id SERIAL PRIMARY KEY,
              event_id VARCHAR(80) NOT NULL,
              trip_id VARCHAR(100) NOT NULL,
              event_type VARCHAR(80),
              severity VARCHAR(50),
              event_timestamp TIMESTAMP,
              lat DOUBLE PRECISION,
              lon DOUBLE PRECISION,
              traffic_conditions TEXT,
              weather_conditions TEXT,
              analysis JSONB,
              created_at TIMESTAMP
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS safety_schema.safety_decisions (
              decision_id SERIAL PRIMARY KEY,
              event_id VARCHAR(80),
              trip_id VARCHAR(100) NOT NULL,
              decision VARCHAR(255),
              action VARCHAR(255),
              reason TEXT,
              recommended_action TEXT,
              created_at TIMESTAMP
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS coaching_schema.coaching (
              coaching_id SERIAL PRIMARY KEY,
              trip_id VARCHAR(80) NOT NULL,
              driver_id VARCHAR(80) NOT NULL,
              coaching_category VARCHAR(80),
              message TEXT,
              priority VARCHAR(20),
              created_at TIMESTAMP
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sentiment_schema.feedback_sentiment (
              sentiment_id SERIAL PRIMARY KEY,
              trip_id VARCHAR(80) NOT NULL,
              driver_id VARCHAR(80) NOT NULL,
              feedback_text TEXT,
              sentiment_score DOUBLE PRECISION,
              sentiment_label VARCHAR(50),
              analysis JSONB,
              created_at TIMESTAMP
            )
        """))
    logger.info(f"{LogToken.DATABASE_INIT} Database tables created / verified.")

    # ── 3. Simulation sidecar (opt-in via SIM_LOOP=true) ───────────────────
    sim_task: asyncio.Task | None = None
    if os.environ.get("SIM_LOOP", "").lower() == "true":
        from scripts.bootstrap_sg_baseline import _run_loop
        interval = int(os.environ.get("SIM_INTERVAL", "30"))
        event_delay = float(os.environ.get("SIM_EVENT_DELAY", "0.5"))
        truck_delay = float(os.environ.get("SIM_TRUCK_DELAY", "5.0"))
        truck_count = int(os.environ.get("SIM_TRUCK_COUNT", "10"))
        sim_task = asyncio.create_task(_run_loop(interval, event_delay, truck_delay, truck_count))
        logger.info(f"{LogToken.STARTUP} Simulation sidecar started (trucks={truck_count} interval={interval}s event_delay={event_delay}s truck_delay={truck_delay}s)")

    yield  # ← app is live and serving requests from here

    # ── Shutdown ────────────────────────────────────────────────────────────
    if sim_task is not None:
        sim_task.cancel()
        logger.info(f"{LogToken.SHUTDOWN} Simulation sidecar stopped.")
    await engine.dispose()
    logger.info(f"{LogToken.SHUTDOWN} Database engine disposed. Shutdown complete.")


# ── OpenAPI Tag Metadata ───────────────────────────────────────────────────────
# Each tag groups related endpoints in the Swagger UI sidebar.
# Adding a description here gives Swagger readers context without opening code.
OPENAPI_TAGS = [
    {
        "name": "Fleet",
        "description": "Commercial vehicles (trucks) in the fleet. "
        "Each vehicle belongs to one tenant and can be assigned to one driver.",
    },
    {
        "name": "Drivers",
        "description": "Driver profiles. The `experience_level` field sets the **AIF360 fairness cohort** "
        "used by the Behavior Agent for bias-corrected scoring.",
    },
    {
        "name": "Routes",
        "description": "Named delivery routes between two locations. "
        "The `route_type` (highway / urban / mixed) informs context-aware safety scoring.",
    },
    {
        "name": "Trips",
        "description": "The central entity. A trip links a driver, vehicle, and route. "
        "Filter by `?status=active` for live trips or `?status=zombie` for timed-out trips. "
        "The `safety_score` field is **null** until the Behavior Agent scores the completed trip.",
    },
    {
        "name": "Issues",
        "description": "Classified driving events within a trip (e.g. `harsh_brake`, `speeding`, `collision`). "
        "Severity levels map to Redis topic priority: critical → emergency, high → safety, medium → general.",
    },
    {
        "name": "Maintenance",
        "description": "Vehicle maintenance records. The `triggered_by` field shows whether a record was "
        "created manually or by the **Safety Agent** after a critical incident.",
    },
    {
        "name": "System",
        "description": "Health check and API metadata endpoints.",
    },
]

# ── App Factory ────────────────────────────────────────────────────────────────
app: FastAPI = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description=settings.project_description,
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
    contact={
        "name": "TraceData Engineering",
        "url": "https://github.com/tracedata-ai",
    },
    license_info={
        "name": "MIT",
    },
    # Swagger UI at /docs — always on (disable in production if needed)
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ── Middleware stack (applied in REVERSE order — last added = outermost) ───────
#
# Request flow:  RequestIdMiddleware → CORSMiddleware → route handler
# Response flow: route handler → CORSMiddleware → RequestIdMiddleware
#
# RequestIdMiddleware must be outermost so the correlation ID is set
# before any other middleware or handler emits a log line.

# 1. CORS — allow the Next.js frontend at port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Request ID — must be added AFTER CORS so it wraps the entire stack
app.add_middleware(RequestIdMiddleware)


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.api_v1_prefix)


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"], summary="Health check")
async def health() -> dict[str, str]:
    """
    Liveness probe used by Docker and Kubernetes.
    Returns 200 OK when the application is running.
    """
    return {"status": "ok", "version": settings.project_version}


@app.get("/", tags=["System"], summary="Root redirect info")
async def root() -> dict[str, str]:
    """Root endpoint — tells clients where to find the API docs."""
    return {
        "message": "TraceData Backend is running.",
        "docs": "/docs",
        "health": "/health",
    }
