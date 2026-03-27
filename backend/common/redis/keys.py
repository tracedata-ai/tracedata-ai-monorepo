class RedisSchema:
    """Central authority for all Redis key patterns and queue names."""
    
    # ── Queues (Lists) ──────────────────────────────────────────────────────
    INGESTION_QUEUE = "td:ingestion:events"
    ORCHESTRATOR_QUEUE = "td:orchestrator:events"
    
    # Agent Queues
    SAFETY_QUEUE = "td:agent:safety"
    SCORING_QUEUE = "td:agent:scoring"
    SUPPORT_QUEUE = "td:agent:support"
    SENTIMENT_QUEUE = "td:agent:sentiment"
    
    # ── State (Hashes/Strings) ──────────────────────────────────────────────
    @staticmethod
    def trip_context(trip_id: str) -> str:
        return f"td:trip:{trip_id}:context"
    
    @staticmethod
    def agent_lock(agent_name: str, trip_id: str) -> str:
        return f"td:lock:{agent_name}:{trip_id}"

    # ── TTLs (Seconds) ──────────────────────────────────────────────────────
    CONTEXT_TTL = 3600  # 1 hour
    LOCK_TTL = 30       # 30 seconds
