"""TraceData Backend — Drivers API Router.

Endpoints:
  GET  /api/v1/drivers          — List all drivers
  GET  /api/v1/drivers/{id}     — Get driver by UUID
  POST /api/v1/drivers          — Register a new driver
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import get_db, get_redis
from api.models.driver import Driver
from api.schemas.driver import DriverCreate, DriverRead
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("/", response_model=list[DriverRead], summary="List all drivers")
async def list_drivers(
    skip: int = 0,
    limit: int = 50,
    tenant_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
) -> list[DriverRead]:
    cache_key = RedisSchema.Api.drivers_list(str(tenant_id or "all"), skip, limit)
    if cached := await redis.cache_get(cache_key):
        return [DriverRead(**item) for item in cached]

    query = select(Driver).offset(skip).limit(limit)
    if tenant_id:
        query = query.where(Driver.tenant_id == tenant_id)
    result = await db.execute(query)
    out = [DriverRead.model_validate(d) for d in result.scalars().all()]

    await redis.cache_set(
        cache_key,
        [d.model_dump() for d in out],
        RedisSchema.Api.DRIVERS_TTL,
    )
    return out


@router.get("/{driver_id}", response_model=DriverRead, summary="Get driver by ID")
async def get_driver(
    driver_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Driver:
    """Fetches a single driver by UUID. Returns 404 if not found."""
    driver = await db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )
    return driver


@router.post(
    "/",
    response_model=DriverRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a driver",
)
async def create_driver(
    payload: DriverCreate,
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
) -> Driver:
    """Registers a new driver. The experience_level field sets the AIF360 fairness cohort."""
    driver = Driver(**payload.model_dump())
    db.add(driver)
    await db.flush()
    await db.refresh(driver)
    await redis.cache_delete(RedisSchema.Api.drivers_list("all", 0, 50))
    return driver
