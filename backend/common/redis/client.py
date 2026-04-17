import json
from datetime import date, datetime
from uuid import UUID

import redis.asyncio as redis

from common.config.settings import get_settings

settings = get_settings()


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder for Redis payloads: datetime, UUID, etc."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class RedisClient:
    """Async Redis client wrapper for TraceData."""

    def __init__(self):
        self._client = redis.from_url(settings.redis_url, decode_responses=True)

    # ── Compatibility Queue Methods (for existing agent runtime) ────────────

    async def push(self, queue_name: str, payload: str):
        """
        Backward-compatible enqueue API used by agent runtime.

        Uses ZSet (same as current pipeline) and derives a score from payload
        priority when present; otherwise uses a neutral default score.
        """
        score = 5
        try:
            data = json.loads(payload)
            if isinstance(data, dict):
                priority = data.get("priority")
                if isinstance(data.get("event"), dict):
                    priority = data["event"].get("priority", priority)

                priority_map = {
                    "critical": 0,
                    "high": 3,
                    "medium": 6,
                    "low": 9,
                }
                if isinstance(priority, str):
                    score = priority_map.get(priority.lower(), score)
        except Exception:
            # Keep default score for non-JSON payloads.
            pass

        await self._client.zadd(queue_name, mapping={payload: score})

    async def pop(self, queue_name: str, timeout: int = 0) -> str | None:
        """
        Backward-compatible dequeue API used by agent runtime.

        Pops from ZSet using ZPOPMIN (non-blocking) to preserve priority ordering.
        Returns member payload string or None if queue is empty.
        """
        result = await self._client.zpopmin(queue_name, count=1)
        if not result:
            return None
        # redis-py ZPOPMIN returns [(member, score), ...]
        return result[0][0]

    # ── Pipeline Queues (ZSets) ──────────────────────────────────────────────

    async def push_to_buffer(
        self, key: str, payload: str, score: int, debug: bool = True
    ):
        """Stage 1 — push raw TelemetryPacket to buffer.

        Args:
            key: Production queue key (e.g., telemetry:TK001:buffer)
            payload: Raw telemetry packet JSON
            score: Priority score for sorting
            debug: If True, also push to debug copy with 1h TTL for observability
        """
        from common.redis.keys import RedisSchema

        # Push to production queue
        await self._client.zadd(key, mapping={payload: score})

        # Mirror to debug queue if enabled
        if debug:
            truck_id = key.split(":")[1]  # Extract truck_id from key
            debug_key = RedisSchema.Telemetry.debug_buffer(truck_id)
            await self._client.zadd(debug_key, mapping={payload: score})
            await self._client.expire(debug_key, RedisSchema.Telemetry.DEBUG_TTL)

    async def pop_from_buffer(self, key: str) -> dict | None:
        """Stage 1 — pop highest priority raw packet from buffer."""
        result = await self._client.zpopmin(key, count=1)
        if not result:
            return None
        raw_json, score = result[0]
        return json.loads(raw_json)

    async def push_to_processed(
        self, key: str, payload: str, score: float | int, debug: bool = True
    ):
        """Stage 2 — push clean TripEvent to processed queue.

        Args:
            key: Production queue key (e.g., telemetry:TK001:processed)
            payload: Clean trip event JSON
            score: ZSET member score (chronological + tie-break; see ``processed_queue_sort_score``)
            debug: If True, also push to debug copy with 1h TTL for observability
        """
        from common.redis.keys import RedisSchema

        # Push to production queue
        await self._client.zadd(key, mapping={payload: score})

        # Mirror to debug queue if enabled
        if debug:
            truck_id = key.split(":")[1]  # Extract truck_id from key
            debug_key = RedisSchema.Telemetry.debug_processed(truck_id)
            await self._client.zadd(debug_key, mapping={payload: score})
            await self._client.expire(debug_key, RedisSchema.Telemetry.DEBUG_TTL)

    async def pop_from_processed(self, key: str) -> dict | None:
        """Stage 2 — pop highest priority clean event from processed queue."""
        result = await self._client.zpopmin(key, count=1)
        if not result:
            return None
        raw_json, score = result[0]
        return json.loads(raw_json)

    async def push_to_rejected(
        self, key: str, payload: str, score: int, ttl: int, debug: bool = True
    ):
        """Push rejected packet to DLQ with TTL.

        Args:
            key: DLQ queue key
            payload: Rejected telemetry packet JSON
            score: Priority score
            ttl: TTL for the DLQ (typically 48 hours)
            debug: If True, also push to visualization buffer
        """
        await self._client.zadd(key, mapping={payload: score})
        await self._client.expire(key, ttl)

        # Also track rejections in visualization buffer
        if debug:
            rejection_event = {
                "type": "rejection",
                "original_key": key,
                "timestamp": datetime.now().__str__(),
                "payload": json.loads(payload) if isinstance(payload, str) else payload,
            }
            await self.push_to_visualization_buffer(
                json.dumps(rejection_event, cls=DateTimeEncoder)
            )

    # ── Debug Queue Inspection (for observability) ───────────────────────────

    async def get_debug_buffer(self, truck_id: str, limit: int = 20) -> list[dict]:
        """Inspect recent raw telemetry packets from debug buffer (1h TTL).

        Returns up to `limit` events from debug:telemetry:{truck_id}:buffer
        sorted by priority (lowest score first).
        """
        from common.redis.keys import RedisSchema

        debug_key = RedisSchema.Telemetry.debug_buffer(truck_id)
        # ZRANGE returns [(member, score), ...] when withscores=True
        raw_events = await self._client.zrange(debug_key, 0, limit - 1, withscores=True)
        return [
            {"payload": json.loads(event), "priority_score": score}
            for event, score in raw_events
        ]

    async def get_debug_processed(self, truck_id: str, limit: int = 20) -> list[dict]:
        """Inspect recent clean trip events from debug queue (1h TTL).

        Returns up to `limit` events from debug:telemetry:{truck_id}:processed
        sorted by priority (lowest score first).
        """
        from common.redis.keys import RedisSchema

        debug_key = RedisSchema.Telemetry.debug_processed(truck_id)
        raw_events = await self._client.zrange(debug_key, 0, limit - 1, withscores=True)
        return [
            {"payload": json.loads(event), "priority_score": score}
            for event, score in raw_events
        ]

    async def get_all_debug_trucks(self) -> dict[str, dict]:
        """Scan all debug queues and return status.

        Returns:
            {
                "TK001": {
                    "buffer_count": 15,
                    "processed_count": 8,
                    "buffer_ttl": 3456,
                    "processed_ttl": 3456
                },
                ...
            }
        """
        buffer_keys = await self._client.keys("debug:telemetry:*:buffer")
        result = {}

        for buffer_key in buffer_keys:
            truck_id = buffer_key.split(":")[
                2
            ]  # Extract from debug:telemetry:TK001:buffer
            processed_key = f"debug:telemetry:{truck_id}:processed"

            buffer_count = await self._client.zcard(buffer_key)
            processed_count = await self._client.zcard(processed_key)
            buffer_ttl = await self._client.ttl(buffer_key)
            processed_ttl = await self._client.ttl(processed_key)

            result[truck_id] = {
                "buffer_count": buffer_count,
                "processed_count": processed_count,
                "buffer_ttl": buffer_ttl,
                "processed_ttl": processed_ttl,
            }

        return result

    # ── Visualization Buffer (60-min TTL for observability) ──────────────────

    async def push_to_visualization_buffer(self, payload: str, ttl: int = 3600):
        """
        Store a recent event in the visualization buffer for inspection.
        Each event is stored as a list entry with automatic 60-minute expiration.
        Non-blocking; ideal for tracking incoming data shape without impacting pipeline.
        """
        viz_key = "td:visualization:recent_events"
        await self._client.lpush(viz_key, payload)
        await self._client.expire(viz_key, ttl)

    async def get_recent_visualization_events(self, limit: int = 50) -> list[dict]:
        """
        Retrieve the most recent events from the visualization buffer.
        Returns up to `limit` events (default 50) in reverse chronological order.
        Useful for dashboards, debugging, or understanding incoming data structure.
        """
        viz_key = "td:visualization:recent_events"
        raw_events = await self._client.lrange(viz_key, 0, limit - 1)
        return [json.loads(event) for event in raw_events]

    # ── Agent Working Cache (Strings/JSON/Lists) ─────────────────────────────

    async def store_trip_context(self, key: str, context: dict, ttl: int):
        """Warmed once by Orchestrator, read by all agents."""
        await self._client.setex(key, ttl, json.dumps(context, cls=DateTimeEncoder))

    async def get_trip_context(self, key: str) -> dict | None:
        """Hydrate agent from shared context."""
        raw = await self._client.get(key)
        return json.loads(raw) if raw else None

    async def push_smoothness_log(self, key: str, log: dict, ttl: int):
        """Accumulate smoothness windows for Scoring Agent."""
        await self._client.lpush(key, json.dumps(log, cls=DateTimeEncoder))
        await self._client.expire(key, ttl)

    async def get_all_smoothness_logs(self, key: str) -> list[dict]:
        """Read full sequence for scoring."""
        raw_logs = await self._client.lrange(key, 0, -1)
        return [json.loads(log) for log in raw_logs]

    async def store_agent_output(self, key: str, output: dict, ttl: int):
        """Store agent result for Orchestrator to consume."""
        await self._client.setex(key, ttl, json.dumps(output, cls=DateTimeEncoder))

    async def get_agent_output(self, key: str) -> dict | None:
        """Read specific agent result."""
        raw = await self._client.get(key)
        return json.loads(raw) if raw else None

    # ── Completion Signalling (Pub/Sub + List) ───────────────────────────────

    async def publish_completion(self, channel: str, event: dict, ttl: int):
        """Dual write: Pub/Sub for immediate, List for durable fallback."""
        event_json = json.dumps(event, cls=DateTimeEncoder)
        await self._client.publish(channel, event_json)
        await self._client.lpush(channel, event_json)
        await self._client.expire(channel, ttl)

    async def subscribe_to_trip(self, channel: str):
        """Get a pubsub object to listen for completions."""
        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    # ── API Response Cache (cache-aside for list endpoints) ─────────────────

    async def cache_get(self, key: str) -> list | dict | None:
        raw = await self._client.get(key)
        return json.loads(raw) if raw else None

    async def cache_set(self, key: str, value: list | dict, ttl: int) -> None:
        await self._client.setex(key, ttl, json.dumps(value, cls=DateTimeEncoder))

    async def cache_delete(self, key: str) -> None:
        await self._client.delete(key)

    # ── Lifecycle ────────────────────────────────────────────────────────────

    async def close(self):
        """Close the Redis connection."""
        await self._client.aclose()
