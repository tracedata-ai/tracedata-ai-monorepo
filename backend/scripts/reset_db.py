import asyncio
import os
import sys

# Add app root to path for imports
sys.path.append(os.getcwd())

from common.db.engine import engine
from common.models.orm import Base


async def reset_db():
    print(f"Resetting database at {engine.url}...")
    try:
        async with engine.begin() as conn:
            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database reset successfully!")
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")


if __name__ == "__main__":
    asyncio.run(reset_db())
