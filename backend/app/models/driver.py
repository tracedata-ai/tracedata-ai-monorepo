"""
Driver — a person licensed to operate a fleet vehicle.

AGE GROUP DESIGN (from master_plan.md simulated data spec):
    young  (22–30) : 40% of the 200-driver fleet  ← bias injected here
    mid    (31–44) : 35% of the 200-driver fleet
    senior (45–60) : 25% of the 200-driver fleet

    The simulator draws harsh_braking_count for young drivers from a
    distribution with mean 35% higher than senior drivers at equivalent
    speed. This produces Disparate Impact Ratio ≈ 0.62 — the seed of
    the AIF360 fairness demonstration.

    AgeGroup is stored on Driver so the Driver Behavior Agent can
    compute per-group statistics without a JOIN to telemetry.

WHY STORE AGE GROUP (NOT JUST DATE OF BIRTH)?
    date_of_birth changes meaning over time (a person ages). age_group is
    set at onboarding and stays fixed — it matches the simulator's fixed
    distribution and avoids recalculating group membership on every query.
"""

import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AgeGroup(str, enum.Enum):
    """
    Agreed age bands — matches simulator bias injection parameters.
    Do NOT change without updating truck_simulator.py and retraining the model.
    """
    YOUNG  = "young"   # 22–30  (40% of fleet)
    MID    = "mid"     # 31–44  (35% of fleet)
    SENIOR = "senior"  # 45–60  (25% of fleet)


class DriverStatus(str, enum.Enum):
    ACTIVE    = "active"
    INACTIVE  = "inactive"
    SUSPENDED = "suspended"


class Driver(Base):
    __tablename__ = "drivers"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Personal Details ──────────────────────────────────────────────────────
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    license_number: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )

    # ── Demographics (fairness analysis) ──────────────────────────────────────
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    age_group: Mapped[AgeGroup | None] = mapped_column(
        Enum(AgeGroup, name="age_group_enum"), nullable=True,
        comment="Pre-computed age band — AIF360 uses this as the protected attribute"
    )

    # ── Status ────────────────────────────────────────────────────────────────
    status: Mapped[DriverStatus] = mapped_column(
        Enum(DriverStatus, name="driver_status_enum"),
        nullable=False, default=DriverStatus.ACTIVE
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Driver {self.full_name} [{self.license_number}] {self.age_group}>"
