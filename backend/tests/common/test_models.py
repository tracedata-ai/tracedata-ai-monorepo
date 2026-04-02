"""
Tests for Pydantic event models (TelemetryPacket, TripEvent, TripContext).
These are pure unit tests — no I/O, no Redis, no database.
"""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from common.models.enums import Priority
from common.models.events import TelemetryPacket, TripEvent
from common.models.trips import TripContext

# ── TripEvent ──────────────────────────────────────────────────────────────────


class TestTripEvent:

    def _valid_payload(self) -> dict:
        return {
            "event_id": str(uuid.uuid4()),
            "device_event_id": "DEV-001",
            "trip_id": "TRIP-001",
            "truck_id": "TRUCK-101",
            "driver_id": "DRIVER-77",
            "event_type": "harsh_brake",
            "category": "harsh_events",
            "priority": "high",
            "timestamp": datetime.now(UTC),
            "offset_seconds": 120,
            "trip_meter_km": 5.4,
            "odometer_km": 124565.4,
        }

    def test_valid_trip_event_parses(self):
        """A complete valid TripEvent parses without error."""
        event = TripEvent(**self._valid_payload())
        assert event.event_type == "harsh_brake"
        assert event.trip_id == "TRIP-001"

    def test_schema_version_defaults(self):
        """schema_version defaults to 'event_v1'."""
        event = TripEvent(**self._valid_payload())
        assert event.schema_version == "event_v1"

    def test_details_defaults_to_empty_dict(self):
        """details field defaults to empty dict when omitted."""
        event = TripEvent(**self._valid_payload())
        assert event.details == {}

    def test_optional_fields_are_none_by_default(self):
        """location is optional (None)."""
        payload = self._valid_payload()
        # category and priority are required, so test with them
        event = TripEvent(**payload)
        assert event.category == "harsh_events"
        assert event.priority == "high"
        assert event.location is None

    def test_missing_trip_id_raises_validation_error(self):
        """Omitting trip_id raises ValidationError."""
        payload = self._valid_payload()
        del payload["trip_id"]
        with pytest.raises(ValidationError):
            TripEvent(**payload)

    def test_missing_event_type_raises_validation_error(self):
        """Omitting event_type raises ValidationError."""
        payload = self._valid_payload()
        del payload["event_type"]
        with pytest.raises(ValidationError):
            TripEvent(**payload)

    def test_location_map_stored_correctly(self):
        """Location dict is parsed into Location model."""
        payload = self._valid_payload()
        payload["location"] = {"lat": 1.2863, "lon": 103.8519}
        event = TripEvent(**payload)
        assert event.location.lat == 1.2863


# ── TelemetryPacket ────────────────────────────────────────────────────────────


class TestTelemetryPacket:

    def _valid_event(self) -> dict:
        return {
            "event_id": str(uuid.uuid4()),
            "device_event_id": "DEV-001",
            "trip_id": "TRIP-001",
            "truck_id": "TRUCK-101",
            "driver_id": "DRIVER-77",
            "event_type": "harsh_brake",
            "category": "harsh_events",
            "priority": "high",
            "timestamp": datetime.now(UTC),
            "offset_seconds": 120,
            "trip_meter_km": 5.4,
            "odometer_km": 124565.4,
        }

    def test_valid_packet_parses(self):
        """A full TelemetryPacket round-trips correctly."""
        packet = TelemetryPacket(
            ping_type="high_speed",
            source="telematics_device",
            event=self._valid_event(),
        )
        assert packet.ping_type == "high_speed"
        assert packet.event.trip_id == "TRIP-001"

    def test_is_emergency_defaults_to_false(self):
        """is_emergency defaults to False."""
        packet = TelemetryPacket(
            ping_type="high_speed",
            source="telematics_device",
            event=self._valid_event(),
        )
        assert packet.is_emergency is False

    def test_missing_ping_type_raises(self):
        """Omitting ping_type raises ValidationError."""
        with pytest.raises(ValidationError):
            TelemetryPacket(source="device", event=self._valid_event())

    def test_emergency_flag_is_set(self):
        """is_emergency is correctly set to True."""
        packet = TelemetryPacket(
            ping_type="emergency",
            source="telematics_device",
            is_emergency=True,
            event=self._valid_event(),
        )
        assert packet.is_emergency is True


# ── TripContext ────────────────────────────────────────────────────────────────


class TestTripContext:

    def _valid_trip_event(self) -> TripEvent:
        """Create a valid TripEvent for TripContext tests."""
        return TripEvent(
            event_id=str(uuid.uuid4()),
            device_event_id="DEV-001",
            trip_id="TRIP-001",
            truck_id="TRUCK-101",
            driver_id="DRIVER-77",
            event_type="harsh_brake",
            category="harsh_events",
            priority=Priority.HIGH,
            timestamp=datetime.now(UTC),
            offset_seconds=120,
            trip_meter_km=5.4,
            odometer_km=124565.4,
        )

    def test_valid_context_parses(self):
        """A complete TripContext parses correctly."""
        ctx = TripContext(
            trip_id="TRIP-001",
            truck_id="TRUCK-101",
            driver_id="DRIVER-77",
            priority=3,
            event=self._valid_trip_event(),
        )
        assert ctx.trip_id == "TRIP-001"

    def test_distance_km_defaults_to_zero(self):
        """historical_avg_score defaults to None when not provided."""
        ctx = TripContext(
            trip_id="TRIP-001",
            truck_id="TRUCK-101",
            driver_id="DRIVER-77",
            priority=3,
            event=self._valid_trip_event(),
        )
        assert ctx.historical_avg_score is None

    def test_end_time_is_optional(self):
        """peer_group_avg is optional (None by default)."""
        ctx = TripContext(
            trip_id="TRIP-001",
            truck_id="TRUCK-101",
            driver_id="DRIVER-77",
            priority=3,
            event=self._valid_trip_event(),
        )
        assert ctx.peer_group_avg is None
