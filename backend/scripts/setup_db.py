import asyncio
import os
import sys

# Add app root to path for imports
sys.path.append(os.getcwd())

from common.db.engine import engine
from common.models.orm import Base


async def init_db():
    print(f"Initializing database at {engine.url}...")
    try:
        async with engine.begin() as conn:
            # This will create all tables defined in models/orm.py
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")


if __name__ == "__main__":
    asyncio.run(init_db())
