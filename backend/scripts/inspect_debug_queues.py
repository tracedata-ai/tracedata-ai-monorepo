"""
Debug Queue Inspector — View telemetry pipeline queues with TTL.

Shows:
  - Raw buffer (pre-ingestion) — debug:telemetry:{truck_id}:buffer
  - Processed queue (post-ingestion) — debug:telemetry:{truck_id}:processed
  - Rejection/DLQ status

All debug queues have 1-hour TTL for observability without filling Redis.

Usage:
  python inspect_debug_queues.py              # Show summary of all trucks
  python inspect_debug_queues.py TK001        # Show detailed view for TK001
  python inspect_debug_queues.py watch        # Live refresh (5s interval)
"""

import asyncio
import json
import sys
from datetime import UTC, datetime

import redis.asyncio as redis


async def show_all_trucks():
    """Show summary across all trucks with debug queues."""
    r = await redis.from_url("redis://localhost:6379/0", decode_responses=True)

    try:
        print("\n" + "=" * 80)
        print(
            "╔════════════════════════════════════════════════════════════════════════════╗"
        )
        print(
            "║                    DEBUG QUEUE INSPECTOR - ALL TRUCKS                     ║"
        )
        print(
            "╚════════════════════════════════════════════════════════════════════════════╝"
        )
        print()

        buffer_keys = await r.keys("debug:telemetry:*:buffer")

        if not buffer_keys:
            print(
                "❌ No debug queues found. Send telemetry with debug enabled to populate them."
            )
            await r.aclose()
            return

        trucks_data = {}
        for buffer_key in sorted(buffer_keys):
            truck_id = buffer_key.split(":")[2]
            processed_key = f"debug:telemetry:{truck_id}:processed"
            rejected_key = f"telemetry:{truck_id}:rejected"

            buffer_count = await r.zcard(buffer_key)
            processed_count = await r.zcard(processed_key)
            rejected_count = await r.zcard(rejected_key)

            buffer_ttl = await r.ttl(buffer_key)
            processed_ttl = await r.ttl(processed_key)

            trucks_data[truck_id] = {
                "buffer_count": buffer_count,
                "processed_count": processed_count,
                "rejected_count": rejected_count,
                "buffer_ttl": buffer_ttl // 60 if buffer_ttl > 0 else 0,
                "processed_ttl": processed_ttl // 60 if processed_ttl > 0 else 0,
            }

        # Print table
        print("TRUCK_ID  │  BUFFER  │ PROCESSED │ REJECTED │  BUFFER_TTL  │ PROC_TTL")
        print("──────────┼──────────┼───────────┼──────────┼──────────────┼──────────")

        for truck_id in sorted(trucks_data.keys()):
            data = trucks_data[truck_id]
            print(
                f"{truck_id:>8}  │ {data['buffer_count']:>8} │ {data['processed_count']:>9} │ {data['rejected_count']:>8} │ {data['buffer_ttl']:>12}m │ {data['processed_ttl']:>6}m"
            )

        print()
        print("💡 To inspect events in a truck's queues, run:")
        print("   python inspect_debug_queues.py {TRUCK_ID}")
        print()

    finally:
        await r.aclose()


async def show_truck_detail(truck_id: str):
    """Show detailed view of a specific truck's queues."""
    r = await redis.from_url("redis://localhost:6379/0", decode_responses=True)

    try:
        print("\n" + "=" * 80)
        print(
            f"╔════════════════════════════════════════════════════════════════════════════╗"
        )
        print(f"║             DEBUG QUEUES FOR TRUCK: {truck_id:<47} ║")
        print(
            f"╚════════════════════════════════════════════════════════════════════════════╝"
        )
        print()

        buffer_key = f"debug:telemetry:{truck_id}:buffer"
        processed_key = f"debug:telemetry:{truck_id}:processed"

        # Buffer queue
        print(f"📥 RAW BUFFER — {buffer_key}")
        print("   (Pre-ingestion raw telemetry packets, 1h TTL)")
        print()

        buffer_events = await r.zrange(buffer_key, 0, -1, withscores=True)

        if not buffer_events:
            print("   [empty]")
        else:
            print(f"   {len(buffer_events)} events:")
            for event_json, score in buffer_events[:5]:  # Show first 5
                try:
                    event = json.loads(event_json)
                    trip_id = event.get("event", {}).get("trip_id", "?")
                    event_type = event.get("event", {}).get("event_type", "?")
                    priority = event.get("event", {}).get("priority", "?")
                    print(
                        f"      • priority={int(score):2d}  {event_type:20s}  trip_id={trip_id}"
                    )
                except Exception as e:
                    print(f"      ⚠️  Parse error: {e}")

            if len(buffer_events) > 5:
                print(f"      ... and {len(buffer_events) - 5} more")

        # Processed queue
        print()
        print(f"✅ PROCESSED — {processed_key}")
        print("   (Post-ingestion clean trip events, 1h TTL)")
        print()

        processed_events = await r.zrange(processed_key, 0, -1, withscores=True)

        if not processed_events:
            print("   [empty]")
        else:
            print(f"   {len(processed_events)} events:")
            for event_json, score in processed_events[:5]:  # Show first 5
                try:
                    event = json.loads(event_json)
                    trip_id = event.get("trip_id", "?")
                    event_type = event.get("event_type", "?")
                    driver_id = event.get("driver_id", "?")
                    print(
                        f"      • priority={int(score):2d}  {event_type:20s}  driver={driver_id}"
                    )
                except Exception as e:
                    print(f"      ⚠️  Parse error: {e}")

            if len(processed_events) > 5:
                print(f"      ... and {len(processed_events) - 5} more")

        print()
        print("=" * 80)

    finally:
        await r.aclose()


async def watch_mode(interval_secs: int = 5):
    """Live monitor mode — refresh every N seconds."""
    while True:
        try:
            await show_all_trucks()
            print(f"\n⏱️  Refreshing in {interval_secs}s... (Ctrl+C to stop)")
            await asyncio.sleep(interval_secs)
        except KeyboardInterrupt:
            print("\n\n👋 Watch mode stopped.")
            break


async def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg == "watch":
            await watch_mode(5)
        elif arg.startswith("tk") or arg.startswith("TK"):
            await show_truck_detail(arg.upper())
        else:
            print(f"Usage: python inspect_debug_queues.py [truck_id|watch]")
            print(f"  truck_id:  Show details for a truck (e.g., TK001)")
            print(f"  watch:     Live refresh mode (5s interval)")
            sys.exit(1)
    else:
        await show_all_trucks()


if __name__ == "__main__":
    asyncio.run(main())
