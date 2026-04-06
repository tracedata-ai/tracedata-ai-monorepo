"""Telemetry simulator endpoints for pushing workflow events from UI."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Literal

import redis.asyncio as redis
from fastapi import APIRouter
from pydantic import BaseModel, Field

from common.config.settings import get_settings
from common.models.events import TelemetryPacket
from common.workflow_fixtures.scoring_harsh_long_trip import build_events

router = APIRouter(prefix="/simulator", tags=["System"])
settings = get_settings()

EventKind = Literal["start", "harsh", "feedback", "smooth", "end"]


class SimulatorEmitRequest(BaseModel):
    kind: EventKind
    trip_id: str = Field(..., min_length=3)
    truck_id: str = Field(..., min_length=2)
    driver_id: str = Field(..., min_length=2)


class SimulatorEmitResponse(BaseModel):
    status: Literal["ok"]
    pushed_count: int
    queue: str
    emitted_kind: EventKind
    trip_id: str
    truck_id: str
    driver_id: str
    event_types: list[str]


def _select_packets(kind: EventKind, packets: list[dict]) -> list[dict]:
    if kind == "start":
        return [
            p
            for p in packets
            if p.get("event", {}).get("event_type") == "start_of_trip"
        ][:1]
    if kind == "smooth":
        return [
            p
            for p in packets
            if p.get("event", {}).get("event_type") == "smoothness_log"
        ][:1]
    if kind == "harsh":
        harsh = [
            p
            for p in packets
            if p.get("event", {}).get("event_type") in {"harsh_brake", "hard_accel"}
        ]
        # Prefer harsh_brake for predictable UI behavior.
        brake = [
            p for p in harsh if p.get("event", {}).get("event_type") == "harsh_brake"
        ]
        return (brake or harsh)[:1]
    if kind == "end":
        return [
            p for p in packets if p.get("event", {}).get("event_type") == "end_of_trip"
        ][:1]
    # feedback
    return [
        p for p in packets if p.get("event", {}).get("event_type") == "driver_feedback"
    ][:1]


@router.post(
    "/emit",
    response_model=SimulatorEmitResponse,
    summary="Emit one workflow event to telemetry buffer",
)
async def emit_simulator_event(payload: SimulatorEmitRequest) -> SimulatorEmitResponse:
    queue = f"telemetry:{payload.truck_id}:buffer"
    all_packets = build_events(
        trip_id=payload.trip_id,
        truck_id=payload.truck_id,
        driver_id=payload.driver_id,
        anchor=datetime.now(UTC).replace(microsecond=0),
    )
    packets = _select_packets(payload.kind, all_packets)
    if not packets:
        packets = [all_packets[0]]

    validated_packets = [
        TelemetryPacket.model_validate(packet).model_dump(mode="json")
        for packet in packets
    ]

    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        now_score = int(datetime.now(UTC).timestamp())
        for i, packet in enumerate(validated_packets):
            await client.zadd(queue, {json.dumps(packet): now_score + i})
    finally:
        await client.aclose()

    return SimulatorEmitResponse(
        status="ok",
        pushed_count=len(validated_packets),
        queue=queue,
        emitted_kind=payload.kind,
        trip_id=payload.trip_id,
        truck_id=payload.truck_id,
        driver_id=payload.driver_id,
        event_types=[
            str(packet.get("event", {}).get("event_type", "unknown"))
            for packet in validated_packets
        ],
    )
