"""
Tests for Pydantic event models (TelemetryPacket, TripEvent, TripContext).
These are pure unit tests — no I/O, no Redis, no database.
"""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

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
        """category, priority, and location are optional (None)."""
        event = TripEvent(**self._valid_payload())
        assert event.category is None
        assert event.priority is None
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
        """Location dict is stored as-is."""
        payload = self._valid_payload()
        payload["location"] = {"lat": 1.2863, "lon": 103.8519}
        event = TripEvent(**payload)
        assert event.location["lat"] == 1.2863


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
            ping_type="normal",
            source="device",
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
            source="device",
            is_emergency=True,
            event=self._valid_event(),
        )
        assert packet.is_emergency is True


# ── TripContext ────────────────────────────────────────────────────────────────


class TestTripContext:

    def test_valid_context_parses(self):
        """A complete TripContext parses correctly."""
        ctx = TripContext(
            trip_id="TRIP-001",
            truck_id="TRUCK-101",
            driver_id="DRIVER-77",
            status="active",
            start_time=datetime.now(UTC),
        )
        assert ctx.trip_id == "TRIP-001"

    def test_distance_km_defaults_to_zero(self):
        """distance_km defaults to 0.0 when not provided."""
        ctx = TripContext(
            trip_id="TRIP-001",
            truck_id="TRUCK-101",
            driver_id="DRIVER-77",
            status="active",
            start_time=datetime.now(UTC),
        )
        assert ctx.distance_km == 0.0

    def test_end_time_is_optional(self):
        """end_time is None by default (trip still in progress)."""
        ctx = TripContext(
            trip_id="TRIP-001",
            truck_id="TRUCK-101",
            driver_id="DRIVER-77",
            status="active",
            start_time=datetime.now(UTC),
        )
        assert ctx.end_time is None
