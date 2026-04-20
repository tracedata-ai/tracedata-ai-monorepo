"""TraceData Backend — Routes API Router.

Endpoints:
  GET  /api/v1/routes          — List all routes
  GET  /api/v1/routes/{id}     — Get route by UUID
  POST /api/v1/routes          — Create a new route
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import get_db
from api.models.route import Route
from api.schemas.route import RouteCreate, RouteRead

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.get("/", response_model=list[RouteRead], summary="List all routes")
async def list_routes(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[Route]:
    """Returns a paginated list of defined delivery routes."""
    result = await db.execute(select(Route).offset(skip).limit(limit))
    return list(result.scalars().all())


@router.get("/{route_id}", response_model=RouteRead, summary="Get route by ID")
async def get_route(
    route_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Route:
    """Fetches a single route. Raises 404 if not found."""
    route = await db.get(Route, route_id)
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
        )
    return route


@router.post(
    "/",
    response_model=RouteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a route",
)
async def create_route(
    payload: RouteCreate,
    db: AsyncSession = Depends(get_db),
) -> Route:
    """Creates a new route definition."""
    route = Route(**payload.model_dump())
    db.add(route)
    await db.flush()
    await db.refresh(route)
    return route


@router.get("/{route_id}/heatmap", summary="Safety event heatmap for a route")
async def route_heatmap(
    route_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Returns lat/lon + severity for all safety events on trips belonging to this route."""
    sql = text("""
        SELECT h.lat, h.lon, h.severity, h.event_type
        FROM safety_schema.harsh_events_analysis h
        JOIN public.trips t ON t.id = (
            CASE
                WHEN h.trip_id ~ '^[0-9a-fA-F-]{36}$' THEN h.trip_id::uuid
                ELSE NULL
            END
        )
        WHERE t.route_id = :route_id
          AND h.lat IS NOT NULL
          AND h.lon IS NOT NULL
        ORDER BY h.created_at DESC
        LIMIT 500
    """)
    rows = (await db.execute(sql, {"route_id": str(route_id)})).mappings().all()
    return [
        {
            "lat": r["lat"],
            "lon": r["lon"],
            "severity": r["severity"],
            "event_type": r["event_type"],
        }
        for r in rows
    ]
