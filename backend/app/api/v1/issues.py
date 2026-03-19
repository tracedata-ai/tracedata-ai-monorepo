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

from app.api.deps import get_db
from app.models.issue import Issue
from app.schemas.issue import IssueCreate, IssueRead

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.get("/", response_model=list[IssueRead], summary="List all issues")
async def list_issues(
    skip: int = 0,
    limit: int = 50,
    trip_id: uuid.UUID | None = Query(None, description="Filter by trip UUID"),
    db: AsyncSession = Depends(get_db),
) -> list[Issue]:
    """
    Returns driving issues.

    TIP: Filter by `?trip_id=<uuid>` to see all incidents for a specific trip.
    This is how the frontend dashboard loads the issue list for a trip detail page.
    """
    query = select(Issue).offset(skip).limit(limit)
    if trip_id:
        query = query.where(Issue.trip_id == trip_id)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{issue_id}", response_model=IssueRead, summary="Get issue by ID")
async def get_issue(
    issue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Issue:
    """Fetches a single issue by UUID. Returns 404 if not found."""
    issue = await db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
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
) -> Issue:
    """Logs a classified driving event. In the full system, this triggers agent routing."""
    issue = Issue(**payload.model_dump())
    db.add(issue)
    await db.flush()
    await db.refresh(issue)
    return issue
