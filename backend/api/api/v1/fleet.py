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

from api.api.deps import get_db
from api.models.fleet import Vehicle
from api.models.maintenance import Maintenance
from api.schemas.fleet import VehicleCreate, VehicleRead

router = APIRouter(prefix="/fleet", tags=["Fleet"])


@router.get("/", response_model=list[VehicleRead], summary="List all vehicles")
async def list_vehicles(
    skip: int = 0,
    limit: int = 50,
    tenant_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[VehicleRead]:
    """
    Returns a paginated list of vehicles.
    Optional: ?tenant_id=<uuid> to filter by fleet operator.
    """
    query = select(Vehicle).offset(skip).limit(limit)
    if tenant_id:
        query = query.where(Vehicle.tenant_id == tenant_id)
    vehicles = list((await db.execute(query)).scalars().all())

    # Collect vehicle IDs that have open (non-completed) maintenance
    open_ids: set[uuid.UUID] = set()
    if vehicles:
        rows = (await db.execute(
            select(Maintenance.vehicle_id).where(
                Maintenance.status.in_(["scheduled", "in_progress", "overdue"])
            )
        )).all()
        open_ids = {r for (r,) in rows}

    out: list[VehicleRead] = []
    for v in vehicles:
        row = VehicleRead.model_validate(v)
        row.has_open_maintenance = v.id in open_ids
        out.append(row)
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
) -> Vehicle:
    """
    Registers a new vehicle in the fleet.

    The payload is validated by Pydantic before this function is called —
    FastAPI returns 422 Unprocessable Entity automatically for bad input.
    """
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    await db.flush()  # flush assigns the DB-generated id before we return it
    await db.refresh(vehicle)
    return vehicle
