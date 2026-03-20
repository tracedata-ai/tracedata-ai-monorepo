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

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from core.config import get_settings
from core.database import engine
from core.logging import LogToken, get_logger, setup_logging
from app.core.middleware import RequestIdMiddleware

# Import all models so their metadata is registered with Base.
# Aliased as _models to prevent `app` name from being bound to the package
# module — which causes mypy to type `app = FastAPI(...)` as Module.
import app.models as _models  # noqa: F401

from app.models.base import Base

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
        await conn.run_sync(Base.metadata.create_all)
    logger.info(f"{LogToken.DATABASE_INIT} Database tables created / verified.")

    yield  # ← app is live and serving requests from here

    # ── Shutdown ────────────────────────────────────────────────────────────
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
