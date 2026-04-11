import asyncio
import os
import sys
from pathlib import Path

# Add app root to path for imports
sys.path.append(os.getcwd())

from sqlalchemy import text

from common.db.engine import engine
from common.models.orm import Base

_AGENT_SCHEMA_SQL = Path(__file__).resolve().with_name("agent_schemas.sql")


def _iter_sql_statements(sql_text: str):
    for chunk in sql_text.split(";"):
        lines = [
            line
            for line in chunk.splitlines()
            if line.strip() and not line.strip().startswith("--")
        ]
        statement = "\n".join(lines).strip()
        if statement:
            yield statement


async def init_db():
    print(f"Initializing database at {engine.url}...")
    try:
        async with engine.begin() as conn:
            # This will create all tables defined in models/orm.py
            await conn.run_sync(Base.metadata.create_all)
            schema_sql = _AGENT_SCHEMA_SQL.read_text(encoding="utf-8")
            for statement in _iter_sql_statements(schema_sql):
                await conn.execute(text(statement))
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")


if __name__ == "__main__":
    asyncio.run(init_db())
