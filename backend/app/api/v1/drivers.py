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

from app.api.deps import get_db
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverRead

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("/", response_model=list[DriverRead], summary="List all drivers")
async def list_drivers(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[Driver]:
    """Returns a paginated list of all registered drivers."""
    result = await db.execute(select(Driver).offset(skip).limit(limit))
    return list(result.scalars().all())


@router.get("/{driver_id}", response_model=DriverRead, summary="Get driver by ID")
async def get_driver(
    driver_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Driver:
    """Fetches a single driver by UUID. Returns 404 if not found."""
    driver = await db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    return driver


@router.post("/", response_model=DriverRead, status_code=status.HTTP_201_CREATED, summary="Register a driver")
async def create_driver(
    payload: DriverCreate,
    db: AsyncSession = Depends(get_db),
) -> Driver:
    """Registers a new driver. The experience_level field sets the AIF360 fairness cohort."""
    driver = Driver(**payload.model_dump())
    db.add(driver)
    await db.flush()
    await db.refresh(driver)
    return driver
