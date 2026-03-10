"""
AuditLog — immutable record of every consequential action in the system.

IMDA AI GOVERNANCE REQUIREMENT:
    The IMDA Model AI Governance Framework requires accountability for every
    AI-generated decision. AuditLog is the technical implementation of that:
    it records who (human or which agent) did what to which entity and when.

    Every alert raised, every risk score generated, every human approval or
    override must produce an AuditLog row. This is the evidence trail for
    the governance section of the group report.

APPEND-ONLY CONTRACT:
    Never UPDATE or DELETE audit rows. If a bug produced a wrong audit entry,
    insert a CORRECTION row with action="correction_of:<original_id>".
    The audit trail must be complete and tamper-evident.

ACTOR TYPES:
    human    — a logged-in fleet manager (actor_id = their session user ID)
    ai_agent — one of our 4 LangGraph agents (actor_id = agent node name)
    system   — background job / Celery task / Kafka consumer

TRACE EXERCISE (from master_plan.md cross-agent demo):
    Vehicle V007 maintenance alert → human approval flow produces:
        Row 1: actor=ai_agent(maintenance), action=failure_predicted,  entity=Vehicle V007
        Row 2: actor=ai_agent(orchestrator), action=alert_dispatched,  entity=AlertPending #X
        Row 3: actor=human(manager_id),  action=alert_approved,        entity=AlertPending #X

    How many rows if the manager escalates instead of approving?
    → Same 3 rows except Row 3 action="alert_escalated"
    + Row 4: actor=system, action=escalation_notified, entity=AlertPending #X
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ActorType(str, enum.Enum):
    HUMAN    = "human"      # logged-in fleet manager
    AI_AGENT = "ai_agent"   # one of the 4 LangGraph agents
    SYSTEM   = "system"     # Celery task, Kafka consumer, scheduled job


class AuditLog(Base):
    """Immutable audit trail. INSERT only — never UPDATE, never DELETE."""

    __tablename__ = "audit_logs"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Who ───────────────────────────────────────────────────────────────────
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True,
        comment="User ID, Agent name hash, or null for anonymous system actions"
    )
    actor_type: Mapped[ActorType] = mapped_column(
        Enum(ActorType, name="actor_type_enum"), nullable=False
    )
    actor_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="Human-readable name — denormalised for audit readability without JOIN"
    )

    # ── What ──────────────────────────────────────────────────────────────────
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True,
        comment="Verb: failure_predicted | alert_dispatched | alert_approved | risk_flagged…"
    )

    # ── Which entity ──────────────────────────────────────────────────────────
    entity_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True,
        comment="vehicle | driver | alert_pending | trip | compliance_check…"
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # ── Context ───────────────────────────────────────────────────────────────
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Before/after state, SHAP values, agent reasoning, request context"
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── When ──────────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc), index=True
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog {self.actor_type}:{self.actor_name}"
            f" → {self.action} on {self.entity_type}:{self.entity_id}>"
        )
