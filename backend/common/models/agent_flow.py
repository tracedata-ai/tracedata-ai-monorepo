from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

AgentFlowEventType = Literal[
    "agent_queued",
    "agent_running",
    "agent_done",
    "worker_health",
]
AgentFlowStatus = Literal[
    "idle",
    "queued",
    "running",
    "success",
    "error",
    "healthy",
    "degraded",
    "unhealthy",
]
AgentFlowAgent = Literal[
    "orchestrator",
    "safety",
    "scoring",
    "sentiment",
    "support",
]


class AgentFlowEvent(BaseModel):
    event_type: AgentFlowEventType
    status: AgentFlowStatus
    agent: AgentFlowAgent
    seq: int = 0
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    trip_id: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class AgentFlowSnapshot(BaseModel):
    seq: int = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    execution: dict[str, AgentFlowStatus] = Field(default_factory=dict)
    worker_health: dict[str, AgentFlowStatus] = Field(default_factory=dict)
    active_trip_id: str | None = None
