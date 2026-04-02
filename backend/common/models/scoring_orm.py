"""Scoring schema ORM — registered in ``api.models`` for ``create_all``."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from common.models.sa_base import Base


class TripScoreORM(Base):
    """Trip behaviour score row (ScoringRepository raw INSERT targets this table)."""

    __tablename__ = "trip_scores"
    __table_args__ = (
        UniqueConstraint("trip_id", name="uq_trip_scores_trip_id"),
        {"schema": "scoring_schema"},
    )

    score_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    trip_id: Mapped[str] = mapped_column(String(100))
    driver_id: Mapped[str] = mapped_column(String(50))
    score: Mapped[float] = mapped_column(Float)
    score_breakdown: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ShapExplanationORM(Base):
    __tablename__ = "shap_explanations"
    __table_args__ = (
        UniqueConstraint("trip_id", name="uq_shap_explanations_trip_id"),
        {"schema": "scoring_schema"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    score_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    trip_id: Mapped[str] = mapped_column(String(100))
    explanations: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class FairnessAuditORM(Base):
    __tablename__ = "fairness_audit"
    __table_args__ = (
        UniqueConstraint("trip_id", name="uq_fairness_audit_trip_id"),
        {"schema": "scoring_schema"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    score_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    trip_id: Mapped[str] = mapped_column(String(100))
    driver_id: Mapped[str] = mapped_column(String(50))
    audit_result: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
