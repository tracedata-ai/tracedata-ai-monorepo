"""TraceData Backend — Tenants API Router."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import get_db
from api.models.tenant import Tenant
from api.schemas.tenant import TenantRead

router = APIRouter(prefix="/tenants", tags=["System"])


@router.get("/", response_model=list[TenantRead], summary="List all fleet operators")
async def list_tenants(
    db: AsyncSession = Depends(get_db),
) -> list[Tenant]:
    """Returns all registered fleet operators (tenants)."""
    result = await db.execute(select(Tenant))
    return list(result.scalars().all())
