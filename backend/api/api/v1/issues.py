"""TraceData Backend — Issues API Router.

Endpoints:
  GET  /api/v1/issues              — List all issues (optional trip filter)
  GET  /api/v1/issues/{id}         — Get issue by UUID
  POST /api/v1/issues              — Log a new driving issue
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import get_db, get_redis
from api.models.issue import Issue
from api.schemas.issue import IssueCreate, IssueRead
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.get("/", response_model=list[IssueRead], summary="List all issues")
async def list_issues(
    skip: int = 0,
    limit: int = 50,
    tenant_id: uuid.UUID | None = None,
    trip_id: uuid.UUID | None = Query(None, description="Filter by trip UUID"),
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
) -> list[IssueRead]:
    cache_key = RedisSchema.Api.issues_list(
        str(tenant_id or "all"), str(trip_id or "all"), skip, limit
    )
    if cached := await redis.cache_get(cache_key):
        return [IssueRead(**item) for item in cached]

    query = select(Issue).offset(skip).limit(limit)
    if trip_id:
        query = query.where(Issue.trip_id == trip_id)
    if tenant_id:
        query = query.where(Issue.tenant_id == tenant_id)
    result = await db.execute(query)
    out = [IssueRead.model_validate(i) for i in result.scalars().all()]

    await redis.cache_set(cache_key, [i.model_dump() for i in out], RedisSchema.Api.ISSUES_TTL)
    return out


@router.get("/{issue_id}", response_model=IssueRead, summary="Get issue by ID")
async def get_issue(
    issue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Issue:
    """Fetches a single issue by UUID. Returns 404 if not found."""
    issue = await db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
        )
    return issue


@router.post(
    "/",
    response_model=IssueRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log a driving issue",
)
async def create_issue(
    payload: IssueCreate,
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
) -> Issue:
    """Logs a classified driving event. In the full system, this triggers agent routing."""
    issue = Issue(**payload.model_dump())
    db.add(issue)
    await db.flush()
    await db.refresh(issue)
    await redis.cache_delete(RedisSchema.Api.issues_list("all", "all", 0, 50))
    return issue
