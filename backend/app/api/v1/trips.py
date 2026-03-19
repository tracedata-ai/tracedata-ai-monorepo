"""TraceData Backend — Trips API Router.

Endpoints:
  GET  /api/v1/trips          — List all trips (with optional status filter)
  GET  /api/v1/trips/{id}     — Get trip by UUID (includes safety score)
  POST /api/v1/trips          — Start a new trip (Start-of-Trip ping)
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripRead

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get("/", response_model=list[TripRead], summary="List all trips")
async def list_trips(
    skip: int = 0,
    limit: int = 50,
    status_filter: str | None = Query(None, alias="status", description="Filter by status: active | completed | zombie"),
    db: AsyncSession = Depends(get_db),
) -> list[Trip]:
    """
    Returns trips with optional status filtering.

    TIP: Try `?status=active` to see only live trips,
    or `?status=zombie` to find trips missing an End-of-Trip ping.
    """
    query = select(Trip).offset(skip).limit(limit)
    if status_filter:
        query = query.where(Trip.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{trip_id}", response_model=TripRead, summary="Get trip by ID")
async def get_trip(
    trip_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Trip:
    """
    Fetches a single trip.

    Note: If `safety_score` is null, the trip is still active or
    has not been scored yet by the Behavior Agent.
    """
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@router.post("/", response_model=TripRead, status_code=status.HTTP_201_CREATED, summary="Start a new trip")
async def start_trip(
    payload: TripCreate,
    db: AsyncSession = Depends(get_db),
) -> Trip:
    """
    Records a Start-of-Trip ping and creates an active trip record.

    In the full system, this also notifies the Orchestrator Agent to
    begin active monitoring of this trip.
    """
    trip = Trip(**payload.model_dump())
    db.add(trip)
    await db.flush()
    await db.refresh(trip)
    return trip
