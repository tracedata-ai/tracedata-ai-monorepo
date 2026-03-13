from fastapi import APIRouter
from app.api.v1.endpoints import entities

api_router = APIRouter()
api_router.include_router(entities.router, prefix="/entities")
