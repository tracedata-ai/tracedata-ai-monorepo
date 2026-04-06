"""
Orchestrator Tools — Event-Driven Routing with EventMatrix

These tools help the OrchestratorAgent make routing decisions:
1. Get event config from EventMatrix (single source of truth)
2. Evaluate coaching rules (deterministic, after scoring)

EventMatrix is imported from common/config/events.py (SINGLE SOURCE OF TRUTH)
LLM validates and interprets the action field for edge cases.
"""

import json
import logging

from langchain_core.tools import tool

from common.config.events import (
    EVENT_MATRIX,
    PRIORITY_MAP,
    compute_routing_agents,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# TOOL 1: Get Event Config from EventMatrix
# ==============================================================================


@tool
def get_event_config(trigger_event_type: str) -> str:
    """
    Look up event in EventMatrix (single source of truth from common/config/events.py).

    Returns event configuration with:
    - category: Event category (e.g., "critical", "harsh_events", "trip_lifecycle")
    - priority: Event priority (CRITICAL, HIGH, MEDIUM, LOW)
    - priority_score: Redis ZSet score (0=CRITICAL, 3=HIGH, 6=MEDIUM, 9=LOW)
    - ml_weight: ML weighting factor for scoring
    - action: What should happen with this event

    Args:
        trigger_event_type: Event type (e.g., "collision", "harsh_brake", "end_of_trip")

    Returns:
        JSON string with event configuration from EventMatrix
    """
    event_config = EVENT_MATRIX.get(trigger_event_type)

    if not event_config:
        return json.dumps(
            {
                "error": f"Unknown event type: '{trigger_event_type}'",
                "available_events": sorted(list(EVENT_MATRIX.keys())),
                "hint": "Use one of the available_events. If new event, add to common/config/events.py first.",
            }
        )

    # Routing: action mapping + safety for all HIGH/CRITICAL events
    agents_from_action = compute_routing_agents(event_config)

    # Convert priority to score
    priority_score = PRIORITY_MAP.get(event_config.priority, 9)

    # Convert Action enum to string for JSON serialization
    action_name = event_config.action.name.replace("_", " ").title()

    config = {
        "event_type": trigger_event_type,
        "category": event_config.category,
        "priority": str(event_config.priority.name),
        "priority_score": priority_score,
        "ml_weight": event_config.ml_weight,
        "action": action_name,
        "agents_from_action": agents_from_action,
        "reasoning": "EventMatrix from common/config/events.py is the single source of truth",
    }

    logger.info(
        f"Event config lookup: {trigger_event_type} → {event_config.action} "
        f"({agents_from_action})"
    )

    return json.dumps(config)


# ==============================================================================
# TOOL 2: Evaluate Coaching Rules (Deterministic)
# ==============================================================================


@tool
def evaluate_coaching_rules(
    behaviour_score: float,
    historical_avg: float,
    flagged_events_count: int,
) -> str:
    """
    DETERMINISTIC rule engine: Should Driver Support Agent run?

    Evaluates three coaching rules. ANY rule triggering means coaching is needed.

    Rule 1: Absolute Floor
      IF behaviour_score < 60
      Reasoning: Score below safe threshold, high-risk state requiring intervention

    Rule 2: Negative Trend Detection
      IF |behaviour_score - historical_avg| > 10
      Reasoning: Significant drop from baseline, catching gradual decline

    Rule 3: Flagged Events Present
      IF flagged_events_count > 0
      Reasoning: Safety incidents occurred during trip, context-specific coaching needed

    Args:
        behaviour_score: Trip score from ScoringAgent (0-100)
        historical_avg: Driver's 3-trip rolling average (0-100)
        flagged_events_count: Number of safety-flagged events this trip

    Returns:
        JSON string with coaching decision

    Example Output (All Rules Triggered):
        {
          "coaching_needed": true,
          "triggered_rules": ["absolute_floor", "trend_detection", "flagged_events"],
          "priority_escalation": true,
          "new_priority": "MEDIUM",
          "reasoning": "Score: 54.2, Avg: 68.4, Events: 2"
        }

    Example Output (No Rules Triggered):
        {
          "coaching_needed": false,
          "triggered_rules": [],
          "priority_escalation": false,
          "new_priority": "LOW",
          "reasoning": "Score: 78.5, Avg: 76.1, Events: 0"
        }
    """

    triggered_rules = []
    coaching_needed = False

    # Rule 1: Absolute Floor
    if behaviour_score < 60:
        triggered_rules.append("absolute_floor")
        coaching_needed = True

    # Rule 2: Negative Trend Detection
    if abs(behaviour_score - historical_avg) > 10:
        triggered_rules.append("trend_detection")
        coaching_needed = True

    # Rule 3: Flagged Events Present
    if flagged_events_count > 0:
        triggered_rules.append("flagged_events")
        coaching_needed = True

    # Priority escalation
    # If coaching is needed, escalate priority (LOW 9 → MEDIUM 6)
    priority_escalation = coaching_needed
    new_priority = "MEDIUM" if priority_escalation else "LOW"

    decision = {
        "coaching_needed": coaching_needed,
        "triggered_rules": triggered_rules,
        "priority_escalation": priority_escalation,
        "new_priority": new_priority,
        "reasoning": (
            f"Score: {behaviour_score}, Historical Avg: {historical_avg}, "
            f"Flagged Events: {flagged_events_count}"
        ),
    }

    logger.info(
        f"Coaching evaluation: needed={coaching_needed}, "
        f"rules={triggered_rules}, escalation={priority_escalation}"
    )

    return json.dumps(decision)


# ==============================================================================
# Tool Registry
# ==============================================================================

ORCHESTRATOR_TOOLS = [
    get_event_config,  # Look up event in EventMatrix
    evaluate_coaching_rules,  # Deterministic coaching rule engine
]
