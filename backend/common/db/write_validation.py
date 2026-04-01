"""
LAYER 2 ENFORCEMENT: Database Write Keys in Intent Capsule

Extends IntentCapsule with database write key scoping.
Checked at runtime before any database write.

Usage:
  token = ScopedToken(
    write_keys_database=[
      "safety_schema.harsh_events_analysis",
      "safety_schema.safety_decisions",
    ]
  )

  # In agent code:
  await self.db.execute_write(query, table="safety_schema.harsh_events_analysis")
  # ✅ In write_keys_database → allowed

  await self.db.execute_write(query, table="coaching_schema.coaching")
  # ❌ NOT in write_keys_database → exception
"""

from datetime import UTC, datetime
from typing import Callable

from common.db.ownership import Owner, can_write, get_table_ownership
import logging

logger = logging.getLogger(__name__)


class WriteKeyViolation(Exception):
    """Raised when agent tries to write to unauthorized table."""

    pass


class DatabaseWriteValidator:
    """
    Runtime enforcement for database write keys (Layer 2).

    Validates every database write against the agent's scoped permissions.
    """

    def __init__(self, agent: str, write_keys_database: list[str] | None = None):
        """
        Initialize validator.

        Args:
            agent: Agent name (e.g., "safety", "scoring")
            write_keys_database: List of "schema.table" names agent can write
        """
        self.agent = agent
        self.write_keys_database = set(write_keys_database or [])

    def validate_write(self, table_name: str) -> bool:
        """
        Check if agent can write to table.

        Args:
            table_name: "schema.table" format

        Returns:
            True if write is allowed

        Raises:
            WriteKeyViolation: If write is not allowed
        """
        if table_name not in self.write_keys_database:
            msg = (
                f"Agent '{self.agent}' attempted unauthorized write to '{table_name}'. "
                f"Allowed tables: {self.write_keys_database}"
            )
            logger.error(
                {
                    "action": "write_key_violation",
                    "agent": self.agent,
                    "table": table_name,
                    "allowed_tables": list(self.write_keys_database),
                }
            )
            raise WriteKeyViolation(msg)

        return True

    @staticmethod
    def get_agent_write_keys(agent: Owner | str) -> list[str]:
        """Get all tables agent owns and can write.

        Args:
            agent: Owner enum or string

        Returns:
            List of "schema.table" names
        """
        from common.db.ownership import get_agent_owned_tables

        owned_tables = get_agent_owned_tables(agent)
        return owned_tables

    @staticmethod
    def create_from_agent(agent: str) -> "DatabaseWriteValidator":
        """Create validator with agent's owned tables.

        Args:
            agent: Agent name as string

        Returns:
            DatabaseWriteValidator with write_keys populated
        """
        try:
            owner = Owner(agent)
        except ValueError:
            # Unknown agent
            logger.warning(
                {
                    "action": "unknown_agent",
                    "agent": agent,
                }
            )
            return DatabaseWriteValidator(agent, write_keys_database=[])

        owned_tables = DatabaseWriteValidator.get_agent_write_keys(owner)
        return DatabaseWriteValidator(agent, write_keys_database=owned_tables)


class DatabaseWriteGuard:
    """
    Decorator to wrap database write methods with validation.

    Example:
      @DatabaseWriteGuard(agent="safety")
      async def write_analysis(self, table, query):
          await db.execute(query)
    """

    def __init__(self, agent: str):
        self.agent = agent
        self.validator = DatabaseWriteValidator.create_from_agent(agent)

    def __call__(self, func: Callable) -> Callable:
        """Wrap function with write validation."""

        async def wrapper(*args, **kwargs):
            # Extract table name from kwargs or first arg after self
            table_name = kwargs.get("table") or (args[1] if len(args) > 1 else None)

            if table_name:
                self.validator.validate_write(table_name)

            return await func(*args, **kwargs)

        return wrapper


# ── SCHEMA :: AGENT MAPPING (for enforcement) ────────────────────────────────

AGENT_OWNED_SCHEMAS = {
    "safety": ["safety_schema"],
    "scoring": ["scoring_schema"],
    "sentiment": ["sentiment_schema"],
    "support": ["coaching_schema"],
    "driver_support": ["coaching_schema"],
}


def get_agent_allowed_schemas(agent: str) -> list[str]:
    """Get schemas agent owns.

    Args:
        agent: Agent name

    Returns:
        List of schema names
    """
    return AGENT_OWNED_SCHEMAS.get(agent, [])


def can_write_to_schema(agent: str, schema: str) -> bool:
    """Check if agent can write to schema.

    Args:
        agent: Agent name
        schema: Schema name

    Returns:
        True if allowed
    """
    allowed = get_agent_allowed_schemas(agent)
    return schema in allowed
