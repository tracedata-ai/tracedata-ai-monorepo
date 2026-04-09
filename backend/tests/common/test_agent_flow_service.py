import json
from unittest.mock import patch

import fakeredis.aioredis as fakeredis
import pytest

from common.agent_flow.service import AgentFlowService
from common.models.agent_flow import AgentFlowEvent
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema


@pytest.fixture
async def fake_agent_flow_service():
    server = fakeredis.FakeRedis(decode_responses=True)
    with patch("common.redis.client.redis.from_url", return_value=server):
        redis = RedisClient()
        service = AgentFlowService(redis)
    yield service, server
    await server.aclose()


async def test_publish_event_updates_snapshot_and_channel(fake_agent_flow_service):
    service, server = fake_agent_flow_service
    event = AgentFlowEvent(
        event_type="agent_running",
        status="running",
        agent="safety",
        trip_id="TRIP-123",
    )

    published = await service.publish_event(event)
    assert published.seq > 0

    raw_state = await server.get(RedisSchema.AgentFlow.STATE_KEY)
    assert raw_state is not None
    state = json.loads(raw_state)
    assert state["execution"]["safety"] == "running"
    assert state["active_trip_id"] == "TRIP-123"


async def test_publish_worker_health_updates_health_snapshot(fake_agent_flow_service):
    service, _ = fake_agent_flow_service
    await service.publish_event(
        AgentFlowEvent(
            event_type="worker_health",
            status="degraded",
            agent="scoring",
            meta={"depth": 42},
        )
    )
    snapshot = await service.get_snapshot()
    assert snapshot.worker_health["scoring"] == "degraded"
