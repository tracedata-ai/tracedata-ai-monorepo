"""TraceData Backend — Drivers API Router.

Endpoints:
  GET  /api/v1/drivers                    — List all drivers
  GET  /api/v1/drivers/{id}               — Get driver by UUID
  GET  /api/v1/drivers/{id}/profile       — Full driver profile (aggregated)
  POST /api/v1/drivers                    — Register a new driver
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from agents.scoring.features import score_gpa_from_value, score_label_from_value
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
        cache_key, [d.model_dump() for d in out], RedisSchema.Api.DRIVERS_TTL
    )
    return out


@router.get("/{driver_id}/profile", summary="Full driver profile")
async def get_driver_profile(
    driver_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Aggregates driver identity, vehicle, performance stats, trips, safety events and coaching."""

    # ── Driver + assigned vehicle ─────────────────────────────────────────────
    driver_row = (
        (
            await db.execute(
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
            )
        )
        .mappings()
        .first()
    )

    if not driver_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )

    # Open maintenance flag for assigned vehicle
    has_open_maintenance = False
    if driver_row["vehicle_id"]:
        maint = (
            await db.execute(
                text("""
                SELECT 1 FROM maintenance
                WHERE vehicle_id = :vid AND status IN ('scheduled','in_progress','overdue')
                LIMIT 1
            """),
                {"vid": driver_row["vehicle_id"]},
            )
        ).first()
        has_open_maintenance = maint is not None

    # ── Score stats ───────────────────────────────────────────────────────────
    score_stats: dict[str, Any] = dict(
        (
            (
                await db.execute(
                    text("""
            SELECT COUNT(*)        AS scored_trips,
                   AVG(score)      AS avg_score,
                   MIN(score)      AS min_score,
                   MAX(score)      AS max_score
            FROM   scoring_schema.trip_scores
            WHERE  driver_id = :did
        """),
                    {"did": str(driver_id)},
                )
            )
            .mappings()
            .first()
        )
        or {}
    )

    # ── Total trip count ──────────────────────────────────────────────────────
    trip_count_row = (
        (
            await db.execute(
                text("SELECT COUNT(*) AS total FROM trips WHERE driver_id = :did"),
                {"did": driver_id},
            )
        )
        .mappings()
        .first()
    )
    total_trips = int(trip_count_row["total"]) if trip_count_row else 0

    # ── Recent trips (last 15) ────────────────────────────────────────────────
    recent_trips_rows = (
        (
            await db.execute(
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
            )
        )
        .mappings()
        .all()
    )

    # ── Score trend (chronological, last 10 scored trips) ────────────────────
    score_trend = (
        (
            await db.execute(
                text("""
            SELECT score FROM scoring_schema.trip_scores
            WHERE  driver_id = :did
            ORDER  BY created_at DESC
            LIMIT  10
        """),
                {"did": str(driver_id)},
            )
        )
        .scalars()
        .all()
    )

    # ── XAI / SHAP explanations (last 5 scored trips) ────────────────────────
    xai_rows = (
        (
            await db.execute(
                text("""
            SELECT se.explanations
            FROM   scoring_schema.shap_explanations se
            JOIN   scoring_schema.trip_scores ts ON ts.score_id = se.score_id
            WHERE  ts.driver_id = :did
            ORDER  BY ts.created_at DESC
            LIMIT  5
        """),
                {"did": str(driver_id)},
            )
        )
        .mappings()
        .all()
    )

    # ── Safety event stats ────────────────────────────────────────────────────
    safety_stats: dict[str, Any] = dict(
        (
            (
                await db.execute(
                    text("""
            SELECT COUNT(*)                                            AS total_events,
                   COUNT(*) FILTER (WHERE h.severity = 'critical')   AS critical_events,
                   COUNT(*) FILTER (WHERE sd.decision = 'escalate')  AS escalated_events
            FROM   safety_schema.harsh_events_analysis h
            JOIN   trips t ON t.id = (
                CASE
                    WHEN h.trip_id ~ '^[0-9a-fA-F-]{36}$' THEN h.trip_id::uuid
                    ELSE NULL
                END
            )
            LEFT JOIN safety_schema.safety_decisions sd ON sd.event_id = h.event_id
            WHERE  t.driver_id = :did
        """),
                    {"did": driver_id},
                )
            )
            .mappings()
            .first()
        )
        or {}
    )

    # ── Recent safety events (last 10) ───────────────────────────────────────
    safety_events_rows = (
        (
            await db.execute(
                text("""
            SELECT h.event_id, h.trip_id, h.event_type, h.severity,
                   h.event_timestamp, h.lat, h.lon,
                   sd.decision
            FROM   safety_schema.harsh_events_analysis h
            JOIN   trips t ON t.id = (
                CASE
                    WHEN h.trip_id ~ '^[0-9a-fA-F-]{36}$' THEN h.trip_id::uuid
                    ELSE NULL
                END
            )
            LEFT JOIN safety_schema.safety_decisions sd ON sd.event_id = h.event_id
            WHERE  t.driver_id = :did
            ORDER  BY h.event_timestamp DESC
            LIMIT  10
        """),
                {"did": driver_id},
            )
        )
        .mappings()
        .all()
    )

    # ── Sentiment / feedback history (last 10) ───────────────────────────────
    sentiment_rows = (
        (
            await db.execute(
                text("""
            SELECT trip_id, feedback_text, sentiment_score, sentiment_label,
                   analysis, created_at
            FROM   sentiment_schema.feedback_sentiment
            WHERE  driver_id = :did
            ORDER  BY created_at DESC
            LIMIT  10
        """),
                {"did": str(driver_id)},
            )
        )
        .mappings()
        .all()
    )

    # ── Coaching history (last 10) ────────────────────────────────────────────
    coaching_rows = (
        (
            await db.execute(
                text("""
            SELECT c.coaching_category, c.priority, c.message, c.created_at
            FROM   coaching_schema.coaching c
            JOIN   trips t ON t.id = (
                CASE
                    WHEN c.trip_id ~ '^[0-9a-fA-F-]{36}$' THEN c.trip_id::uuid
                    ELSE NULL
                END
            )
            WHERE  t.driver_id = :did
            ORDER  BY c.created_at DESC
            LIMIT  10
        """),
                {"did": driver_id},
            )
        )
        .mappings()
        .all()
    )

    # ── Aggregate XAI across fetched trips ───────────────────────────────────
    _impact_weight = {"high": 3.0, "medium": 2.0, "low": 1.0}
    _feature_scores: dict[str, float] = {}
    _xai_method = "deterministic_heuristic"
    for row in xai_rows:
        expl = row["explanations"] or {}
        if expl.get("method") == "ml_shap":
            _xai_method = "ml_shap"
        for feat in expl.get("top_features", []):
            name = feat.get("feature", "")
            if not name:
                continue
            if "shap_value" in feat:
                _feature_scores[name] = _feature_scores.get(name, 0.0) + abs(
                    float(feat["shap_value"])
                )
            elif "impact" in feat:
                _feature_scores[name] = _feature_scores.get(
                    name, 0.0
                ) + _impact_weight.get(feat["impact"], 1.0)

    _FEATURE_LABELS: dict[str, str] = {
        "jerk_mean_avg": "Hard Braking / Jerk",
        "jerk_component": "Hard Braking / Jerk",
        "speed_std_avg": "Speed Variation",
        "speed_component": "Speed Score",
        "lateral_component": "Lateral Movement",
        "engine_component": "Engine Load",
        "idle_ratio": "Idle Time",
        "smoothness_score_avg": "Smoothness",
    }
    xai_top = sorted(_feature_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    xai_max = xai_top[0][1] if xai_top else 1.0
    xai_summary = (
        {
            "method": _xai_method,
            "trip_count": len(xai_rows),
            "top_features": [
                {
                    "feature": feat,
                    "label": _FEATURE_LABELS.get(feat, feat.replace("_", " ").title()),
                    "score": round(val, 4),
                    "pct": round(val / xai_max * 100, 1),
                }
                for feat, val in xai_top
            ],
        }
        if xai_top
        else None
    )

    # ── driver_score: avg_score mapped to 0–5 star scale ─────────────────────
    driver_score = (
        round(max(0.0, min(5.0, float(score_stats["avg_score"]) / 20.0)), 2)
        if score_stats.get("avg_score")
        else None
    )

    # ── Assemble ──────────────────────────────────────────────────────────────
    return {
        "id": str(driver_row["id"]),
        "first_name": driver_row["first_name"],
        "last_name": driver_row["last_name"],
        "email": driver_row["email"],
        "phone": driver_row["phone"],
        "license_number": driver_row["license_number"],
        "status": driver_row["status"],
        "experience_level": driver_row["experience_level"],
        "created_at": (
            driver_row["created_at"].isoformat() if driver_row["created_at"] else None
        ),
        "vehicle": (
            {
                "id": str(driver_row["vehicle_id"]),
                "license_plate": driver_row["license_plate"],
                "make": driver_row["make"],
                "model": driver_row["model"],
                "fuel_level": driver_row["fuel_level"],
                "has_open_maintenance": has_open_maintenance,
            }
            if driver_row["vehicle_id"]
            else None
        ),
        "stats": {
            "total_trips": total_trips,
            "scored_trips": int(score_stats.get("scored_trips") or 0),
            "avg_score": (
                round(float(score_stats["avg_score"]), 1)
                if score_stats.get("avg_score")
                else None
            ),
            "min_score": (
                round(float(score_stats["min_score"]), 1)
                if score_stats.get("min_score")
                else None
            ),
            "max_score": (
                round(float(score_stats["max_score"]), 1)
                if score_stats.get("max_score")
                else None
            ),
            "score_label": (
                score_label_from_value(float(score_stats["avg_score"]))
                if score_stats.get("avg_score")
                else None
            ),
            "score_gpa": (
                score_gpa_from_value(float(score_stats["avg_score"]))
                if score_stats.get("avg_score")
                else None
            ),
            "driver_score": driver_score,
            "total_events": int(safety_stats.get("total_events") or 0),
            "critical_events": int(safety_stats.get("critical_events") or 0),
            "escalated_events": int(safety_stats.get("escalated_events") or 0),
        },
        "xai_summary": xai_summary,
        "score_trend": [round(float(s), 1) for s in reversed(score_trend)],
        "recent_trips": [
            {
                "trip_id": str(r["id"]),
                "status": r["status"],
                "route_name": r["route_name"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "score": (
                    round(float(r["score"]), 1) if r["score"] is not None else None
                ),
            }
            for r in recent_trips_rows
        ],
        "safety_events": [
            {
                "event_id": r["event_id"],
                "trip_id": r["trip_id"],
                "event_type": r["event_type"],
                "severity": r["severity"],
                "decision": r["decision"],
                "event_timestamp": (
                    r["event_timestamp"].isoformat() if r["event_timestamp"] else None
                ),
                "lat": r["lat"],
                "lon": r["lon"],
            }
            for r in safety_events_rows
        ],
        "coaching": [
            {
                "category": r["coaching_category"],
                "priority": r["priority"],
                "message": r["message"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in coaching_rows
        ],
        "sentiment_history": [
            {
                "trip_id": r["trip_id"],
                "feedback_text": r["feedback_text"],
                "sentiment_label": r["sentiment_label"],
                "sentiment_score": r["sentiment_score"],
                "emotions": (r["analysis"] or {}).get("emotion_scores", {}),
                "explanation": (r["analysis"] or {}).get("explanation"),
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in sentiment_rows
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
