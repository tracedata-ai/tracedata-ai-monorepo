"""TraceData Backend — Routes API Router.

Endpoints:
  GET  /api/v1/routes          — List all routes
  GET  /api/v1/routes/{id}     — Get route by UUID
  POST /api/v1/routes          — Create a new route
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
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
