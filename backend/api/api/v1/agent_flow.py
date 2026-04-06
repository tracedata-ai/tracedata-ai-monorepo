import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from common.agent_flow.service import AgentFlowService
from common.models.agent_flow import AgentFlowSnapshot
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

router = APIRouter(prefix="/agent-flow", tags=["System"])


@router.get("/state", response_model=AgentFlowSnapshot, summary="Get Agent Flow snapshot")
async def get_agent_flow_state() -> AgentFlowSnapshot:
    service = AgentFlowService()
    try:
        return await service.get_snapshot()
    finally:
        await service.redis.close()


@router.get("/stream", summary="Stream Agent Flow events (SSE)")
async def stream_agent_flow(request: Request) -> StreamingResponse:
    redis = RedisClient()
    pubsub = redis._client.pubsub()
    await pubsub.subscribe(RedisSchema.AgentFlow.EVENTS_CHANNEL)

    service = AgentFlowService(redis)
    snapshot = await service.get_snapshot()

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Bootstrap state for clients reconnecting mid-run.
            snapshot_payload = json.dumps(snapshot.model_dump(mode="json"))
            yield f"event: snapshot\ndata: {snapshot_payload}\n\n"

            while True:
                if await request.is_disconnected():
                    break

                message = await pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                )
                if message and isinstance(message.get("data"), str):
                    yield f"event: agentflow\ndata: {message['data']}\n\n"
                else:
                    yield ": heartbeat\n\n"
                    await asyncio.sleep(1.0)
        finally:
            await pubsub.unsubscribe(RedisSchema.AgentFlow.EVENTS_CHANNEL)
            await pubsub.aclose()
            await redis.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
