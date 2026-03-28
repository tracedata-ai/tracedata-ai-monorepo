import json

import redis.asyncio as redis

from common.config.settings import get_settings

settings = get_settings()


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

    async def push_to_buffer(self, key: str, payload: str, score: int):
        """Stage 1 — push raw TelemetryPacket to buffer."""
        await self._client.zadd(key, mapping={payload: score})

    async def pop_from_buffer(self, key: str) -> dict | None:
        """Stage 1 — pop highest priority raw packet from buffer."""
        result = await self._client.zpopmin(key, count=1)
        if not result:
            return None
        raw_json, score = result[0]
        return json.loads(raw_json)

    async def push_to_processed(self, key: str, payload: str, score: int):
        """Stage 2 — push clean TripEvent to processed queue."""
        await self._client.zadd(key, mapping={payload: score})

    async def pop_from_processed(self, key: str) -> dict | None:
        """Stage 2 — pop highest priority clean event from processed queue."""
        result = await self._client.zpopmin(key, count=1)
        if not result:
            return None
        raw_json, score = result[0]
        return json.loads(raw_json)

    async def push_to_rejected(self, key: str, payload: str, score: int, ttl: int):
        """Push rejected packet to DLQ with TTL."""
        await self._client.zadd(key, mapping={payload: score})
        await self._client.expire(key, ttl)

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
        await self._client.setex(key, ttl, json.dumps(context))

    async def get_trip_context(self, key: str) -> dict | None:
        """Hydrate agent from shared context."""
        raw = await self._client.get(key)
        return json.loads(raw) if raw else None

    async def push_smoothness_log(self, key: str, log: dict, ttl: int):
        """Accumulate smoothness windows for Scoring Agent."""
        await self._client.lpush(key, json.dumps(log))
        await self._client.expire(key, ttl)

    async def get_all_smoothness_logs(self, key: str) -> list[dict]:
        """Read full sequence for scoring."""
        raw_logs = await self._client.lrange(key, 0, -1)
        return [json.loads(log) for log in raw_logs]

    async def store_agent_output(self, key: str, output: dict, ttl: int):
        """Store agent result for Orchestrator to consume."""
        await self._client.setex(key, ttl, json.dumps(output))

    async def get_agent_output(self, key: str) -> dict | None:
        """Read specific agent result."""
        raw = await self._client.get(key)
        return json.loads(raw) if raw else None

    # ── Completion Signalling (Pub/Sub + List) ───────────────────────────────

    async def publish_completion(self, channel: str, event: dict, ttl: int):
        """Dual write: Pub/Sub for immediate, List for durable fallback."""
        event_json = json.dumps(event)
        await self._client.publish(channel, event_json)
        await self._client.lpush(channel, event_json)
        await self._client.expire(channel, ttl)

    async def subscribe_to_trip(self, channel: str):
        """Get a pubsub object to listen for completions."""
        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    # ── Lifecycle ────────────────────────────────────────────────────────────

    async def close(self):
        """Close the Redis connection."""
        await self._client.aclose()
