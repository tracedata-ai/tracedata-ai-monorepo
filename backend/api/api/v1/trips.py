"""TraceData Backend — Trips API Router.

Endpoints:
  GET  /api/v1/trips          — List all trips (with optional status filter)
  GET  /api/v1/trips/{id}     — Get trip by UUID (includes safety score)
  POST /api/v1/trips          — Start a new trip (Start-of-Trip ping)
"""

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from agents.scoring.features import score_gpa_from_value, score_label_from_value
from api.api.deps import get_db, get_redis
from api.models.trip import Trip
from api.schemas.trip import TripCreate, TripRead
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get("/", response_model=list[TripRead], summary="List all trips")
async def list_trips(
    skip: int = 0,
    limit: int = 50,
    tenant_id: uuid.UUID | None = None,
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by status: active | completed | zombie",
    ),
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
) -> list[TripRead]:
    cache_key = RedisSchema.Api.trips_list(
        str(tenant_id or "all"), status_filter or "all", skip, limit
    )
    if cached := await redis.cache_get(cache_key):
        return [TripRead(**item) for item in cached]

    query = select(Trip).offset(skip).limit(limit)
    if status_filter:
        query = query.where(Trip.status == status_filter)
    if tenant_id:
        query = query.where(Trip.tenant_id == tenant_id)
    result = await db.execute(query)
    trips = list(result.scalars().all())

    # Backfill safety_score from scoring_schema
    if trips:
        ids_missing_score = [str(t.id) for t in trips if t.safety_score is None]
        if ids_missing_score:
            rows = (
                (
                    await db.execute(
                        text(
                            "SELECT trip_id, score FROM scoring_schema.trip_scores "
                            "WHERE trip_id = ANY(:ids)"
                        ),
                        {"ids": ids_missing_score},
                    )
                )
                .mappings()
                .all()
            )
            score_map: dict[str, Decimal] = {r["trip_id"]: r["score"] for r in rows}
            for trip in trips:
                if trip.safety_score is None:
                    trip.safety_score = score_map.get(str(trip.id))

    out = [TripRead.model_validate(t) for t in trips]
    await redis.cache_set(
        cache_key, [t.model_dump() for t in out], RedisSchema.Api.TRIPS_TTL
    )
    return out


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )
    return trip


@router.get("/{trip_id}/detail", summary="Full trip detail from all agent schemas")
async def get_trip_detail(
    trip_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Aggregates trip data from the domain trips table plus all agent-owned schemas:
    scoring, safety, coaching, and sentiment.  Used by the Trip Detail page.
    """
    from sqlalchemy import text

    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    tid = str(trip_id)

    # ── Driver / vehicle / route names ────────────────────────────────────────
    meta = await db.execute(
        text("""
            SELECT d.first_name || ' ' || d.last_name AS driver_name,
                   v.license_plate, v.make, v.model,
                   r.name AS route_name, r.start_location, r.end_location, r.distance_km
            FROM   trips t
            LEFT JOIN drivers  d ON t.driver_id  = d.id
            LEFT JOIN vehicles v ON t.vehicle_id = v.id
            LEFT JOIN routes   r ON t.route_id   = r.id
            WHERE  t.id = :tid
        """),
        {"tid": trip_id},
    )
    meta_row = meta.mappings().first() or {}

    # ── Scoring ───────────────────────────────────────────────────────────────
    score_row = (
        (
            await db.execute(
                text(
                    "SELECT score, score_breakdown, scoring_narrative, driver_id FROM scoring_schema.trip_scores WHERE trip_id = :tid LIMIT 1"
                ),
                {"tid": tid},
            )
        )
        .mappings()
        .first()
    )

    # Driver score: average of all scored trips for this driver, mapped to 0–5
    driver_score: float | None = None
    if score_row:
        avg_row = (
            (
                await db.execute(
                    text(
                        "SELECT AVG(score) AS avg_score FROM scoring_schema.trip_scores WHERE driver_id = :did"
                    ),
                    {"did": score_row["driver_id"]},
                )
            )
            .mappings()
            .first()
        )
        if avg_row and avg_row["avg_score"] is not None:
            driver_score = round(
                max(0.0, min(5.0, float(avg_row["avg_score"]) / 20.0)), 2
            )

    # ── Safety events ─────────────────────────────────────────────────────────
    safety_rows = (
        (
            await db.execute(
                text("""
            SELECT h.event_id, h.event_type, h.severity, h.lat, h.lon,
                   h.location_name, h.event_timestamp, h.traffic_conditions, h.weather_conditions,
                   d.decision, d.action, d.reason, d.recommended_action
            FROM   safety_schema.harsh_events_analysis h
            LEFT JOIN safety_schema.safety_decisions d ON d.event_id = h.event_id
            WHERE  h.trip_id = :tid
            ORDER  BY h.event_timestamp
        """),
                {"tid": tid},
            )
        )
        .mappings()
        .all()
    )

    # ── Coaching ──────────────────────────────────────────────────────────────
    coaching_rows = (
        (
            await db.execute(
                text(
                    "SELECT coaching_category, priority, message FROM coaching_schema.coaching WHERE trip_id = :tid ORDER BY created_at"
                ),
                {"tid": tid},
            )
        )
        .mappings()
        .all()
    )

    # ── Sentiment ─────────────────────────────────────────────────────────────
    sentiment_row = (
        (
            await db.execute(
                text(
                    "SELECT feedback_text, sentiment_score, sentiment_label, analysis FROM sentiment_schema.feedback_sentiment WHERE trip_id = :tid LIMIT 1"
                ),
                {"tid": tid},
            )
        )
        .mappings()
        .first()
    )

    return {
        "trip_id": tid,
        "status": trip.status,
        "created_at": trip.created_at.isoformat() if trip.created_at else None,
        "driver_name": meta_row.get("driver_name"),
        "license_plate": meta_row.get("license_plate"),
        "vehicle": f"{meta_row.get('make', '')} {meta_row.get('model', '')}".strip()
        or None,
        "route_name": meta_row.get("route_name"),
        "route_from": meta_row.get("start_location"),
        "route_to": meta_row.get("end_location"),
        "distance_km": float(meta_row.get("distance_km") or 0) or None,
        "scoring": {
            "score": score_row.get("score") if score_row else None,
            "driver_score": driver_score,
            "breakdown": (
                dict(score_row.get("score_breakdown") or {}) if score_row else {}
            ),
            "narrative": score_row.get("scoring_narrative") if score_row else None,
            "score_label": (
                score_label_from_value(float(score_row["score"]))
                if score_row and score_row.get("score") is not None
                else None
            ),
            "score_gpa": (
                score_gpa_from_value(float(score_row["score"]))
                if score_row and score_row.get("score") is not None
                else None
            ),
        },
        "safety_events": [
            {
                "event_id": r["event_id"],
                "event_type": r["event_type"],
                "severity": r["severity"],
                "lat": r["lat"],
                "lon": r["lon"],
                "location_name": r["location_name"],
                "timestamp": (
                    r["event_timestamp"].isoformat() if r["event_timestamp"] else None
                ),
                "traffic": r["traffic_conditions"],
                "weather": r["weather_conditions"],
                "decision": r["decision"],
                "action": r["action"],
                "reason": r["reason"],
                "recommended_action": r["recommended_action"],
            }
            for r in safety_rows
        ],
        "coaching": [
            {
                "category": r["coaching_category"],
                "priority": r["priority"],
                "message": r["message"],
            }
            for r in coaching_rows
        ],
        "sentiment": (
            {
                "score": sentiment_row.get("sentiment_score"),
                "label": sentiment_row.get("sentiment_label"),
                "feedback_text": sentiment_row.get("feedback_text"),
                "explanation": (sentiment_row.get("analysis") or {}).get("explanation"),
                "emotions": (sentiment_row.get("analysis") or {}).get(
                    "emotion_scores", {}
                ),
            }
            if sentiment_row
            else None
        ),
    }


@router.post(
    "/",
    response_model=TripRead,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new trip",
)
async def start_trip(
    payload: TripCreate,
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
) -> Trip:
    trip = Trip(**payload.model_dump())
    db.add(trip)
    await db.flush()
    await db.refresh(trip)
    await redis.cache_delete(RedisSchema.Api.trips_list("all", "all", 0, 50))
    return trip
