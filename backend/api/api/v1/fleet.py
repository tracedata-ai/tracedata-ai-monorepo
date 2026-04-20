"""
TraceData Backend — Fleet (Vehicle) API Router.

Endpoints:
  GET  /api/v1/fleet          — List all vehicles (with pagination)
  GET  /api/v1/fleet/{id}     — Get a specific vehicle by UUID
  GET  /api/v1/fleet/{id}/detail — Get vehicle with trips, drivers, and event data
  POST /api/v1/fleet          — Create a new vehicle

This is a READ-heavy skeleton. The pattern for every router is:
  1. Declare the router with a prefix and tags (shows in Swagger)
  2. Inject `db: AsyncSession` via `Depends(get_db)` for DB access
  3. Use `select()` (SQLAlchemy 2.0 style) instead of the legacy `query()`
"""

import uuid
from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.engine import RowMapping
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


@router.get("/{vehicle_id}/detail", summary="Get vehicle details with analytics")
async def get_vehicle_detail(
    vehicle_id: uuid.UUID,
    limit: int = Query(
        100, description="Max number of events to return per event type"
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Comprehensive vehicle detail endpoint with:
    - Vehicle info
    - Trip history
    - Driver list
    - Pipeline events aggregated by event type (for graphing)
    """
    # Get vehicle
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )

    # Get all trips for this vehicle, including route names and scores
    trips_rows = (
        (
            await db.execute(
                text(
                    """
                    SELECT t.id,
                           t.driver_id,
                           t.created_at,
                           t.status,
                           r.name AS route_name,
                           COALESCE(ts.score, t.safety_score) AS score
                    FROM trips t
                    LEFT JOIN routes r ON r.id = t.route_id
                      LEFT JOIN scoring_schema.trip_scores ts ON ts.trip_id = t.id::text
                      WHERE t.vehicle_id = :vehicle_id
                    ORDER BY t.created_at DESC
                    LIMIT 1000
                    """
                ),
                {"vehicle_id": str(vehicle_id)},
            )
        )
        .mappings()
        .all()
    )

    trip_ids = [str(row["id"]) for row in trips_rows]

    # Get unique drivers for this vehicle
    driver_ids = sorted(
        {str(row["driver_id"]) for row in trips_rows if row.get("driver_id")}
    )

    # Get pipeline events aggregated by event type
    events_by_type: dict[str, list[dict[str, Any]]] = {}
    if trip_ids:
        rows = (
            (
                await db.execute(
                    text(
                        """
                    SELECT 
                        event_type, 
                        event_id,
                        device_event_id,
                        timestamp, 
                        lat, 
                        lon,
                        details,
                        category,
                        priority,
                        status
                    FROM pipeline_events 
                    WHERE trip_id = ANY(:trip_ids)
                    ORDER BY timestamp ASC
                    """
                    ),
                    {"trip_ids": trip_ids},
                )
            )
            .mappings()
            .all()
        )

        for row in rows:
            event_type = row.get("event_type", "unknown")
            if event_type not in events_by_type:
                events_by_type[event_type] = []

            events_by_type[event_type].append(
                {
                    "event_id": row.get("event_id"),
                    "device_event_id": row.get("device_event_id"),
                    "timestamp": row.get("timestamp"),
                    "lat": row.get("lat"),
                    "lon": row.get("lon"),
                    "details": row.get("details") or {},
                    "category": row.get("category"),
                    "priority": row.get("priority"),
                    "status": row.get("status"),
                }
            )

        # Trim to limit per event type
        for event_type in events_by_type:
            events_by_type[event_type] = events_by_type[event_type][-limit:]

    # Vehicle-scoped safety events for the same trip set
    safety_rows: Sequence[RowMapping] = ()
    if trip_ids:
        safety_rows = (
            (
                await db.execute(
                    text(
                        """
                        SELECT h.event_id,
                               h.trip_id,
                               h.event_type,
                               h.severity,
                               h.event_timestamp,
                               h.lat,
                               h.lon,
                               h.location_name,
                               h.traffic_conditions,
                               h.weather_conditions,
                               d.decision,
                               d.action,
                               d.reason,
                               d.recommended_action
                        FROM safety_schema.harsh_events_analysis h
                        LEFT JOIN safety_schema.safety_decisions d ON d.event_id = h.event_id
                        WHERE h.trip_id = ANY(:trip_ids)
                        ORDER BY h.event_timestamp DESC
                        LIMIT 10
                        """
                    ),
                    {"trip_ids": trip_ids},
                )
            )
            .mappings()
            .all()
        )

    # Get trip score summary
    trip_scores: Sequence[RowMapping] = ()
    if trip_ids:
        try:
            trip_scores = (
                (
                    await db.execute(
                        text(
                            """
                    SELECT 
                        trip_id,
                        score,
                        score as behaviour_score,
                        FALSE as coaching_required
                    FROM scoring_schema.trip_scores
                    WHERE trip_id = ANY(:trip_ids)
                    """
                        ),
                        {"trip_ids": trip_ids},
                    )
                )
                .mappings()
                .all()
            )
        except Exception:
            # Scoring schema may not be populated yet, continue with empty scores
            trip_scores = ()

    score_map: dict[str, dict[str, Any]] = {
        str(row["trip_id"]): dict(row) for row in trip_scores
    }
    total_trips = len(trips_rows)
    avg_score = (
        sum(float(row.get("score") or 0) for row in trips_rows) / max(total_trips, 1)
        if total_trips
        else 0
    )

    return {
        "vehicle": {
            "id": str(vehicle.id),
            "license_plate": vehicle.license_plate,
            "model": vehicle.model,
            "status": vehicle.status,
            "fuel_level": vehicle.fuel_level,
            "created_at": (
                vehicle.created_at.isoformat() if vehicle.created_at else None
            ),
        },
        "statistics": {
            "total_trips": total_trips,
            "total_drivers": len(driver_ids),
            "avg_score": avg_score,
        },
        "trips": [
            {
                "id": str(row["id"]),
                "driver_id": str(row["driver_id"]),
                "created_at": (
                    row["created_at"].isoformat() if row["created_at"] else None
                ),
                "status": row["status"],
                "route_name": row.get("route_name"),
                "score": score_map.get(str(row["id"]), {}).get("score")
                or row.get("score"),
            }
            for row in trips_rows
        ],
        "drivers": driver_ids,
        "events_by_type": events_by_type,
        "safety_events": [
            {
                "event_id": row["event_id"],
                "trip_id": row["trip_id"],
                "event_type": row["event_type"],
                "severity": row["severity"],
                "event_timestamp": (
                    row["event_timestamp"].isoformat()
                    if row["event_timestamp"]
                    else None
                ),
                "lat": row["lat"],
                "lon": row["lon"],
                "location_name": row["location_name"],
                "traffic_conditions": row["traffic_conditions"],
                "weather_conditions": row["weather_conditions"],
                "decision": row["decision"],
                "action": row["action"],
                "reason": row["reason"],
                "recommended_action": row["recommended_action"],
            }
            for row in safety_rows
        ],
    }


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
