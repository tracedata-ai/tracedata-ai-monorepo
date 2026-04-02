"""
Intent Gate — security decorator for all tool calls.

Every tool in the Tool Registry is wrapped with @unified_tool_gateway.
This decorator runs BEFORE the tool executes and enforces:

  1. HMAC verification    — IntentCapsule has not been tampered with
  2. Whitelist check      — tool is in capsule.tool_whitelist
  3. Step sequence        — step_index is in order (no leapfrogging)
  4. PII scrub            — no driver_id in LLM prompts (OWASP LLM02)
  5. HITL check           — escalate if score threshold exceeded
  6. ExecutionLog write   — immutable audit record per call

Sprint 2:  stub — decorator logs the call and passes through.
           No HMAC verification, no whitelist check.
Phase 6:   full enforcement.

Location: backend/security/intent_gate.py
"""

import functools
import logging
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# ── Stub flag — set False in Phase 6 to enforce fully ────────────────────────
ENFORCEMENT_ENABLED: bool = False


def unified_tool_gateway(func: Callable) -> Callable:
    """
    Decorator applied to every tool function in the Tool Registry.

    Sprint 2 behaviour (ENFORCEMENT_ENABLED = False):
      - Logs the tool call with trip_id and tool name
      - Writes a stub ExecutionLog entry
      - Passes through to the real tool function
      - Never blocks execution

    Phase 6 behaviour (ENFORCEMENT_ENABLED = True):
      - HMAC verify IntentCapsule
      - Check tool_whitelist
      - Validate step_index sequence
      - PII scrub inputs
      - HITL check
      - Write real ExecutionLog to Postgres

    Usage:
        @unified_tool_gateway
        async def xgboost_tool(self, features: dict) -> float:
            return self.model.predict(features)
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        tool_name = func.__name__
        # Try to extract trip_id from kwargs or first arg if it's a model
        trip_id = kwargs.get("trip_id", "unknown")

        log_entry = {
            "action": "tool_call",
            "tool": tool_name,
            "trip_id": trip_id,
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "enforced": ENFORCEMENT_ENABLED,
        }

        if ENFORCEMENT_ENABLED:
            # Phase 6: full enforcement
            # capsule = kwargs.get("capsule") or _get_capsule_from_context()
            # _verify_hmac(capsule)
            # _check_whitelist(capsule, tool_name)
            # _validate_step_index(capsule)
            # kwargs = _scrub_pii_from_inputs(kwargs)
            # _check_hitl_threshold(capsule)
            logger.info({**log_entry, "gate": "enforced"})
        else:
            logger.debug({**log_entry, "gate": "stub_passthrough"})

        try:
            result = await func(*args, **kwargs)
            log_entry["status"] = "success"
            logger.debug({**log_entry})
            return result

        except Exception as exc:
            log_entry["status"] = "error"
            log_entry["error"] = str(exc)[:200]
            logger.error({**log_entry})
            raise

    return wrapper


# ── Security violation exception ──────────────────────────────────────────────


class SecurityViolation(Exception):
    """
    Raised when Intent Gate rejects a tool call.
    Celery tasks catch this and do NOT retry — fail fast.

    Attributes:
        violation_type: hmac_mismatch | whitelist_violation |
                        sequence_violation | pii_detected | hitl_required
        trip_id:        for correlation
        tool_name:      which tool was blocked
    """

    def __init__(
        self,
        violation_type: str,
        trip_id: str,
        tool_name: str,
        detail: str = "",
    ) -> None:
        self.violation_type = violation_type
        self.trip_id = trip_id
        self.tool_name = tool_name
        self.detail = detail
        super().__init__(
            f"SecurityViolation [{violation_type}] trip={trip_id} tool={tool_name}: {detail}"
        )
