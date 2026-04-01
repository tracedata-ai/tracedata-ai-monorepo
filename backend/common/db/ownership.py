"""
TABLE OWNERSHIP MATRIX - Single Source of Truth

Defines data ownership, access patterns, and write rules for all tables.
Enforced at 3 layers: Code Structure → Intent Capsule → Database Permissions.
"""

from enum import Enum


class Owner(str, Enum):
    """Table owners"""

    DB_MANAGER = "DBManager"
    SAFETY_AGENT = "SafetyAgent"
    SCORING_AGENT = "ScoringAgent"
    SENTIMENT_AGENT = "SentimentAgent"
    SUPPORT_AGENT = "SupportAgent"


class TABLE_OWNERSHIP:
    """
    Central authority for table ownership, access, and write rules.

    Format:
      "schema.table": {
          "owner": Owner enum,
          "can_read": [who can read],
          "can_write": [who can write],
          "write_rule": "direct|orchestrator|db_manager"
      }

    Write Rules:
      - direct: Direct write to own table (via own repo)
      - orchestrator: Request via orchestrator to proper owner
      - db_manager: Only DBManager writes (shared tables)
    """

    # ─── SHARED TABLES (Public Schema) ─────────────────────────────────────
    # All agents READ, only DBManager WRITES

    TRIPS = {
        "owner": Owner.DB_MANAGER,
        "can_read": ["all_agents"],
        "can_write": [Owner.DB_MANAGER],
        "write_rule": "db_manager",
        "description": "Trip metadata (shared across all agents)",
    }

    EVENTS = {
        "owner": Owner.DB_MANAGER,
        "can_read": ["all_agents"],
        "can_write": [Owner.DB_MANAGER],
        "write_rule": "db_manager",
        "description": "Pipeline events (shared, immutable)",
    }

    # ─── SAFETY AGENT TABLES ──────────────────────────────────────────────
    # SafetyAgent owns exclusively

    HARSH_EVENTS_ANALYSIS = {
        "owner": Owner.SAFETY_AGENT,
        "can_read": ["all_agents"],
        "can_write": [Owner.SAFETY_AGENT],
        "write_rule": "direct",
        "description": "Safety Agent's harsh event analysis",
    }

    SAFETY_DECISIONS = {
        "owner": Owner.SAFETY_AGENT,
        "can_read": ["all_agents"],
        "can_write": [Owner.SAFETY_AGENT],
        "write_rule": "direct",
        "description": "Safety Agent's decisions and actions",
    }

    # ─── SCORING AGENT TABLES ────────────────────────────────────────────
    # ScoringAgent owns exclusively

    TRIP_SCORES = {
        "owner": Owner.SCORING_AGENT,
        "can_read": ["all_agents"],
        "can_write": [Owner.SCORING_AGENT],
        "write_rule": "direct",
        "description": "Trip scores computed by Scoring Agent",
    }

    SHAP_EXPLANATIONS = {
        "owner": Owner.SCORING_AGENT,
        "can_read": ["all_agents"],
        "can_write": [Owner.SCORING_AGENT],
        "write_rule": "direct",
        "description": "SHAP explanations for trip scores",
    }

    FAIRNESS_AUDIT = {
        "owner": Owner.SCORING_AGENT,
        "can_read": ["all_agents"],
        "can_write": [Owner.SCORING_AGENT],
        "write_rule": "direct",
        "description": "Fairness audit log for scores",
    }

    # ─── SENTIMENT AGENT TABLES ───────────────────────────────────────────
    # SentimentAgent owns exclusively

    FEEDBACK_SENTIMENT = {
        "owner": Owner.SENTIMENT_AGENT,
        "can_read": ["all_agents"],
        "can_write": [Owner.SENTIMENT_AGENT],
        "write_rule": "direct",
        "description": "Sentiment analysis of driver feedback",
    }

    # ─── SUPPORT AGENT TABLES ─────────────────────────────────────────────
    # Support Agent owns exclusively

    COACHING = {
        "owner": Owner.SUPPORT_AGENT,
        "can_read": ["all_agents"],
        "can_write": [Owner.SUPPORT_AGENT],
        "write_rule": "direct",
        "description": "Coaching messages (Support Agent only writes)",
    }

    DRIVER_FEEDBACK = {
        "owner": Owner.SUPPORT_AGENT,
        "can_read": ["all_agents"],
        "can_write": [Owner.SUPPORT_AGENT],
        "write_rule": "direct",
        "description": "Driver feedback records",
    }


# ── BUILD LOOKUP TABLES ────────────────────────────────────────────────────


def _build_ownership_map():
    """Build lookup table: schema.table → ownership rules"""
    ownership_map = {
        # Shared
        "public.trips": TABLE_OWNERSHIP.TRIPS,
        "public.events": TABLE_OWNERSHIP.EVENTS,
        # Safety
        "safety_schema.harsh_events_analysis": TABLE_OWNERSHIP.HARSH_EVENTS_ANALYSIS,
        "safety_schema.safety_decisions": TABLE_OWNERSHIP.SAFETY_DECISIONS,
        # Scoring
        "scoring_schema.trip_scores": TABLE_OWNERSHIP.TRIP_SCORES,
        "scoring_schema.shap_explanations": TABLE_OWNERSHIP.SHAP_EXPLANATIONS,
        "scoring_schema.fairness_audit": TABLE_OWNERSHIP.FAIRNESS_AUDIT,
        # Sentiment
        "sentiment_schema.feedback_sentiment": TABLE_OWNERSHIP.FEEDBACK_SENTIMENT,
        # Support
        "coaching_schema.coaching": TABLE_OWNERSHIP.COACHING,
        "coaching_schema.driver_feedback": TABLE_OWNERSHIP.DRIVER_FEEDBACK,
    }
    return ownership_map


OWNERSHIP_MAP = _build_ownership_map()


def get_table_ownership(table_name: str) -> dict | None:
    """Get ownership rules for a table.

    Args:
        table_name: "schema.table" format

    Returns:
        Ownership dict or None if not found
    """
    return OWNERSHIP_MAP.get(table_name)


def can_write(table_name: str, agent: Owner | str) -> bool:
    """Check if agent can write to table.

    Args:
        table_name: "schema.table" format
        agent: Owner enum or string

    Returns:
        True if agent owns the table
    """
    if isinstance(agent, str):
        agent = Owner(agent)

    ownership = get_table_ownership(table_name)
    if not ownership:
        return False

    return agent in ownership["can_write"]


def get_agent_owned_tables(agent: Owner | str) -> list[str]:
    """Get all tables owned by an agent.

    Args:
        agent: Owner enum or string

    Returns:
        List of "schema.table" names
    """
    if isinstance(agent, str):
        agent = Owner(agent)

    owned = []
    for table_name, ownership in OWNERSHIP_MAP.items():
        if ownership["owner"] == agent:
            owned.append(table_name)

    return owned
