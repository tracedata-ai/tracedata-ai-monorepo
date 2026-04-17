"""TraceData Backend — Drivers API Router.

Endpoints:
  GET  /api/v1/drivers                    — List all drivers
  GET  /api/v1/drivers/{id}               — Get driver by UUID
  GET  /api/v1/drivers/{id}/profile       — Full driver profile (aggregated)
  POST /api/v1/drivers                    — Register a new driver
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
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

    await redis.cache_set(cache_key, [d.model_dump() for d in out], RedisSchema.Api.DRIVERS_TTL)
    return out


@router.get("/{driver_id}/profile", summary="Full driver profile")
async def get_driver_profile(
    driver_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Aggregates driver identity, vehicle, performance stats, trips, safety events and coaching."""

    # ── Driver + assigned vehicle ─────────────────────────────────────────────
    driver_row = (await db.execute(
        text("""
            SELECT d.id, d.first_name, d.last_name, d.email, d.phone,
                   d.license_number, d.status, d.experience_level, d.created_at,
                   v.id        AS vehicle_id,
                   v.license_plate,
                   v.make,
                   v.model,
                   v.fuel_level
            FROM   drivers d
            LEFT JOIN vehicles v ON v.id = d.vehicle_id
            WHERE  d.id = :did
        """),
        {"did": driver_id},
    )).mappings().first()

    if not driver_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")

    # Open maintenance flag for assigned vehicle
    has_open_maintenance = False
    if driver_row["vehicle_id"]:
        maint = (await db.execute(
            text("""
                SELECT 1 FROM maintenance
                WHERE vehicle_id = :vid AND status IN ('scheduled','in_progress','overdue')
                LIMIT 1
            """),
            {"vid": driver_row["vehicle_id"]},
        )).first()
        has_open_maintenance = maint is not None

    # ── Score stats ───────────────────────────────────────────────────────────
    score_stats = (await db.execute(
        text("""
            SELECT COUNT(*)        AS scored_trips,
                   AVG(score)      AS avg_score,
                   MIN(score)      AS min_score,
                   MAX(score)      AS max_score
            FROM   scoring_schema.trip_scores
            WHERE  driver_id = :did
        """),
        {"did": str(driver_id)},
    )).mappings().first() or {}

    # ── Total trip count ──────────────────────────────────────────────────────
    trip_count_row = (await db.execute(
        text("SELECT COUNT(*) AS total FROM trips WHERE driver_id = :did"),
        {"did": driver_id},
    )).mappings().first()
    total_trips = int(trip_count_row["total"]) if trip_count_row else 0

    # ── Recent trips (last 15) ────────────────────────────────────────────────
    recent_trips_rows = (await db.execute(
        text("""
            SELECT t.id, t.status, t.created_at,
                   r.name   AS route_name,
                   ts.score
            FROM   trips t
            LEFT JOIN routes r ON r.id = t.route_id
            LEFT JOIN scoring_schema.trip_scores ts ON ts.trip_id = t.id::text
            WHERE  t.driver_id = :did
            ORDER  BY t.created_at DESC
            LIMIT  15
        """),
        {"did": driver_id},
    )).mappings().all()

    # ── Score trend (chronological, last 10 scored trips) ────────────────────
    score_trend = (await db.execute(
        text("""
            SELECT score FROM scoring_schema.trip_scores
            WHERE  driver_id = :did
            ORDER  BY created_at DESC
            LIMIT  10
        """),
        {"did": str(driver_id)},
    )).scalars().all()

    # ── Safety event stats ────────────────────────────────────────────────────
    safety_stats = (await db.execute(
        text("""
            SELECT COUNT(*)                                            AS total_events,
                   COUNT(*) FILTER (WHERE h.severity = 'critical')   AS critical_events,
                   COUNT(*) FILTER (WHERE sd.decision = 'escalate')  AS escalated_events
            FROM   safety_schema.harsh_events_analysis h
            JOIN   trips t ON t.id = h.trip_id::uuid
            LEFT JOIN safety_schema.safety_decisions sd ON sd.event_id = h.event_id
            WHERE  t.driver_id = :did
        """),
        {"did": driver_id},
    )).mappings().first() or {}

    # ── Recent safety events (last 10) ───────────────────────────────────────
    safety_events_rows = (await db.execute(
        text("""
            SELECT h.event_id, h.trip_id, h.event_type, h.severity,
                   h.event_timestamp, h.lat, h.lon,
                   sd.decision
            FROM   safety_schema.harsh_events_analysis h
            JOIN   trips t ON t.id = h.trip_id::uuid
            LEFT JOIN safety_schema.safety_decisions sd ON sd.event_id = h.event_id
            WHERE  t.driver_id = :did
            ORDER  BY h.event_timestamp DESC
            LIMIT  10
        """),
        {"did": driver_id},
    )).mappings().all()

    # ── Coaching history (last 10) ────────────────────────────────────────────
    coaching_rows = (await db.execute(
        text("""
            SELECT c.coaching_category, c.priority, c.message, c.created_at
            FROM   coaching_schema.coaching c
            JOIN   trips t ON t.id = c.trip_id::uuid
            WHERE  t.driver_id = :did
            ORDER  BY c.created_at DESC
            LIMIT  10
        """),
        {"did": driver_id},
    )).mappings().all()

    # ── Assemble ──────────────────────────────────────────────────────────────
    return {
        "id":               str(driver_row["id"]),
        "first_name":       driver_row["first_name"],
        "last_name":        driver_row["last_name"],
        "email":            driver_row["email"],
        "phone":            driver_row["phone"],
        "license_number":   driver_row["license_number"],
        "status":           driver_row["status"],
        "experience_level": driver_row["experience_level"],
        "created_at":       driver_row["created_at"].isoformat() if driver_row["created_at"] else None,
        "vehicle": {
            "id":                  str(driver_row["vehicle_id"]),
            "license_plate":       driver_row["license_plate"],
            "make":                driver_row["make"],
            "model":               driver_row["model"],
            "fuel_level":          driver_row["fuel_level"],
            "has_open_maintenance": has_open_maintenance,
        } if driver_row["vehicle_id"] else None,
        "stats": {
            "total_trips":      total_trips,
            "scored_trips":     int(score_stats.get("scored_trips") or 0),
            "avg_score":        round(float(score_stats["avg_score"]), 1) if score_stats.get("avg_score") else None,
            "min_score":        round(float(score_stats["min_score"]), 1) if score_stats.get("min_score") else None,
            "max_score":        round(float(score_stats["max_score"]), 1) if score_stats.get("max_score") else None,
            "total_events":     int(safety_stats.get("total_events") or 0),
            "critical_events":  int(safety_stats.get("critical_events") or 0),
            "escalated_events": int(safety_stats.get("escalated_events") or 0),
        },
        "score_trend": [round(float(s), 1) for s in reversed(score_trend)],
        "recent_trips": [
            {
                "trip_id":    str(r["id"]),
                "status":     r["status"],
                "route_name": r["route_name"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "score":      round(float(r["score"]), 1) if r["score"] is not None else None,
            }
            for r in recent_trips_rows
        ],
        "safety_events": [
            {
                "event_id":        r["event_id"],
                "trip_id":         r["trip_id"],
                "event_type":      r["event_type"],
                "severity":        r["severity"],
                "decision":        r["decision"],
                "event_timestamp": r["event_timestamp"].isoformat() if r["event_timestamp"] else None,
                "lat":             r["lat"],
                "lon":             r["lon"],
            }
            for r in safety_events_rows
        ],
        "coaching": [
            {
                "category":   r["coaching_category"],
                "priority":   r["priority"],
                "message":    r["message"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in coaching_rows
        ],
    }


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
