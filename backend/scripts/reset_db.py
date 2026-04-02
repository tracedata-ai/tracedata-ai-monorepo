"""
Postgres-only schema reset (legacy).

For Redis + Postgres together, use ``scripts/clean_datastores.py``.
See ``docs/workflow_testing.md`` for fixture-based pipeline tests.
"""

import asyncio
import os
import sys

# Add app root to path for imports
sys.path.append(os.getcwd())

import api.models as _models  # noqa: F401
from api.models.base import Base
from common.db.engine import engine
from sqlalchemy import text


async def reset_db():
    print(f"Resetting database at {engine.url}...")
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS scoring_schema"))
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database reset successfully!")
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")


if __name__ == "__main__":
    asyncio.run(reset_db())
