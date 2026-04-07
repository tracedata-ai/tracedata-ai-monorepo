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
from inspect import isawaitable

from celery import Celery
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from agents.base.agent import Agent
from agents.orchestrator.db_manager import DBManager
from agents.orchestrator.prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT,
    build_orchestrator_routing_user_message,
)
from agents.orchestrator.tools import ORCHESTRATOR_TOOLS
from common.agent_flow.service import AgentFlowService
from common.config.events import (
    EVENT_MATRIX,
    PRIORITY_MAP,
    compute_routing_agents,
    get_warming_type,
)
from common.config.settings import get_settings
from common.db.engine import engine
from common.models.agent_flow import AgentFlowEvent
from common.models.events import TripEvent
from common.models.security import IntentCapsule, ScopedToken
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)
settings = get_settings()

FLAGGED_EVENT_TYPES = {"harsh_brake", "hard_accel", "harsh_corner", "speeding"}
CRITICAL_IMMEDIATE_SUPPORT_TYPES = {"collision", "rollover", "driver_sos"}


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
            "device_event_id": event.device_event_id,
            "event_type": event.event_type,
            "truck_id": truck_id,
        }
        logger.info({**ctx, "action": "event_received"})
        await AgentFlowService(self.redis).publish_event(
            AgentFlowEvent(
                event_type="agent_running",
                status="running",
                agent="orchestrator",
                trip_id=event.trip_id,
                meta={"event_type": event.event_type},
            )
        )

        # ── Step 1: Trip lifecycle ─────────────────────────────────────────
        await self._handle_trip_lifecycle(event, ctx)

        # ── Step 2: Acquire lease → routing → warm cache for routed agents → dispatch
        await self._acquire_and_dispatch(event, ctx)
        await AgentFlowService(self.redis).publish_event(
            AgentFlowEvent(
                event_type="agent_done",
                status="success",
                agent="orchestrator",
                trip_id=event.trip_id,
                meta={"event_type": event.event_type},
            )
        )

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
            logger.info({**ctx, "action": "trip_marked_scoring_pending"})

        elif event.event_type == "coaching_ready":
            await self.db.update_trip(
                trip_id=event.trip_id,
                status="coaching_pending",
            )
            logger.info({**ctx, "action": "trip_marked_coaching_pending"})

    async def _load_trip_runtime_context(self, trip_id: str) -> dict:
        key = RedisSchema.Trip.context(trip_id)
        raw_context = self.redis.get_trip_context(key)
        context = await raw_context if isawaitable(raw_context) else raw_context
        if isinstance(context, dict):
            return context
        return {}

    async def _save_trip_runtime_context(self, trip_id: str, context: dict) -> None:
        key = RedisSchema.Trip.context(trip_id)
        await self.redis.store_trip_context(
            key, context, ttl=RedisSchema.Trip.CONTEXT_TTL_HIGH
        )

    async def _append_flagged_event(self, event: TripEvent) -> None:
        context = await self._load_trip_runtime_context(event.trip_id)
        flagged_events = context.get("flagged_events", [])
        if not isinstance(flagged_events, list):
            flagged_events = []

        entry: dict = {
            "event_id": event.event_id,
            "device_event_id": event.device_event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "priority": str(event.priority),
        }
        try:
            from common.db.repositories.events_repo import EventsRepo

            full = await EventsRepo(engine).get_event_by_id(event.event_id)
            if full:
                loc = full.get("location")
                if loc is not None:
                    entry["location"] = loc
                ev = full.get("evidence")
                if ev:
                    entry["evidence"] = ev
        except Exception as e:
            logger.warning(
                {
                    "action": "flagged_event_enrichment_skipped",
                    "trip_id": event.trip_id,
                    "event_id": event.event_id,
                    "error": str(e),
                }
            )

        flagged_events.append(entry)
        context["flagged_events"] = flagged_events
        context.setdefault("trip_id", event.trip_id)
        context.setdefault("driver_id", event.driver_id)
        context.setdefault("truck_id", event.truck_id)
        await self._save_trip_runtime_context(event.trip_id, context)

        logger.info(
            {
                "action": "event_flagged_for_eot_coaching",
                "trip_id": event.trip_id,
                "event_id": event.event_id,
                "device_event_id": event.device_event_id,
                "event_type": event.event_type,
                "flagged_count": len(flagged_events),
            }
        )

    @staticmethod
    def _estimate_trip_score(all_pings: list[dict]) -> float:
        if not all_pings:
            return 100.0
        harsh_count = sum(
            1
            for ping in all_pings
            if str(ping.get("event_type", "")).lower()
            in {"harsh_brake", "hard_accel", "harsh_corner", "speeding"}
        )
        return float(max(0, 100 - (harsh_count * 10)))

    async def _should_dispatch_coaching(self, event: TripEvent) -> bool:
        context = await self._load_trip_runtime_context(event.trip_id)
        flagged = context.get("flagged_events", [])
        flagged_count = len(flagged) if isinstance(flagged, list) else 0

        baseline = context.get("historical_avg_score")
        if baseline is None:
            baseline = await self._get_rolling_average_score(event.driver_id, n=3)
        baseline_score = float(baseline) if isinstance(baseline, (int, float)) else 75.0

        all_pings = await self._get_all_pings_for_trip(event.trip_id)
        estimated_score = self._estimate_trip_score(all_pings)

        triggered_rules: list[str] = []
        if estimated_score < 60:
            triggered_rules.append("absolute_score")
        if (baseline_score - estimated_score) > 10:
            triggered_rules.append("baseline_drop")
        if flagged_count > 0:
            triggered_rules.append("flagged_events")

        logger.info(
            {
                "action": "coaching_rules_evaluated",
                "trip_id": event.trip_id,
                "event_id": event.event_id,
                "device_event_id": event.device_event_id,
                "estimated_score": estimated_score,
                "historical_avg_score": baseline_score,
                "flagged_events_count": flagged_count,
                "triggered_rules": triggered_rules,
                "coaching_needed": len(triggered_rules) > 0,
            }
        )
        return len(triggered_rules) > 0

    async def _apply_dispatch_policy(
        self, event: TripEvent, agents_to_dispatch: list[str]
    ) -> list[str]:
        deduped = list(dict.fromkeys(agents_to_dispatch))

        if event.event_type in FLAGGED_EVENT_TYPES:
            await self._append_flagged_event(event)
            deduped = [a for a in deduped if a not in {"support", "driver_support"}]

        if event.event_type == "end_of_trip":
            coaching_needed = await self._should_dispatch_coaching(event)
            context = await self._load_trip_runtime_context(event.trip_id)
            context["coaching_pending_after_scoring"] = coaching_needed
            context.setdefault("trip_id", event.trip_id)
            context.setdefault("driver_id", event.driver_id)
            context.setdefault("truck_id", event.truck_id)
            await self._save_trip_runtime_context(event.trip_id, context)
            # Scoring only on this event; Support runs later via coaching_ready
            deduped = [a for a in deduped if a not in {"support", "driver_support"}]

        if event.event_type == "coaching_ready":
            deduped = [a for a in deduped if a in {"support", "driver_support"}] or [
                "driver_support"
            ]
        if event.event_type == "sentiment_ready":
            deduped = [a for a in deduped if a in {"support", "driver_support"}] or [
                "driver_support"
            ]
            context = await self._load_trip_runtime_context(event.trip_id)
            context["sentiment_support_pending"] = False
            context.setdefault("trip_id", event.trip_id)
            context.setdefault("driver_id", event.driver_id)
            context.setdefault("truck_id", event.truck_id)
            await self._save_trip_runtime_context(event.trip_id, context)

        if (
            event.event_type in CRITICAL_IMMEDIATE_SUPPORT_TYPES
            and "support" not in deduped
        ):
            deduped.append("support")

        logger.info(
            {
                "action": "dispatch_policy_applied",
                "trip_id": event.trip_id,
                "event_id": event.event_id,
                "device_event_id": event.device_event_id,
                "event_type": event.event_type,
                "agents_after_policy": deduped,
            }
        )
        return deduped

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
            # COACHING / REGULATORY events use event-driven warming, but if routing
            # still dispatches scoring (e.g. harsh_brake), ScoringAgent needs all_pings.
            if "scoring" in agents_to_dispatch:
                await self._warm_aggregation_driven(event, ["scoring"])

        elif warming_type == "aggregation-driven":
            await self._warm_aggregation_driven(event, agents_to_dispatch)

        elif warming_type == "post_scoring_support":
            await self._warm_post_scoring_support(event, agents_to_dispatch)
        elif warming_type == "post_sentiment_support":
            await self._warm_post_sentiment_support(event, agents_to_dispatch)

        else:
            logger.info(
                {
                    "action": "cache_warming_skipped",
                    "trip_id": trip_id,
                    "event_id": event.event_id,
                    "device_event_id": event.device_event_id,
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
                        "event_id": event.event_id,
                        "device_event_id": event.device_event_id,
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
                trip_context_payload = {
                    **trip_metadata,
                    "primary_event_location": current_event.get("location"),
                    "primary_event_evidence": current_event.get("evidence") or {},
                }
                await self.redis._client.setex(
                    context_key,
                    300,  # 5 minute TTL
                    json.dumps(trip_context_payload),
                )

            logger.info(
                {
                    "action": "cache_warmed_event_driven",
                    "trip_id": trip_id,
                    "event_type": event_type,
                    "agents": agents_to_dispatch,
                    "data_size_bytes": len(json.dumps(current_event))
                    + len(json.dumps(trip_context_payload)),
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
                ctx_key = RedisSchema.Trip.agent_data(trip_id, agent, "trip_context")
                scoring_context = {
                    **trip_metadata,
                    "historical_avg_score": rolling_avg,
                }
                await self.redis._client.setex(
                    ctx_key,
                    3600,
                    json.dumps(scoring_context),
                )

            if need_support:
                agent = "support"
                context_key = RedisSchema.Trip.agent_data(
                    trip_id, agent, "trip_context"
                )
                runtime_context = await self._load_trip_runtime_context(trip_id)
                support_context = {
                    **trip_metadata,
                    "historical_avg_score": runtime_context.get(
                        "historical_avg_score", rolling_avg
                    ),
                    "flagged_events": runtime_context.get("flagged_events", []),
                }
                await self.redis._client.setex(
                    context_key,
                    3600,
                    json.dumps(support_context),
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
                    "event_id": event.event_id,
                    "device_event_id": event.device_event_id,
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

    async def _warm_post_scoring_support(
        self,
        event: TripEvent,
        agents_to_dispatch: list[str],
    ) -> None:
        """
        Support after scoring: trip metadata, coaching history, plus latest
        scoring_output and safety_output from Redis (Safety may have run mid-trip).
        """
        trip_id = event.trip_id
        try:
            if not any(a in agents_to_dispatch for a in ("support", "driver_support")):
                return

            trip_metadata = await self._get_trip_metadata(trip_id)
            if not trip_metadata:
                logger.warning(
                    {"action": "post_scoring_warm_no_metadata", "trip_id": trip_id}
                )
                return

            driver_id = trip_metadata.get("driver_id")
            coaching_history: list[dict] = []
            if driver_id:
                coaching_history = await self._get_coaching_history(trip_id)

            runtime_context = await self._load_trip_runtime_context(trip_id)
            scoring_raw = await self.redis._client.get(
                RedisSchema.Trip.output(trip_id, "scoring")
            )
            safety_raw = await self.redis._client.get(
                RedisSchema.Trip.output(trip_id, "safety")
            )
            scoring_payload: dict | list | None = None
            safety_payload: dict | list | None = None
            if scoring_raw:
                try:
                    scoring_payload = json.loads(scoring_raw)
                except json.JSONDecodeError:
                    scoring_payload = None
            if safety_raw:
                try:
                    safety_payload = json.loads(safety_raw)
                except json.JSONDecodeError:
                    safety_payload = None

            support_context = {
                **trip_metadata,
                "historical_avg_score": runtime_context.get("historical_avg_score"),
                "flagged_events": runtime_context.get("flagged_events", []),
                "scoring_output": scoring_payload,
                "safety_output": safety_payload,
            }
            agent = "support"
            context_key = RedisSchema.Trip.agent_data(trip_id, agent, "trip_context")
            await self.redis._client.setex(
                context_key,
                3600,
                json.dumps(support_context),
            )
            history_key = RedisSchema.Trip.agent_data(
                trip_id, agent, "coaching_history"
            )
            await self.redis._client.setex(
                history_key,
                3600,
                json.dumps(coaching_history),
            )
            logger.info(
                {
                    "action": "cache_warmed_post_scoring_support",
                    "trip_id": trip_id,
                    "has_scoring_output": scoring_payload is not None,
                    "has_safety_output": safety_payload is not None,
                }
            )
        except Exception as e:
            logger.error(
                {
                    "action": "post_scoring_support_warming_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )

    async def _warm_post_sentiment_support(
        self,
        event: TripEvent,
        agents_to_dispatch: list[str],
    ) -> None:
        """
        Support after sentiment: trip metadata + sentiment output snapshot.
        """
        trip_id = event.trip_id
        try:
            if not any(a in agents_to_dispatch for a in ("support", "driver_support")):
                return

            trip_metadata = await self._get_trip_metadata(trip_id)
            if not trip_metadata:
                logger.warning(
                    {"action": "post_sentiment_warm_no_metadata", "trip_id": trip_id}
                )
                return

            runtime_context = await self._load_trip_runtime_context(trip_id)
            sentiment_raw = await self.redis._client.get(
                RedisSchema.Trip.output(trip_id, "sentiment")
            )
            sentiment_payload: dict | list | None = None
            if sentiment_raw:
                try:
                    sentiment_payload = json.loads(sentiment_raw)
                except json.JSONDecodeError:
                    sentiment_payload = None

            support_context = {
                **trip_metadata,
                "flagged_events": runtime_context.get("flagged_events", []),
                "sentiment_output": sentiment_payload,
            }
            context_key = RedisSchema.Trip.agent_data(
                trip_id, "support", "trip_context"
            )
            await self.redis._client.setex(
                context_key,
                3600,
                json.dumps(support_context),
            )

            logger.info(
                {
                    "action": "cache_warmed_post_sentiment_support",
                    "trip_id": trip_id,
                    "has_sentiment_output": sentiment_payload is not None,
                }
            )
        except Exception as e:
            logger.error(
                {
                    "action": "post_sentiment_support_warming_error",
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
        agents_to_dispatch = self._resolve_agents_for_dispatch(event, routing_decision)
        agents_to_dispatch = await self._apply_dispatch_policy(
            event, agents_to_dispatch
        )
        routing_decision["agents_to_dispatch"] = agents_to_dispatch

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

    def _resolve_agents_for_dispatch(
        self, event: TripEvent, routing_decision: dict
    ) -> list[str]:
        """
        Resolve final candidate agents from routing decision with optional fallback.

        Modes via settings.orchestrator_routing_fallback_mode:
          - off: keep current behavior (no routing fallback changes)
          - shadow: log fallback candidate but keep original result
          - enforce: replace invalid/empty critical output with EventMatrix fallback
        """
        raw_agents = routing_decision.get("agents_to_dispatch", [])
        fallback_mode = (settings.orchestrator_routing_fallback_mode or "off").lower()
        allowed_agents = {"safety", "scoring", "support", "driver_support", "sentiment"}
        normalized: list[str] = []
        if isinstance(raw_agents, list):
            normalized = [a for a in raw_agents if isinstance(a, str)]
        filtered = [a for a in normalized if a in allowed_agents]

        config = EVENT_MATRIX.get(event.event_type)
        fallback_agents = compute_routing_agents(config) if config is not None else []
        is_high_or_critical = bool(
            config and str(config.priority.value).lower() in {"high", "critical"}
        )

        needs_fallback = (not isinstance(raw_agents, list)) or (
            is_high_or_critical and len(filtered) == 0
        )

        if fallback_mode == "shadow" and needs_fallback:
            logger.warning(
                {
                    "action": "routing_fallback_shadow",
                    "trip_id": event.trip_id,
                    "event_id": event.event_id,
                    "device_event_id": event.device_event_id,
                    "event_type": event.event_type,
                    "raw_agents_type": type(raw_agents).__name__,
                    "filtered_agents": filtered,
                    "fallback_agents": fallback_agents,
                }
            )
            return filtered

        if fallback_mode == "enforce" and needs_fallback:
            logger.warning(
                {
                    "action": "routing_fallback_enforced",
                    "trip_id": event.trip_id,
                    "event_id": event.event_id,
                    "device_event_id": event.device_event_id,
                    "event_type": event.event_type,
                    "raw_agents_type": type(raw_agents).__name__,
                    "fallback_agents": fallback_agents,
                }
            )
            return fallback_agents

        return filtered

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
            # For harsh-event coaching paths, Scoring is also warmed with
            # aggregation keys. Include them so the scoring task can read
            # all_pings/historical_avg instead of falling back to no_pings_data.
            if agent_name == "scoring":
                read_keys.extend(
                    [
                        RedisSchema.Trip.agent_data(trip_id, agent_name, "all_pings"),
                        RedisSchema.Trip.agent_data(
                            trip_id, agent_name, "historical_avg"
                        ),
                    ]
                )

        elif warming_type == "aggregation-driven":
            # Aggregation-driven agents get specific keys based on agent type
            if agent_name == "scoring":
                read_keys = [
                    RedisSchema.Trip.agent_data(trip_id, agent_name, "all_pings"),
                    RedisSchema.Trip.agent_data(trip_id, agent_name, "historical_avg"),
                    RedisSchema.Trip.agent_data(trip_id, agent_name, "trip_context"),
                ]
            elif agent_name in ("support", "driver_support"):
                read_keys = [
                    RedisSchema.Trip.agent_data(trip_id, "support", "trip_context"),
                    RedisSchema.Trip.agent_data(trip_id, "support", "coaching_history"),
                ]
            else:
                # Fallback for unknown agents
                read_keys = [
                    RedisSchema.Trip.context(trip_id),
                    RedisSchema.Trip.smoothness_logs(trip_id),
                ]
        elif warming_type == "post_scoring_support":
            read_keys = [
                RedisSchema.Trip.agent_data(trip_id, "support", "trip_context"),
                RedisSchema.Trip.agent_data(trip_id, "support", "coaching_history"),
            ]
        elif warming_type == "post_sentiment_support":
            read_keys = [
                RedisSchema.Trip.agent_data(trip_id, "support", "trip_context")
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
        user_prompt = build_orchestrator_routing_user_message(event)

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
                                    "trip_id": event.trip_id,
                                    "event_id": event.event_id,
                                    "device_event_id": event.device_event_id,
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
            elif agent_name == "support" or agent_name == "driver_support":
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
            await AgentFlowService(self.redis).publish_event(
                AgentFlowEvent(
                    event_type="agent_queued",
                    status="queued",
                    agent="support" if agent_name in ("support", "driver_support") else agent_name,  # type: ignore[arg-type]
                    trip_id=event.trip_id,
                    meta={
                        "queue": target_queue,
                        "event_type": event.event_type,
                    },
                )
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
