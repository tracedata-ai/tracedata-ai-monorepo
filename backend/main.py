from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.logging import setup_logging, get_logger

# Domain Routers
from domains.telemetry_safety.router import router as telemetry_router
from domains.driver_evaluation.router import router as evaluation_router
from domains.driver_wellness.router import router as wellness_router
from domains.orchestration.router import router as orchestration_router

# Initialize structured logging
setup_logging()
logger = get_logger("backend.main")

app = FastAPI(
    title="TraceData Backend (DDD)",
    description="Refactored Backend using Bounded Contexts for Fleet Intelligence.",
    version="1.0.0"
)

# Configure CORS
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Routing
app.include_router(telemetry_router, prefix="/api/v1/telemetry-safety")
app.include_router(evaluation_router, prefix="/api/v1/driver-evaluation")
app.include_router(wellness_router, prefix="/api/v1/driver-wellness")
app.include_router(orchestration_router, prefix="/api/v1/orchestration")

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "OK", "architecture": "Bounded Contexts (DDD)"}

@app.get("/", tags=["system"])
async def root():
    return {"message": "Welcome to TraceData Backend (DDD Mode)"}
