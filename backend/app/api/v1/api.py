from fastapi import APIRouter
from app.api.v1.endpoints import entities, telemetry, agents

api_router = APIRouter()
api_router.include_router(entities.router, prefix="/entities")
api_router.include_router(telemetry.router, prefix="/telemetry")
api_router.include_router(agents.router, prefix="/agents")
