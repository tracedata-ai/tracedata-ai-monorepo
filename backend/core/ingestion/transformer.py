from common.config.events import EVENT_MATRIX
from common.models.events import TelemetryPacket, TripEvent


class PacketTransformer:
    """
    Transforms raw TelemetryPacket into validated, enriched TripEvent.
    Applies authoritative EVENT_MATRIX governance for category and priority.
    """

    @staticmethod
    def to_trip_event(packet: TelemetryPacket) -> TripEvent:
        """
        Transforms and enriches the event.
        Category and Priority are OVERRIDDEN by the EVENT_MATRIX.
        """
        raw_event = packet.event
        matrix_config = EVENT_MATRIX.get(raw_event.event_type)

        if not matrix_config:
            raise ValueError(f"Event type '{raw_event.event_type}' not in MATRIX")

        # Create enriched TripEvent
        return TripEvent(
            event_id=raw_event.event_id,
            device_event_id=raw_event.device_event_id,
            trip_id=raw_event.trip_id,
            truck_id=raw_event.truck_id,
            driver_id=raw_event.driver_id,
            event_type=raw_event.event_type,
            category=matrix_config.category,  # Matrix Override
            priority=matrix_config.priority,  # Matrix Override
            timestamp=raw_event.timestamp,
            offset_seconds=raw_event.offset_seconds,
            trip_meter_km=raw_event.trip_meter_km,
            odometer_km=raw_event.odometer_km,
            location=raw_event.location,
            schema_version=raw_event.schema_version,
            details=raw_event.details,
        )
