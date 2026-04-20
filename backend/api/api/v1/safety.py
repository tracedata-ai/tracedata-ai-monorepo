"""
TraceData Backend — Safety Events API Router.

Serves data from agent-owned safety_schema tables:
  harsh_events_analysis  — per-event analysis with lat/lon and JSONB context
  safety_decisions       — agent decision (monitor/escalate) per event

Endpoints:
  GET /api/v1/safety/events/          — List all events (joined with decisions)
  GET /api/v1/safety/events/{event_id} — Full event detail
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import get_db, get_redis
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

router = APIRouter(prefix="/safety", tags=["Safety"])

_LIST_SQL = text("""
    SELECT
        h.id,
        h.event_id,
        h.trip_id,
        h.event_type,
        h.severity,
        h.event_timestamp,
        h.lat,
        h.lon,
        h.location_name,
        h.traffic_conditions,
        h.weather_conditions,
        h.analysis,
        h.created_at,
        d.decision_id,
        d.decision,
        d.action,
        d.reason,
        d.recommended_action,
        dr.first_name,
        dr.last_name
    FROM safety_schema.harsh_events_analysis h
    LEFT JOIN safety_schema.safety_decisions d ON d.event_id = h.event_id
    LEFT JOIN public.trips t ON t.id = (
        CASE
            WHEN h.trip_id ~ '^[0-9a-fA-F-]{36}$' THEN h.trip_id::uuid
            ELSE NULL
        END
    )
    LEFT JOIN public.drivers dr ON dr.id = t.driver_id
    ORDER BY h.created_at DESC
    LIMIT :limit OFFSET :offset
""")

_DETAIL_SQL = text("""
    SELECT
        h.id,
        h.event_id,
        h.trip_id,
        h.event_type,
        h.severity,
        h.event_timestamp,
        h.lat,
        h.lon,
        h.location_name,
        h.traffic_conditions,
        h.weather_conditions,
        h.analysis,
        h.created_at,
        d.decision_id,
        d.decision,
        d.action,
        d.reason,
        d.recommended_action,
        dr.first_name,
        dr.last_name
    FROM safety_schema.harsh_events_analysis h
    LEFT JOIN safety_schema.safety_decisions d ON d.event_id = h.event_id
    LEFT JOIN public.trips t ON t.id = (
        CASE
            WHEN h.trip_id ~ '^[0-9a-fA-F-]{36}$' THEN h.trip_id::uuid
            ELSE NULL
        END
    )
    LEFT JOIN public.drivers dr ON dr.id = t.driver_id
    WHERE h.event_id = :event_id
    LIMIT 1
""")


def _row_to_dict(row) -> dict:
    m = row._mapping
    analysis = m["analysis"] or {}
    trip_ctx = analysis.get("trip_context", {})
    return {
        "id": m["id"],
        "event_id": m["event_id"],
        "trip_id": m["trip_id"],
        "event_type": m["event_type"],
        "severity": m["severity"],
        "event_timestamp": (
            m["event_timestamp"].isoformat() if m["event_timestamp"] else None
        ),
        "lat": m["lat"],
        "lon": m["lon"],
        "location_name": m["location_name"],
        "traffic_conditions": m["traffic_conditions"],
        "weather_conditions": m["weather_conditions"],
        "created_at": m["created_at"].isoformat() if m["created_at"] else None,
        # Decision fields
        "decision_id": m["decision_id"],
        "decision": m["decision"],
        "action": m["action"],
        "reason": m["reason"],
        "recommended_action": m["recommended_action"],
        # Extracted from analysis JSONB
        "assessed_severity": analysis.get("assessed_severity"),
        "llm_path": analysis.get("llm_path", False),
        "analysis_reason": analysis.get("reason"),
        "video_url": (
            analysis.get("primary_event_evidence")
            or trip_ctx.get("primary_event_evidence", {})
        ).get("video_url"),
        "truck_id": trip_ctx.get("truck_id"),
        "driver_id": trip_ctx.get("driver_id"),
        "driver_name": (
            f"{m['first_name']} {m['last_name']}".strip() if m["first_name"] else None
        ),
        "route_name": trip_ctx.get("route_name"),
        "trip_started_at": trip_ctx.get("started_at"),
    }


@router.get("/events/", summary="List safety events with decisions")
async def list_safety_events(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
) -> list[dict]:
    cache_key = RedisSchema.Api.safety_list(skip, limit)
    if cached := await redis.cache_get(cache_key):
        return cached  # type: ignore[return-value]

    result = await db.execute(_LIST_SQL, {"limit": limit, "offset": skip})
    out = [_row_to_dict(row) for row in result.fetchall()]
    await redis.cache_set(cache_key, out, RedisSchema.Api.SAFETY_TTL)
    return out


@router.get("/events/{event_id}", summary="Get full safety event detail")
async def get_safety_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(_DETAIL_SQL, {"event_id": event_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return _row_to_dict(row)
