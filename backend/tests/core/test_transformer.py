"""
Unit tests for PacketTransformer.

Covers the bug fix in transformer.py where priority was incorrectly passed as
an integer (PRIORITY_MAP score) instead of the Priority StrEnum. These tests
act as a regression guard to prevent that from happening again.
"""

import json
from datetime import UTC, datetime

from common.config.events import EVENT_MATRIX
from common.models.enums import PingType, Priority, Source
from common.models.events import Location, TelemetryPacket, TripEvent
from core.ingestion.transformer import PacketTransformer

# ── Helpers ───────────────────────────────────────────────────────────────────


def make_packet(
    event_type: str,
    priority: Priority = Priority.LOW,
    location: Location | None = None,
) -> TelemetryPacket:
    """Build a minimal valid TelemetryPacket for transformer tests."""
    return TelemetryPacket(
        ping_type=PingType.HIGH_SPEED,
        source=Source.TELEMATICS_DEVICE,
        is_emergency=False,
        event=TripEvent(
            event_id="evt-transformer-001",
            device_event_id="dev-transformer-001",
            trip_id="trip-transformer-001",
            truck_id="TK-TEST",
            driver_id="DRV-ANON-TEST",
            event_type=event_type,
            category="test",
            priority=priority,
            timestamp=datetime.now(UTC),
            offset_seconds=60,
            trip_meter_km=5.0,
            odometer_km=100000.0,
            location=location or Location(lat=1.29, lon=103.85),
            details={},
        ),
    )


# ── Priority type regression tests ────────────────────────────────────────────


class TestTransformerPriorityType:
    """
    Regression guard for the bug where PRIORITY_MAP[event.priority.value]
    returned an integer, causing Pydantic to reject the TripEvent output.
    priority must always be a Priority StrEnum, never an int.
    """

    def test_priority_is_string_enum_not_int(self):
        """Regression: priority must be a Priority StrEnum, not an integer."""
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)

        result = transformer.transform(packet)

        assert isinstance(
            result.priority, Priority
        ), f"priority must be Priority StrEnum, got {type(result.priority)}"
        assert not isinstance(
            result.priority, int
        ), "priority must NOT be an int (was PRIORITY_MAP score before fix)"

    def test_priority_critical_is_string(self):
        """CRITICAL priority produces 'critical' string, not 0."""
        transformer = PacketTransformer()
        packet = make_packet("collision", Priority.CRITICAL)

        result = transformer.transform(packet)

        assert result.priority == Priority.CRITICAL
        assert result.priority == "critical"
        assert result.priority != 0

    def test_priority_high_is_string(self):
        """HIGH priority produces 'high' string, not 3."""
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)

        result = transformer.transform(packet)

        assert result.priority == Priority.HIGH
        assert result.priority == "high"
        assert result.priority != 3

    def test_priority_medium_is_string(self):
        """MEDIUM priority produces 'medium' string, not 6."""
        transformer = PacketTransformer()
        packet = make_packet("speeding", Priority.MEDIUM)

        result = transformer.transform(packet)

        assert result.priority == Priority.MEDIUM
        assert result.priority == "medium"
        assert result.priority != 6

    def test_priority_low_is_string(self):
        """LOW priority produces 'low' string, not 9."""
        transformer = PacketTransformer()
        packet = make_packet("end_of_trip", Priority.LOW)

        result = transformer.transform(packet)

        assert result.priority == Priority.LOW
        assert result.priority == "low"
        assert result.priority != 9

    def test_transform_does_not_raise_for_any_priority(self):
        """Transform must succeed (not raise ValidationError) for all priorities."""
        transformer = PacketTransformer()
        event_priority_pairs = [
            ("collision", Priority.CRITICAL),
            ("harsh_brake", Priority.HIGH),
            ("speeding", Priority.MEDIUM),
            ("end_of_trip", Priority.LOW),
        ]
        for event_type, priority in event_priority_pairs:
            packet = make_packet(event_type, priority)
            result = transformer.transform(packet)
            assert isinstance(
                result, TripEvent
            ), f"transform failed for {event_type}/{priority}"

    def test_priority_survives_json_roundtrip(self):
        """Priority value is preserved correctly through JSON serialisation."""
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)

        result = transformer.transform(packet)
        serialised = result.model_dump_json()
        deserialised = TripEvent(**json.loads(serialised))

        assert deserialised.priority == Priority.HIGH
        assert deserialised.priority == "high"


# ── Category from EVENT_MATRIX ────────────────────────────────────────────────


class TestTransformerCategory:
    """Transformer must use EVENT_MATRIX category, not the input category."""

    def test_category_comes_from_event_matrix(self):
        """category is always sourced from EVENT_MATRIX, not the packet."""
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)
        # Input has category="test" — should be overwritten by EVENT_MATRIX
        packet.event.category = "something_wrong"

        result = transformer.transform(packet)

        expected_category = EVENT_MATRIX["harsh_brake"].category
        assert result.category == expected_category

    def test_category_end_of_trip(self):
        """end_of_trip maps to trip_lifecycle category."""
        transformer = PacketTransformer()
        packet = make_packet("end_of_trip", Priority.LOW)

        result = transformer.transform(packet)

        assert result.category == "trip_lifecycle"

    def test_category_harsh_brake(self):
        """harsh_brake maps to harsh_events category."""
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)

        result = transformer.transform(packet)

        assert result.category == "harsh_events"

    def test_category_speeding(self):
        """speeding maps to speed_compliance category."""
        transformer = PacketTransformer()
        packet = make_packet("speeding", Priority.MEDIUM)

        result = transformer.transform(packet)

        assert result.category == "speed_compliance"


# ── Field passthrough ─────────────────────────────────────────────────────────


class TestTransformerFieldPassthrough:
    """Transformer must preserve all identity and payload fields."""

    def test_event_id_preserved(self):
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)
        packet.event.event_id = "evt-passthrough-unique"

        result = transformer.transform(packet)

        assert result.event_id == "evt-passthrough-unique"

    def test_device_event_id_preserved(self):
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)
        packet.event.device_event_id = "dev-passthrough-unique"

        result = transformer.transform(packet)

        assert result.device_event_id == "dev-passthrough-unique"

    def test_trip_id_preserved(self):
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)
        packet.event.trip_id = "trip-passthrough-unique"

        result = transformer.transform(packet)

        assert result.trip_id == "trip-passthrough-unique"

    def test_driver_id_preserved(self):
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)
        packet.event.driver_id = "DRV-ANON-PASSTHROUGH"

        result = transformer.transform(packet)

        assert result.driver_id == "DRV-ANON-PASSTHROUGH"

    def test_source_comes_from_packet_level(self):
        """source comes from TelemetryPacket, not from event."""
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)
        packet.source = Source.DRIVER_APP

        result = transformer.transform(packet)

        assert result.source == Source.DRIVER_APP

    def test_ping_type_comes_from_packet_level(self):
        """ping_type comes from TelemetryPacket, not from event."""
        transformer = PacketTransformer()
        packet = make_packet("end_of_trip", Priority.LOW)
        packet.ping_type = PingType.END_OF_TRIP

        result = transformer.transform(packet)

        assert result.ping_type == PingType.END_OF_TRIP

    def test_is_emergency_preserved(self):
        transformer = PacketTransformer()
        packet = make_packet("collision", Priority.CRITICAL)
        packet.is_emergency = True

        result = transformer.transform(packet)

        assert result.is_emergency is True

    def test_location_preserved(self):
        transformer = PacketTransformer()
        loc = Location(lat=1.29, lon=103.85)
        packet = make_packet("harsh_brake", Priority.HIGH, location=loc)

        result = transformer.transform(packet)

        assert result.location.lat == 1.29
        assert result.location.lon == 103.85

    def test_ingested_at_is_set(self):
        """ingested_at must be set by the transformer (not from input)."""
        transformer = PacketTransformer()
        before = datetime.now(UTC).replace(tzinfo=None)
        packet = make_packet("harsh_brake", Priority.HIGH)

        result = transformer.transform(packet)

        assert result.ingested_at is not None
        # transformer sets ingested_at without tzinfo (naive UTC)
        ingested = result.ingested_at.replace(tzinfo=None)
        assert ingested >= before

    def test_returns_trip_event_type(self):
        """transform always returns a TripEvent instance."""
        transformer = PacketTransformer()
        packet = make_packet("harsh_brake", Priority.HIGH)

        result = transformer.transform(packet)

        assert isinstance(result, TripEvent)
