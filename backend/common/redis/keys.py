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

        # ── CACHE WARMING HELPERS (from improvement guide) ──────
        @staticmethod
        def agent_data(trip_id: str, agent: str, data_type: str) -> str:
            """
            Pre-warmed data for specific agent.

            Format: trips:{trip_id}:{agent}:{data_type}
            Examples:
              trips:TRP-123:safety:current_event
              trips:TRP-123:scoring:all_pings
            """
            return f"trips:{trip_id}:{agent}:{data_type}"

        @staticmethod
        def event_driven_cache(trip_id: str, agent: str) -> dict[str, str]:
            """Keys for event-driven agents (Safety, Support)."""
            return {
                "current_event": RedisSchema.Trip.agent_data(
                    trip_id, agent, "current_event"
                ),
                "trip_context": RedisSchema.Trip.agent_data(
                    trip_id, agent, "trip_context"
                ),
            }

        @staticmethod
        def aggregation_driven_cache(trip_id: str, agent: str) -> dict[str, str]:
            """Keys for aggregation-driven agents (Scoring, Support)."""
            if agent == "scoring":
                return {
                    "all_pings": RedisSchema.Trip.agent_data(
                        trip_id, agent, "all_pings"
                    ),
                    "historical_avg": RedisSchema.Trip.agent_data(
                        trip_id, agent, "historical_avg"
                    ),
                }
            elif agent == "support":
                return {
                    "trip_context": RedisSchema.Trip.agent_data(
                        trip_id, agent, "trip_context"
                    ),
                    "coaching_history": RedisSchema.Trip.agent_data(
                        trip_id, agent, "coaching_history"
                    ),
                }
            else:
                # Default for unknown agents
                return {
                    "all_pings": RedisSchema.Trip.agent_data(
                        trip_id, agent, "all_pings"
                    ),
                }

    class Lock:
        """Lock-related keys."""

        @staticmethod
        def trip_lock(trip_id: str) -> str:
            """Distributed lock for trip processing."""
            return f"lock:trip:{trip_id}"

        @staticmethod
        def lock_info(trip_id: str) -> str:
            """Lock metadata (locked_by, locked_at)."""
            return f"lock:info:{trip_id}"

    class AgentFlow:
        """Global Agent Flow observability keys."""

        EVENTS_CHANNEL: str = "agentflow:events"
        STATE_KEY: str = "agentflow:state:current"
        SEQ_KEY: str = "agentflow:seq"

    class Api:
        """API-level read-through cache keys for slow-changing list endpoints."""

        FLEET_TTL: int = 300        # 5 min — vehicles rarely change
        DRIVERS_TTL: int = 300      # 5 min — driver roster rarely changes
        MAINTENANCE_TTL: int = 120  # 2 min — work orders update more often
        TRIPS_TTL: int = 60         # 1 min — active trips change status
        ISSUES_TTL: int = 300       # 5 min — issues are append-only
        SAFETY_TTL: int = 300       # 5 min — historical, append-only

        @staticmethod
        def fleet_list(tenant_id: str, skip: int, limit: int) -> str:
            return f"td:api:fleet:list:{tenant_id}:{skip}:{limit}"

        @staticmethod
        def drivers_list(tenant_id: str, skip: int, limit: int) -> str:
            return f"td:api:drivers:list:{tenant_id}:{skip}:{limit}"

        @staticmethod
        def maintenance_list(vehicle_id: str, skip: int, limit: int) -> str:
            return f"td:api:maintenance:list:{vehicle_id}:{skip}:{limit}"

        @staticmethod
        def trips_list(tenant_id: str, status: str, skip: int, limit: int) -> str:
            return f"td:api:trips:list:{tenant_id}:{status}:{skip}:{limit}"

        @staticmethod
        def issues_list(tenant_id: str, trip_id: str, skip: int, limit: int) -> str:
            return f"td:api:issues:list:{tenant_id}:{trip_id}:{skip}:{limit}"

        @staticmethod
        def safety_list(skip: int, limit: int) -> str:
            return f"td:api:safety:list:{skip}:{limit}"
