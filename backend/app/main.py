"""
Main entry point for the TraceData AI Middleware.

This module initializes the FastAPI application, configures global middleware,
and imports the routed API endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.logging import setup_logging, get_logger

# Initialize structured logging
setup_logging()
logger = get_logger("app.main")

app = FastAPI(
    title="TraceData Backend",
    description="Backend for Fleet Intelligence and Driver Advocacy.",
    version="0.1.0",
    openapi_tags=[
        {"name": "system", "description": "System health and root endpoints"},
        {"name": "telemetry", "description": "Telemetry ingestion and processing logic"},
        {"name": "agents", "description": "Agentic shell interactions and orchestration"},
    ]
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include central router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["system"])
async def health_check():
    """
    Performs a heartbeat check of the middleware.
    """
    return {
        "status": "OK",
        "database": "connected (mock)",
        "environment": "Dockerized (Fargate-ready)"
    }

@app.get("/", tags=["system"])
async def root():
    """Welcome endpoint for the TraceData AI Middleware."""
    return {"message": "Welcome to TraceData AI Middleware Shell"}
