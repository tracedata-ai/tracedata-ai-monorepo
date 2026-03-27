"""TraceData Backend — Maintenance API Router.

Endpoints:
  GET  /api/v1/maintenance              — List all records (optional vehicle filter)
  GET  /api/v1/maintenance/{id}         — Get record by UUID
  POST /api/v1/maintenance              — Create a maintenance record
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import get_db
from api.models.maintenance import Maintenance
from api.schemas.maintenance import MaintenanceCreate, MaintenanceRead

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.get(
    "/", response_model=list[MaintenanceRead], summary="List maintenance records"
)
async def list_maintenance(
    skip: int = 0,
    limit: int = 50,
    vehicle_id: uuid.UUID | None = Query(None, description="Filter by vehicle UUID"),
    db: AsyncSession = Depends(get_db),
) -> list[Maintenance]:
    """
    Returns maintenance records.
    Filter by `?vehicle_id=<uuid>` to see full maintenance history for one truck.
    """
    query = select(Maintenance).offset(skip).limit(limit)
    if vehicle_id:
        query = query.where(Maintenance.vehicle_id == vehicle_id)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get(
    "/{record_id}",
    response_model=MaintenanceRead,
    summary="Get maintenance record by ID",
)
async def get_maintenance(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Maintenance:
    """Fetches a single maintenance record. Returns 404 if not found."""
    record = await db.get(Maintenance, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance record not found"
        )
    return record


@router.post(
    "/",
    response_model=MaintenanceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create maintenance record",
)
async def create_maintenance(
    payload: MaintenanceCreate,
    db: AsyncSession = Depends(get_db),
) -> Maintenance:
    """
    Creates a maintenance record.

    Set `triggered_by='safety_agent'` when called programmatically by the Safety Agent
    after a collision detection — this creates a full AI-to-action audit trail.
    """
    record = Maintenance(**payload.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record
