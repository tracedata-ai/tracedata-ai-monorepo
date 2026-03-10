"""
Models package — import ALL models here.

WHY THIS FILE EXISTS:
    Alembic's env.py imports Base from app.db.base, then does:
        import app.models  ← this file
    If a model file is never imported, SQLAlchemy doesn't register it in
    Base.metadata, and Alembic generates no migration for its table.

    One import here → all 5 tables covered in every migration.
"""

from app.models.alert import AlertPending, AlertSeverity, HumanDecision
from app.models.audit_log import ActorType, AuditLog
from app.models.driver import AgeGroup, Driver, DriverStatus
from app.models.telemetry import ShiftType, TelemetryRaw
from app.models.vehicle import Vehicle, VehicleStatus, VehicleType

__all__ = [
    # Models
    "TelemetryRaw",
    "Driver",
    "Vehicle",
    "AuditLog",
    "AlertPending",
    # Enums (exported so agents can import from one place)
    "ShiftType",
    "AgeGroup",
    "DriverStatus",
    "VehicleType",
    "VehicleStatus",
    "ActorType",
    "AlertSeverity",
    "HumanDecision",
]
