"""
AlertPending — the human-in-the-loop queue.

PURPOSE:
    Every consequential AI decision goes through this table before it
    affects a driver's record or triggers an operational action.
    Fleet managers see alerts in the dashboard and choose:
        approve   → action proceeds, AuditLog row written
        dismiss   → alert closed, AuditLog row written  
        escalate  → sent to senior manager, AuditLog row written

    The human_decision field starts NULL (pending) and is set by the
    manager's action. The Orchestrator polls this table for pending alerts
    and synthesises the cross-agent evidence into the alert description.

FROM master_plan.md CROSS-AGENT DEMO:
    "Orchestrator synthesises a single unified alert: SHAP reasoning from
    each agent, plain English summary, two action buttons: Approve / Escalate"
    "Fleet manager's human_decision field (approve/dismiss/escalate) written
    to AuditLog"

    This table IS that "unified alert". One row per cross-agent finding.

LIFECYCLE:
    1. Agent detects issue → INSERT with human_decision=NULL
    2. Fleet manager sees alert in dashboard
    3. Manager clicks Approve → UPDATE human_decision="approve", resolved_at=now
    4. AuditLog row written for the decision
    5. Downstream action triggered (e.g. schedule maintenance)
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AlertSeverity(str, enum.Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class HumanDecision(str, enum.Enum):
    APPROVE  = "approve"
    DISMISS  = "dismiss"
    ESCALATE = "escalate"


class AlertPending(Base):
    __tablename__ = "alerts_pending"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Source ────────────────────────────────────────────────────────────────
    agent_source: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True,
        comment="Which agent created this alert: orchestrator | maintenance | compliance | customer_intel"
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="alert_severity_enum"),
        nullable=False, default=AlertSeverity.MEDIUM
    )

    # ── Subject (what the alert is about) ─────────────────────────────────────
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # ── Content ───────────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Short title shown in dashboard: 'Vehicle V007 — High Brake Wear Risk'"
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Full plain-English explanation including SHAP reasoning from agents"
    )
    evidence_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Raw cross-agent evidence: SHAP values, telemetry snapshots, compliance flags"
    )

    # ── Human Decision ────────────────────────────────────────────────────────
    human_decision: Mapped[HumanDecision | None] = mapped_column(
        Enum(HumanDecision, name="human_decision_enum"),
        nullable=True, default=None,
        comment="NULL = pending manager action. Set when manager acts in dashboard."
    )
    decided_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True,
        comment="User ID of the manager who made the decision"
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc), index=True
    )

    def __repr__(self) -> str:
        return (
            f"<AlertPending [{self.severity}] from {self.agent_source}"
            f" — decision={self.human_decision}>"
        )
