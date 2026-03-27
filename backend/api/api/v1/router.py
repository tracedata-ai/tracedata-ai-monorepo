"""
TraceData Backend — API v1 Router Aggregator.

This is the single mount point for all v1 sub-routers.
Adding a new resource = importing its router and calling include_router() here.
"""

from fastapi import APIRouter

from api.api.v1 import drivers, fleet, issues, maintenance, routes, tenants, trips

# This router is mounted at /api/v1 in main.py
api_router = APIRouter()

api_router.include_router(fleet.router)
api_router.include_router(drivers.router)
api_router.include_router(routes.router)
api_router.include_router(trips.router)
api_router.include_router(issues.router)
api_router.include_router(maintenance.router)
api_router.include_router(tenants.router)
