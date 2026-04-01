"""
Orchestrator Agent — LLM-based routing with DB Manager and Celery.

Reads clean TripEvents from the processed queue, acquires DB lease, uses LLM
reasoning to route agents, warms Redis for those agents, then dispatches via
Celery to specialized workers (Safety, Scoring, Sentiment, Support).

Event routing is driven by LLM + EventMatrix for consistency.
Internal components:
  - LLM Agent: uses get_event_config tool to look up EventMatrix
  - DB Manager: acquire_lock, release_lock, create_trip, update_trip
  - Celery dispatch: sends IntentCapsule to agent-specific queues
  - IntentCapsule: security token with scoped Redis R/W access
  - Cache Warming: event-driven vs aggregation-driven strategies

Location: backend/agents/orchestrator/agent.py
"""

import asyncio
import json
import logging
from datetime import UTC, datetime

from celery import Celery
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from agents.base.agent import Agent
from agents.orchestrator.db_manager import DBManager
from agents.orchestrator.tools import ORCHESTRATOR_TOOLS
from common.config.events import (
    PRIORITY_MAP,
    get_warming_type,
)
from common.config.settings import get_settings
from common.db.engine import engine
from common.models.events import TripEvent
from common.models.security import IntentCapsule, ScopedToken
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_celery() -> Celery:
    """Import Celery app lazily to avoid circular imports."""
    from celery_app import app

    return app


def _get_llm():
    """Get LLM instance based on configuration."""
    if settings.openai_api_key:
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=0.1,  # Deterministic routing
        )
    elif settings.anthropic_api_key:
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=settings.anthropic_api_key,
            temperature=0.1,  # Deterministic routing
        )
    else:
        raise ValueError(
            "No LLM API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY"
        )


# ── System Prompt for Orchestrator ────────────────────────────────────────────
ORCHESTRATOR_SYSTEM_PROMPT = """
You are the TraceData OrchestratorAgent. Your job is to make routing decisions 
for events flowing through the multi-agent system.

ARCHITECTURE:
- EventMatrix is the SINGLE SOURCE OF TRUTH for event behavior
- You validate decisions using LLM reasoning
- You use the tools to look up event configuration

YOUR WORKFLOW:
═════════════════════════════════════════════════════════════════════════════

1. LOOKUP EVENT IN EVENTMATRIX
   
   Use tool: get_event_config(trigger_event_type)
   
   This returns:
   - event_type: The event name
   - category: Event category (critical, harsh_events, trip_lifecycle, etc.)
   - priority: Event priority (CRITICAL, HIGH, MEDIUM, LOW)
   - priority_score: Redis ZSet score (0=CRITICAL, 3=HIGH, 6=MEDIUM, 9=LOW)
   - ml_weight: Machine learning weighting factor
   - action: What should happen (source of truth!)
   - agents_from_action: List of agents that should run

2. INTERPRET THE ACTION FIELD (This is the key!)
   
   The 'action' field tells you which agents should run:
   
   - "Emergency Alert & 911" → dispatch ["safety"]
   - "Emergency Alert" → dispatch ["safety"]
   - "Fleet Alert" → dispatch ["safety"]
   - "Coaching" → dispatch ["scoring", "support"]
   - "Regulatory" → dispatch ["scoring"]
   - "Scoring" → dispatch ["scoring"]
   - "Sentiment" → dispatch ["sentiment"]
   - "Support" → dispatch ["support"]
   - "HITL" → dispatch ["human_in_the_loop"]
   - "Analytics" → dispatch []
   - "Logging" → dispatch []
   - "Reward Bonus" → dispatch []
   - "Reject & Log" → dispatch []

3. RETURN YOUR DECISION (JSON ONLY)
   
   Return ONLY valid JSON, no extra text:
   
   {
     "trip_id": "TRIP-...",
     "event_type": "harsh_brake",
     "priority_score": 3,
     "agents_to_dispatch": ["scoring", "support"],
     "action": "Coaching",
     "reasoning": "EventMatrix lookup returned action='Coaching'. 
                   Maps to [scoring, support] agents per standard mapping."
   }

KEY PRINCIPLES:
═════════════════════════════════════════════════════════════════════════════

✓ EventMatrix is SINGLE SOURCE OF TRUTH
  - Always look it up using get_event_config tool
  - Don't guess or hallucinate agent names

✓ Deterministic routing
  - Same event type → same actions (unless edge cases detected)
  - Use tool first, then decide

✓ Return JSON only
  - Valid JSON with required fields
  - No markdown, no extra text

✓ Empty dispatch list is valid
  - Some events (like "smoothness_log") don't need agents
  - Just return empty agents_to_dispatch list

EXAMPLE:
═════════════════════════════════════════════════════════════════════════════

Trip receives event: "harsh_brake"

1. Call get_event_config("harsh_brake")
   → Returns: action="Coaching", priority="HIGH", priority_score=3

2. Map action "Coaching" → agents ["scoring", "support"]

3. Return:
   {
     "trip_id": "TRIP-abc123...",
     "event_type": "harsh_brake",
     "priority_score": 3,
     "agents_to_dispatch": ["scoring", "support"],
     "action": "Coaching",
     "reasoning": "EventMatrix action 'Coaching' maps to [scoring, support] agents."
   }

Let's route this event!
"""


class OrchestratorAgent:
    """
    LLM-based event router with Celery dispatch.

    Uses LLM reasoning + EventMatrix to decide which agents handle each event.
    Polls all configured truck IDs in round-robin.
    """

    AGENT_NAME = "orchestrator"

    def __init__(
        self,
        truck_ids: list[str] | None = None,
    ) -> None:
        """
        Initialize OrchestratorAgent with LLM and DB components.

        Args:
            truck_ids: List of truck IDs to monitor for events.
        """
        self.truck_ids = truck_ids or []
        self.redis = RedisClient()
        self.db = DBManager()
        self._running = False

        # Initialize LLM agent for routing decisions
        llm = _get_llm()
        self.llm_agent = Agent(
            llm=llm,
            agent_name="OrchestratorRouter",
            tools=ORCHESTRATOR_TOOLS,
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        )
        logger.info("OrchestratorAgent initialized with LLM routing")

    # ── Main loop ─────────────────────────────────────────────────────────────

    async def _discover_trucks(self) -> list[str]:
        """
        Discover truck IDs from active processed queues in Redis.
        Returns list of truck_ids that have events waiting.

        Pattern: telemetry:{truck_id}:processed (sorted set)
        """
        pattern = "telemetry:*:processed"
        keys = await self.redis._client.keys(pattern)

        # Extract truck_id from "telemetry:{truck_id}:processed"
        truck_ids = [key.split(":")[1] for key in keys if ":" in key]

        if truck_ids:
            logger.info(
                {
                    "action": "trucks_discovered",
                    "count": len(truck_ids),
                    "truck_ids": truck_ids,
                }
            )
        else:
            logger.debug(
                "No trucks with processed queues found (waiting for ingestion to populate)."
            )

        return sorted(set(truck_ids))  # Deduplicate and sort for consistency

    async def run(self) -> None:
        """Poll all discovered truck processed queues in round-robin."""
        self._running = True
        logger.info(
            {
                "action": "orchestrator_started",
                "mode": "dynamic_truck_discovery",
            }
        )

        try:
            while self._running:
                # Dynamically discover trucks from processed queues
                truck_ids = await self._discover_trucks()

                if not truck_ids:
                    # Ingestion hasn't populated processed queues yet
                    logger.debug("No trucks found, sleeping 1s before retry...")
                    await asyncio.sleep(1.0)
                    continue

                handled = 0
                for truck_id in truck_ids:
                    key = RedisSchema.Telemetry.processed(truck_id)
                    result = await self.redis.pop_from_processed(key)
                    if result is None:
                        continue
                    handled += 1
                    await self._handle_event(result, truck_id)

                if handled == 0:
                    await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info({"action": "orchestrator_stopping"})
        finally:
            await self.redis.close()

    # ── Event handling ────────────────────────────────────────────────────────

    async def _handle_event(self, event_data: dict, truck_id: str) -> None:
        """
        Full orchestration sequence for one TripEvent:
          1. Parse TripEvent
          2. Handle trip lifecycle (create trip, update status)
          3. Acquire DB lease → LLM routing → warm Redis for routed agents
          4. Seal IntentCapsule (includes device_event_id for lock release)
          5. Dispatch via Celery
          6. Listen for CompletionEvent (non-blocking check)
        """
        try:
            event = TripEvent(**event_data)
        except Exception as e:
            logger.error(
                {
                    "action": "event_parse_failed",
                    "error": str(e)[:200],
                }
            )
            return

        ctx = {
            "trip_id": event.trip_id,
            "event_id": event.event_id,
            "event_type": event.event_type,
            "truck_id": truck_id,
        }
        logger.info({**ctx, "action": "event_received"})

        # ── Step 1: Trip lifecycle ─────────────────────────────────────────
        await self._handle_trip_lifecycle(event, ctx)

        # ── Step 2: Acquire lease → routing → warm cache for routed agents → dispatch
        await self._acquire_and_dispatch(event, ctx)

    async def _handle_trip_lifecycle(self, event: TripEvent, ctx: dict) -> None:
        """Create trip row on start_of_trip. Update status on end_of_trip."""
        if event.event_type == "start_of_trip":
            await self.db.create_trip(
                trip_id=event.trip_id,
                driver_id=event.driver_id,
                truck_id=event.truck_id,
                started_at=event.timestamp,
            )
            logger.info({**ctx, "action": "trip_created"})

        elif event.event_type == "end_of_trip":
            await self.db.update_trip(
                trip_id=event.trip_id,
                status="scoring_pending",
                action_sla="1_week",
            )

    async def _warm_cache(
        self,
        event: TripEvent,
        agents_to_dispatch: list[str],
    ) -> None:
        """
        Main cache warming dispatcher.

        Warms Redis only for agents chosen by routing (aligned with capsules).
        Strategy still comes from EventMatrix via get_warming_type(event_type).

        Called after acquire_lock and routing, before sealing capsules.
        """
        trip_id = event.trip_id
        event_type = event.event_type

        if not agents_to_dispatch:
            return

        warming_type = get_warming_type(event_type)

        if warming_type == "event-driven":
            await self._warm_event_driven(event, agents_to_dispatch)

        elif warming_type == "aggregation-driven":
            await self._warm_aggregation_driven(event, agents_to_dispatch)

        else:
            logger.info(
                {
                    "action": "cache_warming_skipped",
                    "trip_id": trip_id,
                    "event_type": event_type,
                    "reason": "no_warming_needed",
                }
            )

    async def _warm_event_driven(
        self,
        event: TripEvent,
        agents_to_dispatch: list[str],
    ) -> None:
        """
        Event-driven warming: minimal data for Safety/Support agents.

        Fetches:
          - Current event (1-2 KB)
          - Trip metadata (1-2 KB)

        Load time: 1-2 milliseconds
        Used by: Safety, Support agents on single-event analysis
        """
        trip_id = event.trip_id
        event_type = event.event_type

        try:
            if not agents_to_dispatch:
                return

            # Fetch current event data
            current_event = await self._get_event_data(event)
            if not current_event:
                logger.warning(
                    {
                        "action": "event_data_fetch_failed",
                        "trip_id": trip_id,
                        "event_id": event.event_id,
                    }
                )
                return

            # Fetch trip metadata
            trip_metadata = await self._get_trip_metadata(trip_id)
            if not trip_metadata:
                logger.warning(
                    {
                        "action": "trip_metadata_fetch_failed",
                        "trip_id": trip_id,
                    }
                )
                return

            # Store pre-warmed data for each routed agent (scoped keys)
            for agent in agents_to_dispatch:
                # Store current event
                event_key = RedisSchema.Trip.agent_data(trip_id, agent, "current_event")
                await self.redis._client.setex(
                    event_key,
                    300,  # 5 minute TTL
                    json.dumps(current_event),
                )

                # Store trip context
                context_key = RedisSchema.Trip.agent_data(
                    trip_id, agent, "trip_context"
                )
                await self.redis._client.setex(
                    context_key,
                    300,  # 5 minute TTL
                    json.dumps(trip_metadata),
                )

            logger.info(
                {
                    "action": "cache_warmed_event_driven",
                    "trip_id": trip_id,
                    "event_type": event_type,
                    "agents": agents_to_dispatch,
                    "data_size_bytes": len(json.dumps(current_event))
                    + len(json.dumps(trip_metadata)),
                    "load_time_ms": 1,
                }
            )

        except Exception as e:
            logger.error(
                {
                    "action": "event_driven_warming_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )

    async def _warm_aggregation_driven(
        self,
        event: TripEvent,
        agents_to_dispatch: list[str],
    ) -> None:
        """
        Aggregation-driven warming: heavy data for Scoring agent.

        Fetches:
          - ALL pings from entire trip (10+ data points)
          - Rolling average score (for context)
          - Coaching history (for support agent)

        Load time: 1-2 seconds (expensive but necessary for end_of_trip!)
        Used by: Scoring, Support agents on trip completion
        """
        trip_id = event.trip_id
        event_type = event.event_type

        try:
            agents_set = set(agents_to_dispatch)
            need_scoring = "scoring" in agents_set
            need_support = "support" in agents_set

            if not need_scoring and not need_support:
                logger.info(
                    {
                        "action": "aggregation_warming_no_scoring_support",
                        "trip_id": trip_id,
                        "agents": agents_to_dispatch,
                    }
                )
                return

            all_pings: list[dict] = []
            if need_scoring:
                all_pings = await self._get_all_pings_for_trip(trip_id)
                if not all_pings:
                    logger.warning(
                        {
                            "action": "no_pings_found",
                            "trip_id": trip_id,
                        }
                    )
                    if not need_support:
                        return

            trip_metadata = await self._get_trip_metadata(trip_id)
            if not trip_metadata:
                logger.warning(
                    {
                        "action": "trip_metadata_fetch_failed",
                        "trip_id": trip_id,
                    }
                )
                return

            driver_id = trip_metadata.get("driver_id")
            rolling_avg = None
            coaching_history: list[dict] = []

            if driver_id and need_scoring:
                rolling_avg = await self._get_rolling_average_score(driver_id, n=3)
            if driver_id and need_support:
                coaching_history = await self._get_coaching_history(trip_id)

            if need_scoring and all_pings:
                agent = "scoring"
                pings_key = RedisSchema.Trip.agent_data(trip_id, agent, "all_pings")
                await self.redis._client.setex(
                    pings_key,
                    3600,
                    json.dumps(all_pings),
                )
                avg_key = RedisSchema.Trip.agent_data(trip_id, agent, "historical_avg")
                await self.redis._client.setex(
                    avg_key,
                    3600,
                    json.dumps({"rolling_avg_score": rolling_avg}),
                )

            if need_support:
                agent = "support"
                context_key = RedisSchema.Trip.agent_data(
                    trip_id, agent, "trip_context"
                )
                await self.redis._client.setex(
                    context_key,
                    3600,
                    json.dumps(trip_metadata),
                )
                history_key = RedisSchema.Trip.agent_data(
                    trip_id, agent, "coaching_history"
                )
                await self.redis._client.setex(
                    history_key,
                    3600,
                    json.dumps(coaching_history),
                )

            pings_count = len(all_pings)

            logger.info(
                {
                    "action": "cache_warmed_aggregation_driven",
                    "trip_id": trip_id,
                    "event_type": event_type,
                    "agents": agents_to_dispatch,
                    "ping_count": pings_count,
                    "data_size_kb": len(json.dumps(all_pings)) / 1024,
                    "load_time_ms": 1500,
                }
            )

        except Exception as e:
            logger.error(
                {
                    "action": "aggregation_driven_warming_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )

    # ── Cache Warming Helper Methods ────────────────────────────────────────

    async def _get_event_data(self, event: TripEvent) -> dict | None:
        """Fetch event data from database."""
        try:
            # Access the EventsRepository through DBManager
            from common.db.repositories.events_repo import EventsRepo

            events_repo = EventsRepo(engine)
            event_data = await events_repo.get_event_by_id(event.event_id)
            return event_data
        except Exception as e:
            logger.error(
                {
                    "action": "get_event_data_error",
                    "event_id": event.event_id,
                    "error": str(e),
                }
            )
            return None

    async def _get_trip_metadata(self, trip_id: str) -> dict | None:
        """Fetch trip metadata from database."""
        try:
            from common.db.repositories.events_repo import EventsRepo

            events_repo = EventsRepo(engine)
            metadata = await events_repo.get_trip_metadata(trip_id)
            return metadata
        except Exception as e:
            logger.error(
                {
                    "action": "get_trip_metadata_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            return None

    async def _get_all_pings_for_trip(self, trip_id: str) -> list[dict]:
        """Fetch all pings/events for a trip (EXPENSIVE!)."""
        try:
            from common.db.repositories.events_repo import EventsRepo

            events_repo = EventsRepo(engine)
            pings = await events_repo.get_all_pings_for_trip(trip_id)
            return pings
        except Exception as e:
            logger.error(
                {
                    "action": "get_all_pings_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            return []

    async def _get_rolling_average_score(
        self,
        driver_id: str,
        n: int = 3,
    ) -> float | None:
        """Fetch driver's rolling average score."""
        try:
            from common.db.repositories.events_repo import EventsRepo

            events_repo = EventsRepo(engine)
            avg = await events_repo.get_rolling_average_score(driver_id, n)
            return avg
        except Exception as e:
            logger.error(
                {
                    "action": "get_rolling_average_error",
                    "driver_id": driver_id,
                    "error": str(e),
                }
            )
            return None

    async def _get_coaching_history(
        self,
        trip_id: str,
        limit: int = 5,
    ) -> list[dict]:
        """Fetch coaching history for a trip."""
        try:
            from common.db.repositories.events_repo import EventsRepo

            events_repo = EventsRepo(engine)
            history = await events_repo.get_coaching_history(trip_id, limit)
            return history
        except Exception as e:
            logger.error(
                {
                    "action": "get_coaching_history_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            return []

    async def _acquire_and_dispatch(self, event: TripEvent, ctx: dict) -> None:
        """
        Acquire DB lease then dispatch to Celery.
        Order matters: lock BEFORE dispatch.
        Uses LLM to determine which agents should handle the event.
        """
        device_event_id = event.device_event_id

        # ── Acquire lease ──────────────────────────────────────────────────
        acquired = await self.db.acquire_lock(device_event_id)
        if not acquired:
            logger.warning({**ctx, "action": "lock_failed", "reason": "already_locked"})
            return

        # ── Get routing decision from LLM ──────────────────────────────────
        routing_decision = self._get_routing_decision(event)
        agents_to_dispatch = routing_decision.get("agents_to_dispatch", [])

        if not agents_to_dispatch:
            # No agents to dispatch — release lock and return
            logger.info(
                {
                    **ctx,
                    "action": "dispatch_skipped_no_agents",
                    "reason": routing_decision.get("action", "unknown"),
                }
            )
            await self.db.release_lock(device_event_id)
            return

        await self._warm_cache(event, agents_to_dispatch)

        # ── Seal IntentCapsules for each agent ─────────────────────────────
        # Create a capsule for each agent that will handle the event
        capsules = {}
        for agent_name in agents_to_dispatch:
            capsule = self._seal_capsule(event, agent_name)
            capsules[agent_name] = capsule

        # ── Route to agent queue via Celery ───────────────────────────────
        dispatched = await self._dispatch(event, capsules, ctx, routing_decision)

        if not dispatched:
            # Release lock if dispatch failed — event will be retried
            await self.db.fail_event(device_event_id)

    def _seal_capsule(self, event: TripEvent, agent_name: str) -> IntentCapsule:
        """
        Build and seal an IntentCapsule for this event.

        Encapsulates the trip context, permissions, and security token.
        Uses scoped keys that match pre-warmed data from cache warming stage.

        HMAC signing deferred to Phase 6 (see security.capsule module).
        """
        trip_id = event.trip_id
        event_type = event.event_type

        # Determine which keys this agent should have access to
        # based on the cache warming strategy
        warming_type = get_warming_type(event_type)
        read_keys = []

        if warming_type == "event-driven":
            # Event-driven agents get: current_event + trip_context (scoped)
            read_keys = [
                RedisSchema.Trip.agent_data(trip_id, agent_name, "current_event"),
                RedisSchema.Trip.agent_data(trip_id, agent_name, "trip_context"),
            ]

        elif warming_type == "aggregation-driven":
            # Aggregation-driven agents get specific keys based on agent type
            if agent_name == "scoring":
                read_keys = [
                    RedisSchema.Trip.agent_data(trip_id, agent_name, "all_pings"),
                    RedisSchema.Trip.agent_data(trip_id, agent_name, "historical_avg"),
                ]
            elif agent_name == "support":
                read_keys = [
                    RedisSchema.Trip.agent_data(trip_id, agent_name, "trip_context"),
                    RedisSchema.Trip.agent_data(
                        trip_id, agent_name, "coaching_history"
                    ),
                ]
            else:
                # Fallback for unknown agents
                read_keys = [
                    RedisSchema.Trip.context(trip_id),
                    RedisSchema.Trip.smoothness_logs(trip_id),
                ]
        else:
            # No warming needed — provide generic trip context
            read_keys = [
                RedisSchema.Trip.context(trip_id),
                RedisSchema.Trip.smoothness_logs(trip_id),
            ]

        # Write keys are always agent-specific
        write_keys = [
            RedisSchema.Trip.output(trip_id, agent_name),
            RedisSchema.Trip.events_channel(trip_id),
        ]

        # Create scoped token with warming-aware keys
        token = ScopedToken(
            agent=agent_name,
            trip_id=trip_id,
            expires_at=datetime.now(UTC).replace(second=0, microsecond=0),
            read_keys=read_keys,
            write_keys=write_keys,
        )

        # Create capsule with priority-based TTL
        priority_value = (
            event.priority
            if isinstance(event.priority, int)
            else PRIORITY_MAP.get(event.priority, 9)
        )

        # Higher priority = longer TTL (critical events need more time)
        if priority_value <= 0:  # CRITICAL
            ttl_seconds = 3600  # 1 hour
        elif priority_value <= 3:  # HIGH
            ttl_seconds = 1800  # 30 minutes
        else:  # MEDIUM/LOW
            ttl_seconds = 600  # 10 minutes

        capsule = IntentCapsule(
            trip_id=trip_id,
            agent=agent_name,
            device_event_id=event.device_event_id,
            priority=priority_value,
            tool_whitelist=["redis_read", "redis_write"],
            step_to_tools={"1": ["redis_read"], "2": ["redis_write"]},
            ttl_seconds=ttl_seconds,
            token=token,
        )

        logger.info(
            {
                "action": "capsule_sealed",
                "trip_id": trip_id,
                "agent": agent_name,
                "warming_type": warming_type,
                "read_keys_count": len(read_keys),
                "ttl_seconds": ttl_seconds,
            }
        )
        return capsule

    def _get_routing_decision(self, event: TripEvent) -> dict:
        """
        Use LLM agent to get routing decision for an event.

        Returns:
            dict with keys: agents_to_dispatch, priority_score, action, reasoning
        """
        user_prompt = f"""
You are routing an event from a vehicle telematics system.

Event Details:
- Trip ID: {event.trip_id}
- Event Type: {event.event_type}
- Driver ID: {event.driver_id}
- Truck ID: {event.truck_id}
- Priority: {event.priority}
- Timestamp: {event.timestamp}

Your task:
1. Use get_event_config tool to look up this event type in EventMatrix
2. Interpret the action field and determine which agents should run
3. Return your routing decision as valid JSON

Return ONLY the JSON object, no additional text."""

        input_data = {
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ]
        }

        try:
            result = self.llm_agent.invoke(input_data)

            # Extract the routing decision from LLM output
            if isinstance(result, dict) and "messages" in result:
                # Get the last message (should be assistant response)
                messages = result["messages"]
                if messages:
                    last_msg = messages[-1]
                    # Extract content from LangChain Message objects
                    if hasattr(last_msg, "content"):
                        content = last_msg.content
                    elif isinstance(last_msg, dict):
                        content = last_msg.get("content", "")
                    else:
                        content = str(last_msg)

                    # Parse JSON from response
                    try:
                        decision = json.loads(content)
                        # Validate required fields
                        if "agents_to_dispatch" in decision:
                            logger.info(
                                {
                                    "log_action": "routing_decision",
                                    "event_type": event.event_type,
                                    "agents": decision.get("agents_to_dispatch", []),
                                    "action": decision.get("action", "unknown"),
                                }
                            )
                            return decision
                    except json.JSONDecodeError as e:
                        logger.warning(
                            {
                                "action": "routing_json_parse_failed",
                                "event_type": event.event_type,
                                "error": str(e),
                                "content": content[:200],
                            }
                        )

            logger.error(
                {
                    "action": "routing_decision_failed",
                    "event_type": event.event_type,
                    "result": str(result)[:200],
                }
            )
            # Return empty dispatch as fallback (won't route event)
            return {
                "agents_to_dispatch": [],
                "action": "ERROR",
                "reasoning": "LLM routing failed",
            }

        except Exception as e:
            logger.error(
                {
                    "action": "routing_invocation_failed",
                    "event_type": event.event_type,
                    "error": str(e),
                }
            )
            return {
                "agents_to_dispatch": [],
                "action": "ERROR",
                "reasoning": "Exception during routing",
            }

    async def _dispatch(
        self,
        event: TripEvent,
        capsules: dict,
        ctx: dict,
        routing_decision: dict,
    ) -> bool:
        """
        Dispatch to multiple agents via Celery based on routing decision.
        Returns True if at least one agent was dispatched, False otherwise.
        """
        agents_to_dispatch = routing_decision.get("agents_to_dispatch", [])
        action = routing_decision.get("action", "unknown")

        if not agents_to_dispatch:
            logger.info(
                {
                    **ctx,
                    "action": "dispatch_skipped",
                    "reason": "no_agents_from_routing",
                    "llm_action": action,
                }
            )
            # Not an error — some events (like "smoothness_log") don't need agents
            await self.db.release_lock(event.device_event_id)
            return False

        celery = _get_celery()

        # Dispatch to each agent in the routing decision
        dispatched = False
        for agent_name in agents_to_dispatch:
            capsule = capsules.get(agent_name)
            if not capsule:
                logger.warning(
                    {
                        **ctx,
                        "action": "capsule_missing",
                        "agent": agent_name,
                    }
                )
                continue

            priority_score = (
                event.priority
                if isinstance(event.priority, int)
                else PRIORITY_MAP.get(event.priority, 9)
            )

            # Map agent name to queue and task
            if agent_name == "safety":
                target_queue = settings.safety_queue
                task_name = "tasks.safety_tasks.analyse_event"
            elif agent_name == "scoring":
                target_queue = settings.scoring_queue
                task_name = "tasks.scoring_tasks.score_trip"
            elif agent_name == "support":
                target_queue = settings.support_queue
                task_name = "tasks.support_tasks.generate_coaching"
            elif agent_name == "sentiment":
                target_queue = settings.sentiment_queue
                task_name = "tasks.sentiment_tasks.analyse_feedback"
            else:
                logger.warning(
                    {
                        **ctx,
                        "action": "unknown_agent",
                        "agent": agent_name,
                    }
                )
                continue

            logger.info(
                {
                    **ctx,
                    "action": "dispatch",
                    "target": agent_name,
                    "llm_action": action,
                }
            )
            celery.send_task(
                task_name,
                kwargs={"intent_capsule": capsule.model_dump()},
                queue=target_queue,
                priority=priority_score,
            )
            dispatched = True

        return dispatched

    @staticmethod
    def _agent_for_event(event_type: str) -> str:
        """
        DEPRECATED: Use LLM-based routing instead.
        This is kept for compatibility only.
        """
        logger.warning(
            {
                "action": "deprecated_agent_for_event",
                "event_type": event_type,
                "note": "Use LLM-based routing instead",
            }
        )
        # Fallback: return "orchestrator" (no dispatch)
        return "orchestrator"
