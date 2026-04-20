"""TraceData Backend — Embeddings / Semantic Search API.

Endpoints:
  GET  /api/v1/embeddings/search              — Semantic similarity search over agent outputs
  GET  /api/v1/embeddings/related/event/{id}  — 5 semantically similar safety events
  GET  /api/v1/embeddings/stats               — Count of stored embeddings by content_type
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import get_db
from common.embeddings.client import embed_text

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


@router.get("/search", summary="Semantic similarity search over agent outputs")
async def search_embeddings(
    q: str = Query(..., description="Natural-language query"),
    content_type: str | None = Query(
        None,
        description="Filter: driver_feedback | coaching_message | safety_decision | scoring_narrative",
    ),
    driver_id: str | None = Query(None, description="Filter by driver UUID"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Embed the query and return the nearest stored embeddings by cosine distance."""
    vector = await embed_text(q)
    if vector is None:
        return []

    vec_str = "[" + ",".join(f"{x:.8f}" for x in vector) + "]"

    params: dict = {
        "vec": vec_str,
        "limit": limit,
        "ctype": content_type,
        "driver_id": driver_id,
    }

    rows = (
        (
            await db.execute(
                text("""
            SELECT id, content_type, source_id, driver_id, trip_id, content, created_at,
                   1 - (embedding <=> cast(:vec as vector)) AS similarity
            FROM   vector_schema.embeddings
            WHERE  embedding IS NOT NULL
              AND  (:ctype IS NULL OR content_type = :ctype)
              AND  (:driver_id IS NULL OR driver_id = :driver_id)
            ORDER  BY embedding <=> cast(:vec as vector)
            LIMIT  :limit
        """),
                params,
            )
        )
        .mappings()
        .all()
    )

    return [
        {
            "id": r["id"],
            "content_type": r["content_type"],
            "source_id": r["source_id"],
            "driver_id": r["driver_id"],
            "trip_id": r["trip_id"],
            "content": r["content"],
            "similarity": round(float(r["similarity"]), 4),
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        }
        for r in rows
    ]


@router.get("/related/event/{event_id}", summary="5 semantically similar safety events")
async def related_events(
    event_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Reuses the stored embedding for event_id — no OpenAI call needed."""
    rows = (
        (
            await db.execute(
                text("""
            WITH target AS (
                SELECT embedding
                FROM   vector_schema.embeddings
                WHERE  source_id    = :eid
                  AND  content_type = 'safety_decision'
                  AND  embedding    IS NOT NULL
                LIMIT  1
            )
            SELECT
                e.source_id                              AS event_id,
                e.trip_id,
                e.driver_id,
                1 - (e.embedding <=> t.embedding)        AS similarity,
                h.event_type,
                h.severity,
                h.event_timestamp,
                h.lat,
                h.lon,
                sd.decision,
                sd.reason
            FROM   vector_schema.embeddings e
            CROSS JOIN target t
            LEFT JOIN safety_schema.harsh_events_analysis h  ON h.event_id = e.source_id
            LEFT JOIN safety_schema.safety_decisions      sd ON sd.event_id = e.source_id
            WHERE  e.content_type = 'safety_decision'
              AND  e.source_id   != :eid
              AND  e.embedding    IS NOT NULL
            ORDER  BY e.embedding <=> t.embedding
            LIMIT  :limit
                """),
                {"eid": event_id, "limit": limit},
            )
        )
        .mappings()
        .all()
    )

    return [
        {
            "event_id": r["event_id"],
            "trip_id": r["trip_id"],
            "driver_id": r["driver_id"],
            "similarity": round(float(r["similarity"]), 4),
            "event_type": r["event_type"],
            "severity": r["severity"],
            "decision": r["decision"],
            "reason": r["reason"],
            "lat": r["lat"],
            "lon": r["lon"],
            "event_timestamp": (
                r["event_timestamp"].isoformat() if r["event_timestamp"] else None
            ),
        }
        for r in rows
    ]


@router.get("/stats", summary="Count of stored embeddings by type")
async def embedding_stats(db: AsyncSession = Depends(get_db)) -> list[dict]:
    rows = (await db.execute(text("""
            SELECT content_type, COUNT(*) AS total
            FROM   vector_schema.embeddings
            GROUP  BY content_type
            ORDER  BY total DESC
        """))).mappings().all()
    return [{"content_type": r["content_type"], "total": int(r["total"])} for r in rows]
