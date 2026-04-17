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

from api.api.deps import get_db
from api.models.trip import Trip
from api.schemas.trip import TripCreate, TripRead

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
) -> list[Trip]:
    """
    Returns trips with optional status and tenant filtering.

    TIP: Try `?status=active` to see only live trips,
    or `?tenant_id=<uuid>` to see trips for a specific operator.
    """
    query = select(Trip).offset(skip).limit(limit)
    if status_filter:
        query = query.where(Trip.status == status_filter)
    if tenant_id:
        query = query.where(Trip.tenant_id == tenant_id)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

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
    score_row = (await db.execute(
        text("SELECT score, score_breakdown, scoring_narrative FROM scoring_schema.trip_scores WHERE trip_id = :tid LIMIT 1"),
        {"tid": tid},
    )).mappings().first()

    # ── Safety events ─────────────────────────────────────────────────────────
    safety_rows = (await db.execute(
        text("""
            SELECT h.event_id, h.event_type, h.severity, h.lat, h.lon,
                   h.event_timestamp, h.traffic_conditions, h.weather_conditions,
                   d.decision, d.action, d.reason, d.recommended_action
            FROM   safety_schema.harsh_events_analysis h
            LEFT JOIN safety_schema.safety_decisions d ON d.event_id = h.event_id
            WHERE  h.trip_id = :tid
            ORDER  BY h.event_timestamp
        """),
        {"tid": tid},
    )).mappings().all()

    # ── Coaching ──────────────────────────────────────────────────────────────
    coaching_rows = (await db.execute(
        text("SELECT coaching_category, priority, message FROM coaching_schema.coaching WHERE trip_id = :tid ORDER BY created_at"),
        {"tid": tid},
    )).mappings().all()

    # ── Sentiment ─────────────────────────────────────────────────────────────
    sentiment_row = (await db.execute(
        text("SELECT sentiment_score, sentiment_label, analysis FROM sentiment_schema.feedback_sentiment WHERE trip_id = :tid LIMIT 1"),
        {"tid": tid},
    )).mappings().first()

    return {
        "trip_id": tid,
        "status": trip.status,
        "created_at": trip.created_at.isoformat() if trip.created_at else None,
        "driver_name": meta_row.get("driver_name"),
        "license_plate": meta_row.get("license_plate"),
        "vehicle": f"{meta_row.get('make', '')} {meta_row.get('model', '')}".strip() or None,
        "route_name": meta_row.get("route_name"),
        "route_from": meta_row.get("start_location"),
        "route_to": meta_row.get("end_location"),
        "distance_km": float(meta_row.get("distance_km") or 0) or None,
        "scoring": {
            "score": score_row.get("score") if score_row else None,
            "breakdown": dict(score_row.get("score_breakdown") or {}) if score_row else {},
            "narrative": score_row.get("scoring_narrative") if score_row else None,
        },
        "safety_events": [
            {
                "event_id": r["event_id"],
                "event_type": r["event_type"],
                "severity": r["severity"],
                "lat": r["lat"],
                "lon": r["lon"],
                "timestamp": r["event_timestamp"].isoformat() if r["event_timestamp"] else None,
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
            {"category": r["coaching_category"], "priority": r["priority"], "message": r["message"]}
            for r in coaching_rows
        ],
        "sentiment": {
            "score": sentiment_row.get("sentiment_score") if sentiment_row else None,
            "label": sentiment_row.get("sentiment_label") if sentiment_row else None,
            "emotions": (sentiment_row.get("analysis") or {}).get("emotion_scores", {}) if sentiment_row else {},
        } if sentiment_row else None,
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
