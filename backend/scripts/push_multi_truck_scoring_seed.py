"""
Multi-truck load seed (5 trucks × N trips × 3 events) for E2E / load-style scoring tests.

Replaces the old ``scoring_test_data.py``. Implementation lives in
``common/workflow_fixtures/multi_truck_scoring_seed.py``.

Usage (from ``backend/``):

  REDIS_URL=redis://localhost:6379/0 python scripts/push_multi_truck_scoring_seed.py
  python scripts/push_multi_truck_scoring_seed.py --trips-per-truck 5

See ``docs/workflow_testing.md``.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from common.config.settings import get_settings
from common.workflow_fixtures.multi_truck_scoring_seed import push_multi_truck_scoring_seed


async def main() -> None:
    p = argparse.ArgumentParser(description="Push multi-truck scoring seed to Redis buffers")
    p.add_argument(
        "--redis-url",
        default=None,
        help="Override Redis URL (default: REDIS_URL or settings)",
    )
    p.add_argument("--trips-per-truck", type=int, default=10)
    args = p.parse_args()

    url = args.redis_url or os.environ.get("REDIS_URL") or get_settings().redis_url
    summary = await push_multi_truck_scoring_seed(
        redis_url=url,
        trips_per_truck=args.trips_per_truck,
    )

    print("\n[OK] Multi-truck seed pushed")
    print(f"  trucks:            {summary['trucks']}")
    print(f"  trips per truck:   {summary['trips_per_truck']}")
    print(f"  total trips:       {summary['trips_total']}")
    print(f"  total ZADD events: {summary['events_total']}")


if __name__ == "__main__":
    asyncio.run(main())
