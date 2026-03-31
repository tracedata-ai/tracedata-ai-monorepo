class RedisSchema:
    """Central authority for all Redis key patterns and queue names."""

    class Telemetry:
        DLQ_TTL: int = 172800  # 48 hours
        DEBUG_TTL: int = 3600  # 1 hour — for debugging/observability only

        @staticmethod
        def buffer(truck_id: str) -> str:
            """Stage 1 — raw TelemetryPacket (consumed)."""
            return f"telemetry:{truck_id}:buffer"

        @staticmethod
        def processed(truck_id: str) -> str:
            """Stage 2 — clean TripEvent (consumed)."""
            return f"telemetry:{truck_id}:processed"

        @staticmethod
        def rejected(truck_id: str) -> str:
            """Dead Letter Queue (48h TTL)."""
            return f"telemetry:{truck_id}:rejected"

        @staticmethod
        def debug_buffer(truck_id: str) -> str:
            """DEBUG COPY — raw TelemetryPacket (1h TTL, for observability)."""
            return f"debug:telemetry:{truck_id}:buffer"

        @staticmethod
        def debug_processed(truck_id: str) -> str:
            """DEBUG COPY — clean TripEvent (1h TTL, for observability)."""
            return f"debug:telemetry:{truck_id}:processed"

    class Trip:
        CONTEXT_TTL_HIGH: int = 172800  # 48 hours — CRITICAL/HIGH
        CONTEXT_TTL_LOW: int = 600  # 10 minutes — MEDIUM/LOW
        OUTPUT_TTL: int = 600  # 10 minutes
        EVENT_TTL: int = 600  # 10 minutes

        @staticmethod
        def context(trip_id: str) -> str:
            return f"trip:{trip_id}:context"

        @staticmethod
        def smoothness_logs(trip_id: str) -> str:
            return f"trip:{trip_id}:smoothness_logs"

        @staticmethod
        def output(trip_id: str, agent_name: str) -> str:
            return f"trip:{trip_id}:{agent_name}_output"

        @staticmethod
        def events_channel(trip_id: str) -> str:
            return f"trip:{trip_id}:events"
