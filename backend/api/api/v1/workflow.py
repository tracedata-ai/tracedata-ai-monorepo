"""Workflow runtime views (pipeline tables) for live operations UI."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import get_db

router = APIRouter(prefix="/workflow", tags=["System"])


class WorkflowTripRead(BaseModel):
    trip_id: str
    driver_id: str
    truck_id: str
    status: str
    started_at: str | None = None
    updated_at: str | None = None


@router.get(
    "/trips",
    response_model=list[WorkflowTripRead],
    summary="List pipeline workflow trips",
)
async def list_workflow_trips(
    status: str | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[WorkflowTripRead]:
    query = """
        SELECT trip_id, driver_id, truck_id, status,
               started_at::text AS started_at,
               updated_at::text AS updated_at
        FROM pipeline_trips
    """
    params: dict[str, object] = {"limit": limit}
    if status:
        query += " WHERE status = :status"
        params["status"] = status
    query += " ORDER BY updated_at DESC NULLS LAST LIMIT :limit"

    result = await db.execute(text(query), params)
    return [WorkflowTripRead(**dict(row._mapping)) for row in result]
