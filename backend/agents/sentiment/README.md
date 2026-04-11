# agents/sentiment

Zhicheng's agent for feedback and sentiment analysis. Runs as an independent Celery worker container.

- **agent.py**: `SentimentAgent` class inheriting from `TDAgentBase`.
- **graph.py**: Sentiment-specific LangGraph nodes.
- **tools.py**: LLM call, pgvector search, and embedding tools.
- **tasks.py**: Celery task definition for `analyse_feedback`.

**Local Verification Report: Sentiment Agent**

**Scope**  
This report documents the local verification process for the `sentiment` agent and the final successful output observed after validation.

**Local Verification Steps**

1. Start the required services:
```bash
docker compose up -d --build db redis api ingestion orchestrator sentiment_worker
```

2. Reset Redis and Postgres state, then recreate schemas:
```bash
docker compose exec -T api python scripts/clean_datastores.py
```

3. Confirm the `pgvector` extension is available:
```bash
docker compose exec -T db psql -U postgres -d tracedata -c "SELECT extname FROM pg_extension WHERE extname='vector';"
```

4. Confirm sentiment tables exist:
```bash
docker compose exec -T db psql -U postgres -d tracedata -c "\dt sentiment_schema.*"
```

5. Watch the sentiment worker logs:
```bash
docker compose logs -f sentiment_worker
```

6. Push the first `driver_feedback` event:
```bash
docker compose exec -T api python - <<'PY'
import asyncio
import redis.asyncio as redis
from pydantic import TypeAdapter
from common.models.events import TelemetryPacket

packet = {
    "batch_id": "BAT-SENT-001",
    "ping_type": "medium_speed",
    "source": "driver_app",
    "is_emergency": False,
    "event": {
        "event_id": "EVT-SENT-001",
        "device_event_id": "DEV-SENT-001",
        "trip_id": "TRP-SENT-001",
        "truck_id": "TK-SENT-001",
        "driver_id": "DRV-SENT-001",
        "event_type": "driver_feedback",
        "category": "driver_feedback",
        "priority": "medium",
        "timestamp": "2026-04-11T09:00:00Z",
        "offset_seconds": 300,
        "trip_meter_km": None,
        "odometer_km": None,
        "location": None,
        "schema_version": "event_v1",
        "details": {
            "trip_rating": 2,
            "message": "I feel really tired after today's route, and the delays made me more frustrated than usual.",
            "fatigue_self_report": "high"
        },
    },
}

async def main():
    client = redis.from_url("redis://redis:6379/0", decode_responses=True)
    try:
        ta = TypeAdapter(TelemetryPacket)
        model = ta.validate_python(packet)
        await client.zadd("telemetry:TK-SENT-001:buffer", {model.model_dump_json(): 0})
        print("pushed")
    finally:
        await client.aclose()

asyncio.run(main())
PY
```

7. Push the second `driver_feedback` event for the same driver to validate historical window stats and trend logic:
```bash
docker compose exec -T api python - <<'PY'
import asyncio
import redis.asyncio as redis
from pydantic import TypeAdapter
from common.models.events import TelemetryPacket

packet = {
    "batch_id": "BAT-SENT-002",
    "ping_type": "medium_speed",
    "source": "driver_app",
    "is_emergency": False,
    "event": {
        "event_id": "EVT-SENT-002",
        "device_event_id": "DEV-SENT-002",
        "trip_id": "TRP-SENT-002",
        "truck_id": "TK-SENT-001",
        "driver_id": "DRV-SENT-001",
        "event_type": "driver_feedback",
        "category": "driver_feedback",
        "priority": "medium",
        "timestamp": "2026-04-11T10:30:00Z",
        "offset_seconds": 320,
        "trip_meter_km": None,
        "odometer_km": None,
        "location": None,
        "schema_version": "event_v1",
        "details": {
            "trip_rating": 2,
            "message": "I still feel exhausted, and today I was even more stressed and uneasy than before.",
            "fatigue_self_report": "high"
        },
    },
}

async def main():
    client = redis.from_url("redis://redis:6379/0", decode_responses=True)
    try:
        ta = TypeAdapter(TelemetryPacket)
        model = ta.validate_python(packet)
        await client.zadd("telemetry:TK-SENT-001:buffer", {model.model_dump_json(): 0})
        print("pushed")
    finally:
        await client.aclose()

asyncio.run(main())
PY
```

8. Optional: inspect the final sentiment output in Redis:
```bash
docker compose exec -T redis redis-cli GET trip:TRP-SENT-002:sentiment_output
```

**Final Successful Output**

```json
{
  "trip_id": "TRP-SENT-002",
  "agent": "sentiment",
  "status": "done",
  "final": true,
  "result": {
    "status": "success",
    "sentiment": "negative",
    "sentiment_score": 0.7384,
    "risk_level": 0.7384,
    "emotion_scores": {
      "fatigue": 0.6868,
      "anxiety": 0.6884,
      "anger": 0.6205,
      "sadness": 0.6331
    },
    "current_scores": {
      "fatigue": 0.6868,
      "anxiety": 0.6884,
      "anger": 0.6205,
      "sadness": 0.6331
    },
    "window_stats": {
      "fatigue_avg": 0.6867,
      "anxiety_avg": 0.6228,
      "anger_avg": 0.6609,
      "sadness_avg": 0.6538
    },
    "trend": {
      "fatigue": "stable",
      "anxiety": "rising",
      "anger": "stable",
      "sadness": "stable"
    },
    "dominant_emotion": "anxiety",
    "dominant_emotion_score": 0.6884,
    "explanation": "The emotional assessment indicates that you are currently experiencing high emotional risk, primarily characterized by significant fatigue and anxiety. Your feelings of exhaustion and increased stress suggest that these factors are impacting your overall well-being. While your levels of fatigue, anger, and sadness remain stable, the rising trend in anxiety is a..."
  }
}
```

**Verification Result**
- Local end-to-end verification completed successfully.
- The `sentiment` agent processed `driver_feedback` events correctly.
- Historical window statistics and trend detection were confirmed on the second event.
- Final output was written successfully with `status: "success"` and `final: true`.