"""
TraceData Backend — Fleet (Vehicle) API Router.

Endpoints:
  GET  /api/v1/fleet          — List all vehicles (with pagination)
  GET  /api/v1/fleet/{id}     — Get a specific vehicle by UUID
  POST /api/v1/fleet          — Create a new vehicle

This is a READ-heavy skeleton. The pattern for every router is:
  1. Declare the router with a prefix and tags (shows in Swagger)
  2. Inject `db: AsyncSession` via `Depends(get_db)` for DB access
  3. Use `select()` (SQLAlchemy 2.0 style) instead of the legacy `query()`
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import get_db, get_redis
from api.models.fleet import Vehicle
from api.models.maintenance import Maintenance
from api.schemas.fleet import VehicleCreate, VehicleRead
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

router = APIRouter(prefix="/fleet", tags=["Fleet"])


@router.get("/", response_model=list[VehicleRead], summary="List all vehicles")
async def list_vehicles(
    skip: int = 0,
    limit: int = 50,
    tenant_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
) -> list[VehicleRead]:
    cache_key = RedisSchema.Api.fleet_list(str(tenant_id or "all"), skip, limit)
    if cached := await redis.cache_get(cache_key):
        return [VehicleRead(**item) for item in cached]

    query = select(Vehicle).offset(skip).limit(limit)
    if tenant_id:
        query = query.where(Vehicle.tenant_id == tenant_id)
    vehicles = list((await db.execute(query)).scalars().all())

    open_ids: set[uuid.UUID] = set()
    if vehicles:
        rows = (
            await db.execute(
                select(Maintenance.vehicle_id).where(
                    Maintenance.status.in_(["scheduled", "in_progress", "overdue"])
                )
            )
        ).all()
        open_ids = {r for (r,) in rows}

    out: list[VehicleRead] = []
    for v in vehicles:
        row = VehicleRead.model_validate(v)
        row.has_open_maintenance = v.id in open_ids
        out.append(row)

    await redis.cache_set(
        cache_key, [r.model_dump() for r in out], RedisSchema.Api.FLEET_TTL
    )
    return out


@router.get("/{vehicle_id}", response_model=VehicleRead, summary="Get vehicle by ID")
async def get_vehicle(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Vehicle:
    """
    Fetches a single vehicle by its UUID.

    Raises 404 if the vehicle does not exist.
    """
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )
    return vehicle


@router.post(
    "/",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a vehicle",
)
async def create_vehicle(
    payload: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
) -> Vehicle:
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    await db.flush()
    await db.refresh(vehicle)
    await redis.cache_delete(RedisSchema.Api.fleet_list("all", 0, 50))
    return vehicle
