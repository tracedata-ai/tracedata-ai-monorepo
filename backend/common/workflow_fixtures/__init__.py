"""
Named workflow sequences (TelemetryPacket lists) for local / CI pipeline tests.

Load with ``scripts/play_workflow.py --fixture <name>`` or import ``build_events``.
How to reset Redis/DB and run fixtures: ``backend/docs/workflow_testing.md``.
"""

from __future__ import annotations

#: Short CLI name → importable submodule (must expose ``build_events``)
FIXTURE_REGISTRY: dict[str, str] = {
    "minimal_trip": "common.workflow_fixtures.minimal_trip",
    "safety_collision_trip": "common.workflow_fixtures.safety_collision_trip",
    "scoring_harsh_long_trip": "common.workflow_fixtures.scoring_harsh_long_trip",
}


def list_fixtures() -> list[str]:
    return sorted(FIXTURE_REGISTRY.keys())


def resolve_fixture(name: str) -> str:
    key = name.strip()
    if key not in FIXTURE_REGISTRY:
        known = ", ".join(list_fixtures())
        raise ValueError(f"Unknown fixture {key!r}. Choose one of: {known}")
    return FIXTURE_REGISTRY[key]
