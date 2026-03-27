import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventORM(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(36), unique=True)
    device_event_id: Mapped[str] = mapped_column(String(50), unique=True)
    trip_id: Mapped[str] = mapped_column(String(100))
    truck_id: Mapped[str] = mapped_column(String(50))
    driver_id: Mapped[str] = mapped_column(String(50))
    event_type: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(20))
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)
    offset_seconds: Mapped[int] = mapped_column(Integer)
    trip_meter_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    odometer_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Lifecycle Status
    status: Mapped[str] = mapped_column(String(20), default="received")
    locked_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    locked_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    processed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
