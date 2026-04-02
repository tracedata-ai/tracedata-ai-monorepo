"""
CROSS-DOMAIN WRITE SCENARIOS & ORCHESTRATOR COORDINATION

Defines when agents need to write outside their domain and how it's handled.

Pattern:
  Agent A generates result
    → Passes suggestion/request to Orchestrator
  Orchestrator detects cross-domain write
    → Routes to Agent B (owner)
  Agent B processes & writes to its table
    → Returns result
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CrossDomainScenario(Enum):
    """Types of cross-domain write scenarios."""

    SCORING_SUGGESTS_COACHING = "scoring_suggests_coaching"
    SAFETY_REQUESTS_TRIP_UPDATE = "safety_requests_trip_update"
    AGENT_REQUESTS_SHARED_WRITE = "agent_requests_shared_write"


@dataclass
class CrossDomainRequest:
    """Request from agent for cross-domain write."""

    scenario: CrossDomainScenario
    initiating_agent: str
    target_agent: str | None  # None if target is DBManager
    target_table: str
    trip_id: str
    data: dict
    reason: str


# ──────────────────────────────────────────────────────────────────────────────
# SCENARIO 1: Scoring Agent suggests coaching
# ──────────────────────────────────────────────────────────────────────────────

SCENARIO_1_SCORING_SUGGESTS_COACHING = {
    "name": "Scoring Agent suggests coaching",
    "initiating_agent": "scoring",
    "target_agent": "support",
    "target_table": "coaching_schema.coaching",
    "flow": """
    1. ScoringAgent processes end_of_trip event
       - Computes trip score
       - Determines if coaching is needed
       - Writes to scoring_schema.trip_scores ✅ Own table

    2. ScoringAgent can't write to coaching table (not owner)
       - Returns in result: {"suggested_coaching": {...}}

    3. Orchestrator receives ScoringAgent result
       - Detects cross-domain request
       - Creates CrossDomainRequest

    4. Orchestrator -> SupportAgent
       - Passes suggested coaching
       - SupportAgent writes to coaching_schema.coaching ✅ Own table

    5. SupportAgent returns success
    """,
    "code_example": """
    # ScoringAgent._execute()
    score = compute_score(all_pings)
    await self.scoring_repo.write_trip_score(trip_id, score)  # ✅ Own

    if needs_coaching(score):
        return {
            "score": score,
            "suggested_coaching": {  # ← Cross-domain request
                "category": "harsh_brake",
                "message": "Reduce braking force",
                "priority": "high",
            }
        }

    # Orchestrator detects result
    if result.get("suggested_coaching"):
        # Create cross-domain request
        request = CrossDomainRequest(
            scenario=CrossDomainScenario.SCORING_SUGGESTS_COACHING,
            initiating_agent="scoring",
            target_agent="support",
            target_table="coaching_schema.coaching",
            trip_id=trip_id,
            data=result["suggested_coaching"],
            reason="Scoring suggested coaching"
        )
        # Route to SupportAgent
        await orchestrator._handle_cross_domain_write(request)
    """,
}

# ──────────────────────────────────────────────────────────────────────────────
# SCENARIO 2: Safety Agent requests trip update
# ──────────────────────────────────────────────────────────────────────────────

SCENARIO_2_SAFETY_REQUESTS_TRIP_UPDATE = {
    "name": "Safety Agent requests trip update",
    "initiating_agent": "safety",
    "target_agent": None,  # None = DBManager
    "target_table": "public.trips",
    "flow": """
    1. SafetyAgent processes harsh_brake event
       - Analyzes event
       - Determines trip needs intervention
       - Writes to safety_schema.safety_decisions ✅ Own table

    2. SafetyAgent can't write to trips table (not owner)
       - Returns in result: {"requested_action": "escalate"}

    3. Orchestrator receives SafetyAgent result
       - Detects cross-domain request
       - Calls DBManager.update_trip_status()

    4. DBManager writes to public.trips ✅ Shared table owner

    5. Trip status updated
    """,
    "code_example": """
    # SafetyAgent._execute()
    severity = assess_event_severity(event_data)
    await self.safety_repo.write_safety_decision(  # ✅ Own
        event_id=event_id,
        decision="escalate",
        reason="Critical safety incident"
    )

    if severity >= 0.9:  # Critical
        return {
            "decision": "escalate",
            "requested_action": {  # ← Cross-domain request
                "action": "escalate",
                "new_status": "safety_hold",
                "reason": "Critical safety incident"
            }
        }

    # Orchestrator detects result
    if result.get("requested_action"):
        # Route to DBManager
        await orchestrator.db.update_trip(
            trip_id=trip_id,
            status=result["requested_action"]["new_status"]
        )
    """,
}

# ──────────────────────────────────────────────────────────────────────────────
# SCENARIO 3: Any Agent requests write to shared table
# ──────────────────────────────────────────────────────────────────────────────

SCENARIO_3_AGENT_REQUESTS_SHARED_WRITE = {
    "name": "Any Agent requests write to shared table",
    "initiating_agent": "any",
    "target_agent": None,  # None = DBManager
    "target_table": "public.events | public.trips",
    "flow": """
    1. Agent processes event
       - Does its work
       - Can't write to public.* tables (not owner)
       - Returns in result: {"shared_write_request": {...}}

    2. Orchestrator detects request
       - Routes to appropriate DBManager method

    3. DBManager writes to shared table
    """,
    "code_example": """
    # Generic pattern for any agent
    result = {
        "agent_work": "completed",
        "shared_write_request": {  # ← Cross-domain
            "type": "update_events",
            "trip_id": trip_id,
            "updates": {...}
        }
    }

    # Orchestrator routes
    if result.get("shared_write_request"):
        await orchestrator.db.handle_shared_write(
            request=result["shared_write_request"]
        )
    """,
}


# ──────────────────────────────────────────────────────────────────────────────
# ORCHESTRATOR HANDLER
# ──────────────────────────────────────────────────────────────────────────────


class CrossDomainHandler:
    """Orchestrator component that handles cross-domain writes."""

    def __init__(self, db_manager, agents_registry):
        self.db = db_manager
        self.agents = agents_registry

    async def handle_cross_domain_request(
        self,
        request: CrossDomainRequest,
    ) -> Any:
        """
        Route cross-domain write request to appropriate handler.

        Args:
            request: CrossDomainRequest with scenario and data

        Returns:
            Result from handler
        """
        if request.scenario == CrossDomainScenario.SCORING_SUGGESTS_COACHING:
            return await self._handle_scoring_suggests_coaching(request)

        elif request.scenario == CrossDomainScenario.SAFETY_REQUESTS_TRIP_UPDATE:
            return await self._handle_safety_requests_trip_update(request)

        elif request.scenario == CrossDomainScenario.AGENT_REQUESTS_SHARED_WRITE:
            return await self._handle_agent_requests_shared_write(request)

        else:
            raise ValueError(f"Unknown scenario: {request.scenario}")

    async def _handle_scoring_suggests_coaching(
        self,
        request: CrossDomainRequest,
    ) -> dict:
        """Route coaching suggestion from Scoring to Support Agent."""
        support_agent = self.agents.get("support")
        if not support_agent:
            raise RuntimeError("Support Agent not available")

        # Support Agent writes to coaching_schema.coaching
        coaching_id = await support_agent.write_coaching(
            trip_id=request.trip_id,
            driver_id=request.data.get("driver_id"),
            coaching_category=request.data.get("category"),
            message=request.data.get("message"),
            priority=request.data.get("priority", "normal"),
        )

        return {
            "scenario": request.scenario.value,
            "status": "success",
            "coaching_id": coaching_id,
        }

    async def _handle_safety_requests_trip_update(
        self,
        request: CrossDomainRequest,
    ) -> dict:
        """Route trip update request to DBManager."""
        # DBManager writes to public.trips
        await self.db.update_trip(
            trip_id=request.trip_id,
            status=request.data.get("new_status"),
            action_sla=request.data.get("action_sla"),
        )

        return {
            "scenario": request.scenario.value,
            "status": "success",
            "trip_id": request.trip_id,
        }

    async def _handle_agent_requests_shared_write(
        self,
        request: CrossDomainRequest,
    ) -> dict:
        """Route shared table write to DBManager."""
        if request.target_table == "public.trips":
            result = await self.db.update_trip(
                trip_id=request.trip_id,
                **request.data,
            )
        else:
            raise ValueError(f"Unknown shared table: {request.target_table}")

        return {
            "scenario": request.scenario.value,
            "status": "success",
            "result": result,
        }
