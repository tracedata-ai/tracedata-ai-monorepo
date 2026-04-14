"""Telemetry simulator endpoints for pushing workflow events from UI."""

from __future__ import annotations

import importlib
import json
from datetime import UTC, datetime
from typing import Literal

import redis.asyncio as redis
from fastapi import APIRouter, BackgroundTasks
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


class SimulatorBatchRequest(BaseModel):
    truck_count: int = Field(default=10, ge=1, le=10)
    event_delay: float = Field(default=2.0, ge=0.1, le=10.0)
    truck_delay: float = Field(default=5.0, ge=1.0, le=30.0)


class SimulatorBatchResponse(BaseModel):
    status: Literal["started"]
    truck_count: int
    event_delay: float
    truck_delay: float
    estimated_duration_seconds: float


async def _run_batch_background(
    truck_count: int, event_delay: float, truck_delay: float
) -> None:
    from scripts.bootstrap_sg_baseline import _push_trip_batch

    fixture_mod = importlib.import_module("common.workflow_fixtures.sg_baseline_trip")
    settings = get_settings()
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await _push_trip_batch(
            client,
            fixture_mod.build_events,
            truck_count=truck_count,
            event_delay=event_delay,
            truck_delay=truck_delay,
        )
    finally:
        await client.aclose()


@router.post(
    "/run-batch",
    response_model=SimulatorBatchResponse,
    summary="Run a full trip cycle for N trucks in the background",
)
async def run_simulator_batch(
    payload: SimulatorBatchRequest, background_tasks: BackgroundTasks
) -> SimulatorBatchResponse:
    avg_events_per_truck = 20
    estimated = (
        payload.truck_count * avg_events_per_truck * payload.event_delay
        + (payload.truck_count - 1) * payload.truck_delay
    )
    background_tasks.add_task(
        _run_batch_background,
        payload.truck_count,
        payload.event_delay,
        payload.truck_delay,
    )
    return SimulatorBatchResponse(
        status="started",
        truck_count=payload.truck_count,
        event_delay=payload.event_delay,
        truck_delay=payload.truck_delay,
        estimated_duration_seconds=round(estimated, 1),
    )


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
