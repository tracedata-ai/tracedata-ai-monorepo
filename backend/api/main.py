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
from prometheus_fastapi_instrumentator import Instrumentator
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
      2. Demo reset (if DEMO_RESET=true) — drops all tables and flushes Redis for a clean slate.
      3. Create DB tables (idempotent — safe to call if tables already exist).
      4. Start simulation sidecar (if SIM_LOOP=true).

    ON SHUTDOWN:
      Dispose the engine to close all DB connections cleanly.

    In production, replace create_all with `alembic upgrade head` via entrypoint.sh.
    """
    # ── 1. Logging ─────────────────────────────────────────────────────────
    setup_logging()  # Reads backend/logging.yaml and wires handlers
    logger.info(f"{LogToken.STARTUP} TraceData Backend starting up...")

    # ── 2. Demo reset (opt-in) ─────────────────────────────────────────────
    # When DEMO_RESET=true every boot wipes all tables + Redis so the demo
    # always starts from a clean, reproducible baseline.
    if os.environ.get("DEMO_RESET", "").lower() == "true":
        from scripts.bootstrap_sg_baseline import (
            _push_baseline_trip_packets,
            reset_for_demo,
        )

        logger.info(
            f"{LogToken.STARTUP} DEMO_RESET=true — wiping all tables and Redis..."
        )
        await reset_for_demo()
        logger.info(f"{LogToken.STARTUP} Demo reset complete. Re-seeding baseline...")
        # Re-seed immediately so the app never starts with an empty DB.
        # reset_for_demo() clears the bootstrap marker, so this will always push.
        pushed = await _push_baseline_trip_packets()
        logger.info(f"{LogToken.STARTUP} Re-seed complete ({pushed} packets pushed).")

    # ── 3. Database ─────────────────────────────────────────────────────────
    async with engine.begin() as conn:
        # Agent-owned schemas must exist before create_all runs,
        # since some ORM models reference them (e.g. scoring_schema.trip_scores)
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS scoring_schema"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS safety_schema"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS coaching_schema"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS sentiment_schema"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS vector_schema"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Public tables (SQLAlchemy models)
        await conn.run_sync(Base.metadata.create_all)
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
              location_name TEXT,
              traffic_conditions TEXT,
              weather_conditions TEXT,
              analysis JSONB,
              created_at TIMESTAMP
            )
        """))
        await conn.execute(
            text(
                "ALTER TABLE safety_schema.harsh_events_analysis "
                "ADD COLUMN IF NOT EXISTS location_name TEXT"
            )
        )
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
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vector_schema.embeddings (
              id           SERIAL PRIMARY KEY,
              content_type VARCHAR(80)  NOT NULL,
              source_id    VARCHAR(80)  NOT NULL,
              driver_id    VARCHAR(80),
              trip_id      VARCHAR(80),
              content      TEXT         NOT NULL,
              embedding    vector(1536),
              created_at   TIMESTAMP    DEFAULT now()
            )
        """))
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_emb_driver ON vector_schema.embeddings (driver_id)"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_emb_type ON vector_schema.embeddings (content_type)"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_emb_hnsw ON vector_schema.embeddings "
                "USING hnsw (embedding vector_cosine_ops)"
            )
        )
    logger.info(f"{LogToken.DATABASE_INIT} Database tables created / verified.")

    # ── 4. Simulation sidecar (opt-in via SIM_LOOP=true) ───────────────────
    # Disabled by default. Enable in K8s via env var — uses adaptive rate control:
    #   Phase 1 (warmup): SIM_TRUCK_COUNT trucks every SIM_WARMUP_INTERVAL seconds
    #   Phase 2 (steady): same batch every SIM_STEADY_INTERVAL seconds after SIM_WARMUP_HOURS
    sim_task: asyncio.Task | None = None
    if os.environ.get("SIM_LOOP", "").lower() == "true":
        from scripts.bootstrap_sg_baseline import _run_loop

        event_delay = float(os.environ.get("SIM_EVENT_DELAY", "2.0"))
        truck_delay = float(os.environ.get("SIM_TRUCK_DELAY", "5.0"))
        truck_count = int(os.environ.get("SIM_TRUCK_COUNT", "2"))
        warmup_interval = int(os.environ.get("SIM_WARMUP_INTERVAL", "300"))
        steady_interval = int(os.environ.get("SIM_STEADY_INTERVAL", "3600"))
        warmup_hours = float(os.environ.get("SIM_WARMUP_HOURS", "2.0"))
        sim_task = asyncio.create_task(
            _run_loop(
                event_delay=event_delay,
                truck_delay=truck_delay,
                truck_count=truck_count,
                warmup_interval=warmup_interval,
                steady_interval=steady_interval,
                warmup_hours=warmup_hours,
            )
        )
        logger.info(
            f"{LogToken.STARTUP} Simulation sidecar started "
            f"(trucks={truck_count} warmup={warmup_interval}s/{warmup_hours}h "
            f"steady={steady_interval}s event_delay={event_delay}s)"
        )

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


# ── Prometheus metrics ────────────────────────────────────────────────────────
# Instruments all routes automatically (request count, latency histograms).
# Exposes /metrics endpoint scraped by the Prometheus ServiceMonitor.
Instrumentator().instrument(app).expose(app)

# ── Middleware stack (applied in REVERSE order — last added = outermost) ───────
#
# Request flow:  RequestIdMiddleware → CORSMiddleware → route handler
# Response flow: route handler → CORSMiddleware → RequestIdMiddleware
#
# RequestIdMiddleware must be outermost so the correlation ID is set
# before any other middleware or handler emits a log line.

# 1. CORS — origins driven by CORS_ALLOWED_ORIGINS env var (configmap in prod)
# Note: Cannot use "*" with allow_credentials=True per CORS spec
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
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
