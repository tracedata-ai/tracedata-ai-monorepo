"""
Security Models — IntentCapsule and ScopedToken.

IntentCapsule:  immutable signed mission plan issued by Orchestrator.
                Sealed with HMAC-SHA256 before Celery dispatch.
                Every tool call verifies the seal has not been tampered with.

ScopedToken:    defines which Redis keys an agent may read/write.
                Enforces principle of least privilege — agents cannot
                access other agents' data or real driver identities.

ExecutionContext: mutable runtime state (step_index lives here, NOT in capsule).
ExecutionLog:    immutable audit record written on every tool call.

Location: backend/common/models/security.py
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

# ── ScopedToken ───────────────────────────────────────────────────────────────


class ScopedToken(BaseModel):
    """
    Defines exactly which Redis keys this agent may touch for this trip.
    Issued by Orchestrator, embedded inside IntentCapsule.

    Key constraint: read_keys never include demographic fields or real driver_id.
    This enforces Fairness Through Unawareness at the access control level.
    """

    agent: str
    trip_id: str
    expires_at: datetime
    read_keys: list[str] = Field(default_factory=list)
    write_keys: list[str] = Field(default_factory=list)


# ── IntentCapsule ─────────────────────────────────────────────────────────────


class IntentCapsule(BaseModel):
    """
    Immutable signed mission plan for one agent execution.

    Sealed by Orchestrator with HMAC-SHA256 before dispatch.
    Verified by Intent Gate before every tool call.

    is_closed is set True by Orchestrator after final CompletionEvent.
    Once closed the capsule is an immutable audit record.

    step_to_tools defines which tools are permitted at each step:
        { "1": ["redis_read", "xgboost_tool"],
          "2": ["redis_write", "llm_call"] }
    """

    trip_id: str
    agent: str
    priority: int
    step_index_max: int = 1
    tool_whitelist: list[str] = Field(default_factory=list)
    step_to_tools: dict[str, list[str]] = Field(default_factory=dict)
    permitted_tools: list[str] = Field(default_factory=list)  # flat alias
    hmac_seal: str = ""  # set by sign_capsule()
    issued_by: str = "orchestrator"
    ttl_seconds: int = 3600
    is_closed: bool = False
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    closed_at: datetime | None = None
    token: "ScopedToken | None" = None


# ── ExecutionContext ──────────────────────────────────────────────────────────


class ExecutionContext(BaseModel):
    """
    Mutable runtime state for one agent execution.

    step_index lives HERE — not in IntentCapsule (which is immutable).
    Orchestrator is the only component that increments step_index.
    Intent Gate reads this to enforce step sequence validation.
    """

    correlation_id: str
    trip_id: str
    agent: str
    current_step_index: int = 0
    completed_actions: list[str] = Field(default_factory=list)
    status: str = "PENDING"
    # PENDING → IN_PROGRESS → COMPLETED | LOCKED
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ── ExecutionLog ──────────────────────────────────────────────────────────────


class ExecutionLog(BaseModel):
    """
    Immutable audit record written on every tool call.
    Written by Intent Gate — on success AND failure.

    capsule_snapshot captures exact capsule state at call time,
    enabling forensic replay and compliance audit.
    """

    log_id: str
    trip_id: str
    capsule_id: str
    agent: str
    tool_name: str
    step_index: int
    status: str  # 'success' | 'rejected_hmac' | 'rejected_whitelist' |
    # 'rejected_sequence' | 'rejected_pii' | 'rejected_hitl' | 'error'
    capsule_snapshot: dict[str, Any] = Field(default_factory=dict)
    rejection_reason: str | None = None
    tokens_input: int | None = None
    tokens_output: int | None = None
    latency_ms: int | None = None
    executed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ── ForensicSnapshot ──────────────────────────────────────────────────────────


class ForensicSnapshot(BaseModel):
    """
    Captured on security violations. Published to critical-alerts channel.
    Also persisted to execution_logs table.
    """

    trip_id: str
    agent: str
    tool_name: str
    violation_type: str  # 'hmac_mismatch' | 'whitelist_violation' |
    # 'sequence_violation' | 'pii_detected' | 'hitl_required'
    capsule_snapshot: dict[str, Any] = Field(default_factory=dict)
    offending_input: str = ""  # first 200 chars only
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ── Backwards compatibility ───────────────────────────────────────────────────
# Old SecurityContext referenced in some API routes — keep until cleaned up.


class SecurityContext(BaseModel):
    token: str
    intent_id: str
    hmac_sig: str
