import json
from datetime import UTC, datetime

from common.models.agent_flow import AgentFlowEvent, AgentFlowSnapshot
from common.redis.client import DateTimeEncoder, RedisClient
from common.redis.keys import RedisSchema


class AgentFlowService:
    """Redis-backed publish + snapshot utilities for Agent Flow UI."""

    def __init__(self, redis_client: RedisClient | None = None):
        self.redis = redis_client or RedisClient()

    async def get_snapshot(self) -> AgentFlowSnapshot:
        raw = await self.redis._client.get(RedisSchema.AgentFlow.STATE_KEY)
        if not raw:
            return AgentFlowSnapshot()
        data = json.loads(raw)
        return AgentFlowSnapshot.model_validate(data)

    async def publish_event(self, event: AgentFlowEvent) -> AgentFlowEvent:
        seq = await self.redis._client.incr(RedisSchema.AgentFlow.SEQ_KEY)
        hydrated = event.model_copy(update={"seq": int(seq), "ts": datetime.now(UTC)})

        snapshot = await self.get_snapshot()
        snapshot.seq = hydrated.seq
        snapshot.updated_at = hydrated.ts
        if hydrated.trip_id:
            snapshot.active_trip_id = hydrated.trip_id

        if hydrated.status in {"queued", "running", "success", "error"}:
            snapshot.execution[hydrated.agent] = hydrated.status
        if hydrated.status in {"healthy", "degraded", "unhealthy"}:
            snapshot.worker_health[hydrated.agent] = hydrated.status

        await self.redis._client.set(
            RedisSchema.AgentFlow.STATE_KEY,
            json.dumps(snapshot.model_dump(mode="json"), cls=DateTimeEncoder),
        )
        payload = json.dumps(hydrated.model_dump(mode="json"), cls=DateTimeEncoder)
        await self.redis._client.publish(RedisSchema.AgentFlow.EVENTS_CHANNEL, payload)
        return hydrated
