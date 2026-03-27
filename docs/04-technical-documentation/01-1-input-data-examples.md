```py
from pydantic import BaseModel
from .enums import Priority, AgentName, Source, PingType


# ── RAW DEVICE PAYLOADS ──────────────────────────────────


class Location(BaseModel):
    """GPS coordinates of the event."""

    lat: float
    lon: float


class TelemetryEvent(BaseModel):
    """
    Generic event schema for all telematics device events.
    details field is flexible — shape depends on event_type.

    Spatio-temporal anchor fields:
      offset_seconds  → when in the trip (time)
      trip_meter_km   → where in the trip (distance)
      odometer_km     → absolute vehicle lifetime distance
    """

    event_id:        str
    device_event_id: str
    trip_id:         str
    driver_id:       str
    truck_id:        str
    event_type:      str
    category:        str
    priority:        str
    timestamp:       str
    schema_version:  str = "event_v1"

    # spatio-temporal anchor — present on all device pings
    # None for driver app events (app does not have device fields)
    offset_seconds:  int   | None = None
    trip_meter_km:   float | None = None
    odometer_km:     float | None = None

    location:        Location | None = None
    details:         dict = {}


class Evidence(BaseModel):
    """
    Optional evidence attached to an event.
    Populated when device uploads media to S3.

    Two evidence tiers:

    Harsh Event Dashcam Clip (harsh_brake, hard_accel, harsh_corner):
      Device is always recording. On harsh event detection, a 66-second
      clip is saved: 15 seconds before + 15 seconds after the event.
      For fleet manager reference only — never processed by ML models.
      Fields: video_url, video_duration_seconds, capture_offset_seconds,
              video_codec, video_resolution

    Emergency Evidence Bundle (collision, rollover, driver_sos):
      Full evidence package — dashcam clip + cabin voice + sensor dump.
      Fields: all of the above + voice_url + sensor_dump_url
    """

    # dashcam — present on ALL harsh events and emergencies
    video_url:              str | None = None
    video_duration_seconds: int        = 30      # fixed: 15s before + 15s after
    capture_offset_seconds: int        = -15     # clip starts 15s before detection
    video_codec:            str        = "h264"
    video_resolution:       str        = "1280x720"

    # voice + sensor — emergency events only
    voice_url:              str | None = None
    voice_duration_seconds: int | None = None
    sensor_dump_url:        str | None = None
    sensor_dump_size_bytes: int | None = None


class TelemetryPacket(BaseModel):
    """
    Full raw payload arriving from the telematics device or driver app.
    This is what gets written to the Redis telemetry buffer.
    ping_type and source are stamped by the sender.
    """

    batch_id:     str
    ping_type:    PingType
    source:       Source = Source.DEVICE
    is_emergency: bool   = False
    event:        TelemetryEvent
    evidence:     Evidence | None = None


# ── PROCESSED EVENT ──────────────────────────────────────


class TripEvent(BaseModel):
    """
    Cleaned, flat event produced by the Ingestion Tool.
    This is what the Orchestrator and agents work with.

    Preserves spatio-temporal anchor from TelemetryEvent
    for distance normalisation in fairness scoring.
    """

    batch_id:      str
    trip_id:       str
    driver_id:     str
    truck_id:      str
    timestamp:     str
    event_type:    str
    category:      str
    priority:      Priority
    is_emergency:  bool
    ping_type:     PingType  # routing decisions
    source:        Source    # audit trail

    # spatio-temporal anchor — preserved from TelemetryEvent
    offset_seconds: int   | None = None
    trip_meter_km:  float | None = None
    odometer_km:    float | None = None

    location:       Location | None = None
    details:        dict = {}
    evidence:       Evidence | None = None


# ── TRIP CONTEXT ─────────────────────────────────────────


class TripContext(BaseModel):
    """
    Written to Redis by Orchestrator at job start.
    Every agent hydrates from this on task pickup.
    """

    trip_id:   str
    driver_id: str
    truck_id:  str
    priority:  Priority
    event:     TripEvent


# ── AGENT RESULTS ────────────────────────────────────────


class SafetyResult(BaseModel):
    """Output contract for the Safety Agent."""

    trip_id:               str
    agent:                 AgentName
    score:                 float
    flags:                 list[str]
    requires_human_review: bool


class CompletionEvent(BaseModel):
    """
    Published to Redis Pub/Sub when an agent finishes.
    Orchestrator listens for these to advance the workflow.
    """

    trip_id: str
    agent:   AgentName
    status:  str
    final:   bool = False
```

```py
from pydantic import BaseModel, ConfigDict


class EventConfig(BaseModel):
    """
    Configuration for a single event type.
    Frozen — values cannot change at runtime.

    ml_weight:
      positive  → penalty contribution to driver score
      negative  → reward bonus (e.g. smoothness_log = -0.2)
      None      → not scored (driver feedback, lifecycle events)

    has_dashcam_evidence:
      True  → device saves 66s dashcam clip on detection
               (15s before + 15s after)
      False → no clip saved for this event type
    """

    model_config = ConfigDict(frozen=True)

    category:              str
    priority:              str
    ml_weight:             float | None = None
    has_dashcam_evidence:  bool         = False


# ── EVENT MATRIX ─────────────────────────────────────────
# Single source of truth for event routing, ML weights,
# and dashcam evidence flags.
# Ingestion Tool validates all incoming events against this.
# Orchestrator reads category to decide agent dispatch.
# Scoring Agent reads ml_weight in Sprint 3.

EVENT_MATRIX: dict[str, EventConfig] = {

    # DEVICE EVENTS — safety critical
    # dashcam evidence: collision and rollover carry full bundle
    # (video + voice + sensor dump via Emergency Ping)
    "collision":       EventConfig(category="critical",         priority="critical", ml_weight=1.0,  has_dashcam_evidence=True),
    "rollover":        EventConfig(category="critical",         priority="critical", ml_weight=1.0,  has_dashcam_evidence=True),
    "vehicle_offline": EventConfig(category="critical",         priority="high",     ml_weight=0.3,  has_dashcam_evidence=False),

    # DEVICE EVENTS — harsh driving
    # dashcam evidence: device always recording, clip saved on detection
    # 30 seconds (15s before + 15s after) — fleet manager reference only
    "harsh_brake":     EventConfig(category="harsh_events",     priority="high",     ml_weight=0.7,  has_dashcam_evidence=True),
    "hard_accel":      EventConfig(category="harsh_events",     priority="high",     ml_weight=0.7,  has_dashcam_evidence=True),
    "harsh_corner":    EventConfig(category="harsh_events",     priority="high",     ml_weight=0.6,  has_dashcam_evidence=True),

    # DEVICE EVENTS — compliance
    "speeding":        EventConfig(category="speed_compliance",  priority="medium",   ml_weight=0.5,  has_dashcam_evidence=False),

    # DEVICE EVENTS — efficiency
    "excessive_idle":  EventConfig(category="idle_fuel",         priority="low",      ml_weight=0.2,  has_dashcam_evidence=False),

    # DEVICE EVENTS — positive behaviour
    # smoothness_log carries negative ml_weight — reward bonus not penalty
    "smoothness_log":  EventConfig(category="normal_operation",  priority="low",      ml_weight=-0.2, has_dashcam_evidence=False),
    "normal_operation":EventConfig(category="normal_operation",  priority="low",      ml_weight=0.0,  has_dashcam_evidence=False),

    # DEVICE EVENTS — trip lifecycle
    "start_of_trip":   EventConfig(category="trip_lifecycle",    priority="low",      ml_weight=None, has_dashcam_evidence=False),
    "end_of_trip":     EventConfig(category="trip_lifecycle",    priority="low",      ml_weight=None, has_dashcam_evidence=False),

    # DRIVER GENERATED EVENTS
    # ml_weight=None — driver feedback does not feed XGBoost score
    # has_dashcam_evidence=False — driver app has no dashcam access
    "driver_sos":      EventConfig(category="critical",          priority="critical", ml_weight=None, has_dashcam_evidence=False),
    "driver_dispute":  EventConfig(category="driver_feedback",   priority="high",     ml_weight=None, has_dashcam_evidence=False),
    "driver_complaint":EventConfig(category="driver_feedback",   priority="high",     ml_weight=None, has_dashcam_evidence=False),
    "driver_feedback": EventConfig(category="driver_feedback",   priority="medium",   ml_weight=None, has_dashcam_evidence=False),
    "driver_comment":  EventConfig(category="driver_feedback",   priority="low",      ml_weight=None, has_dashcam_evidence=False),
}


# ── THRESHOLDS ───────────────────────────────────────────
# Externalised operational thresholds for device events.
# Ingestion Tool cross-checks event details against these.
# Configurable without firmware updates or code redeployment.

THRESHOLDS: dict[str, dict] = {

    "idle": {
        # below acceptable  → no flag, normal operation
        # warning zone      → flagged for review, no event fired
        # above excessive   → excessive_idle event triggered
        "acceptable_seconds":        120,
        "warning_seconds":           300,
        "excessive_seconds":         300,
    },

    "rpm": {
        # normal cruising range for trucks
        # over_rev must be sustained for duration to count
        "normal_max":                1800,
        "acceptable_max":            2500,
        "over_rev_threshold":        2500,
        "over_rev_duration_seconds": 5,
    },

    "acceleration": {
        # G-force thresholds for harsh event detection
        "harsh_brake_g":            -0.7,   # deceleration
        "harsh_accel_g":             0.75,  # acceleration
        "harsh_corner_g":            0.8,   # lateral
    },

    "jerk": {
        # rate of change of acceleration (m/s³)
        # below smooth_threshold → counts as a smooth second
        "smooth_threshold":          0.05,
    },

    "speed": {
        # sustained over limit triggers speeding event
        "speeding_duration_seconds": 30,
    },
}


# ── SMOOTHNESS LOG DETAILS REFERENCE ─────────────────────
# Reference schema for the details block of smoothness_log events.
# details is a free dict in TelemetryEvent — this documents
# the expected structure for Scoring Agent consumption.
#
# Device computes all stats from 600 1Hz samples per 10-min window.
# Scoring Agent applies XGBoost formula using these stats.
# Raw 600-point arrays are uploaded to S3 — not included here.

SMOOTHNESS_LOG_DETAILS: dict[str, str] = {
    "sample_count":    "int   — number of 1Hz samples in window (typically 600)",
    "window_seconds":  "int   — duration of sampling window in seconds",

    "speed": {
        "mean_kmh":  "float — mean speed over window",
        "std_dev":   "float — speed consistency (lower = smoother)",
        "max_kmh":   "float — peak speed in window",
        "variance":  "float — speed variance",
    },

    "longitudinal": {
        "mean_accel_g":      "float — mean forward/braking G-force",
        "std_dev":           "float — consistency of acceleration pattern",
        "max_decel_g":       "float — hardest braking event in window",
        "harsh_brake_count": "int   — times threshold exceeded",
        "harsh_accel_count": "int   — times threshold exceeded",
    },

    "lateral": {
        "mean_lateral_g":     "float — mean cornering G-force",
        "max_lateral_g":      "float — hardest corner in window",
        "harsh_corner_count": "int   — times threshold exceeded",
    },

    "jerk": {
        "mean":    "float — mean rate of acceleration change (m/s³)",
        "max":     "float — worst sudden movement in window",
        "std_dev": "float — jerk consistency (lower = smoother)",
    },

    "engine": {
        "mean_rpm":             "float — mean engine RPM over window",
        "max_rpm":              "float — peak RPM in window",
        "idle_seconds":         "int   — total idle time in window",
        "idle_events":          "int   — number of distinct idle periods",
        "longest_idle_seconds": "int   — longest single idle period",
        "over_rev_count":       "int   — times RPM exceeded threshold",
        "over_rev_seconds":     "int   — total seconds over RPM threshold",
    },

    "incident_event_ids": "list[str] — device_event_ids of events in this window",
    "raw_log_url":        "str       — S3 link to compressed 600-point binary",
}
```

```py
from redis_client import RedisClient
from keys import RedisSchema
from models import (
    TelemetryPacket,
    Priority,
    EVENT_MATRIX,
)


# ── PRIORITY MAP ─────────────────────────────────────────
# maps priority string from EVENT_MATRIX → Priority enum score
# used for Redis Sorted Set scoring

PRIORITY_MAP: dict[str, Priority] = {
    "critical": Priority.CRITICAL,
    "high":     Priority.HIGH,
    "medium":   Priority.MEDIUM,
    "low":      Priority.LOW,
}


# ── SEED EVENTS ──────────────────────────────────────────
# Six events covering all sources, ping types, and priority levels.
# All event_types match EVENT_MATRIX keys exactly.
# All device events carry spatio-temporal anchor fields.

EVENTS: list[dict] = [

    # 1. DEVICE — Emergency Ping — collision — CRITICAL
    {
        "batch_id":     "EMERGENCY-T12345-2026-03-07-08-44-23",
        "ping_type":    "emergency",
        "source":       "telematics_device",
        "is_emergency": True,
        "event": {
            "event_id":        "EV-EMERGENCY-T12345-001",
            "device_event_id": "DEV-001",
            "trip_id":         "TRIP-T12345-2026-03-07-08:00",
            "driver_id":       "D6789",
            "truck_id":        "T12345",
            "event_type":      "collision",
            "category":        "critical",
            "priority":        "critical",
            "timestamp":       "2026-03-07T08:44:23Z",
            "offset_seconds":  2963,
            "trip_meter_km":   34.2,
            "odometer_km":     180234.2,
            "location":        {"lat": 1.2863, "lon": 104.0115},
            "details": {
                "g_force_magnitude":        2.3,
                "confidence":               0.99,
                "airbag_triggered":         True,
                "impact_direction":         "front_left",
                "speed_kmh":                48,
                "injury_severity_estimate": "moderate",
            },
        },
        # emergency bundle: dashcam clip + voice + sensor dump
        # dashcam: 30s (15s before + 15s after) — same window as harsh events
        "evidence": {
            "video_url":              "s3://tracedata-clips/EMERGENCY-T12345.mp4",
            "video_duration_seconds": 30,
            "capture_offset_seconds": -15,
            "video_codec":            "h264",
            "video_resolution":       "1280x720",
            "voice_url":              "s3://tracedata-voice/EMERGENCY-T12345.wav",
            "voice_duration_seconds": 30,
            "sensor_dump_url":        "s3://tracedata-sensors/EMERGENCY-T12345.bin",
            "sensor_dump_size_bytes": 5242880,
        },
    },

    # 2. DRIVER — SOS from driver app — CRITICAL
    {
        "batch_id":     "DRIVER-SOS-D6789-2026-03-07-09-00-00",
        "ping_type":    "emergency",
        "source":       "driver_app",
        "is_emergency": True,
        "event": {
            "event_id":        "EV-SOS-D6789-001",
            "device_event_id": "APP-001",
            "trip_id":         "TRIP-T12345-2026-03-07-08:00",
            "driver_id":       "D6789",
            "truck_id":        "T12345",
            "event_type":      "driver_sos",
            "category":        "critical",
            "priority":        "critical",
            "timestamp":       "2026-03-07T09:00:00Z",
            "offset_seconds":  None,
            "trip_meter_km":   None,
            "odometer_km":     None,
            "location":        {"lat": 1.2900, "lon": 104.0200},
            "details": {
                "message": "Need immediate assistance",
            },
        },
        "evidence": None,
    },

    # 3. DEVICE — High-Speed Send — harsh_brake — HIGH
    {
        "batch_id":     "HIGH-T12345-2026-03-07-09-10-00",
        "ping_type":    "high_speed",
        "source":       "telematics_device",
        "is_emergency": False,
        "event": {
            "event_id":        "EV-HIGH-T12345-002",
            "device_event_id": "DEV-002",
            "trip_id":         "TRIP-T12345-2026-03-07-08:00",
            "driver_id":       "D6789",
            "truck_id":        "T12345",
            "event_type":      "harsh_brake",
            "category":        "harsh_events",
            "priority":        "high",
            "timestamp":       "2026-03-07T09:10:00Z",
            "offset_seconds":  4200,
            "trip_meter_km":   48.7,
            "odometer_km":     180248.7,
            "location":        {"lat": 1.3000, "lon": 103.8500},
            "details": {
                "g_force_x":        -0.92,
                "speed_kmh":        88,
                "confidence":       0.95,
                "duration_seconds": 2,
            },
        },
        # dashcam clip: 15s before + 15s after = 30s total
        # fleet manager reference only — not processed by ML
        "evidence": {
            "video_url":              "s3://tracedata-clips/HIGH-T12345-2026-03-07-09-10-00.mp4",
            "video_duration_seconds": 30,
            "capture_offset_seconds": -15,
            "video_codec":            "h264",
            "video_resolution":       "1280x720",
        },
    },

    # 4. DRIVER — dispute — HIGH
    {
        "batch_id":     "DRIVER-DISPUTE-D6789-2026-03-07-09-30-00",
        "ping_type":    "high_speed",
        "source":       "driver_app",
        "is_emergency": False,
        "event": {
            "event_id":        "EV-DISPUTE-D6789-001",
            "device_event_id": "APP-002",
            "trip_id":         "TRIP-T12345-2026-03-07-08:00",
            "driver_id":       "D6789",
            "truck_id":        "T12345",
            "event_type":      "driver_dispute",
            "category":        "driver_feedback",
            "priority":        "high",
            "timestamp":       "2026-03-07T09:30:00Z",
            "offset_seconds":  None,
            "trip_meter_km":   None,
            "odometer_km":     None,
            "location":        None,
            "details": {
                "disputed_event_id": "EV-HIGH-T12345-002",
                "reason":            "Road conditions caused braking, not driver error",
            },
        },
        "evidence": None,
    },

    # 5. DEVICE — Medium-Speed Send — speeding — MEDIUM
    {
        "batch_id":     "MEDIUM-T12345-2026-03-07-10-00-00",
        "ping_type":    "medium_speed",
        "source":       "telematics_device",
        "is_emergency": False,
        "event": {
            "event_id":        "EV-MEDIUM-T12345-003",
            "device_event_id": "DEV-003",
            "trip_id":         "TRIP-T12345-2026-03-07-08:00",
            "driver_id":       "D6789",
            "truck_id":        "T12345",
            "event_type":      "speeding",
            "category":        "speed_compliance",
            "priority":        "medium",
            "timestamp":       "2026-03-07T10:00:00Z",
            "offset_seconds":  7200,
            "trip_meter_km":   62.4,
            "odometer_km":     180262.4,
            "location":        {"lat": 1.3200, "lon": 103.8700},
            "details": {
                "speed_kmh":        112,
                "speed_limit_kmh":  90,
                "duration_seconds": 45,
                "confidence":       0.97,
            },
        },
        "evidence": None,
    },

    # 6. DEVICE — 10-Min Batch Ping — smoothness_log — LOW
    {
        "batch_id":     "BATCH-T12345-2026-03-07-10-10-00",
        "ping_type":    "batch",
        "source":       "telematics_device",
        "is_emergency": False,
        "event": {
            "event_id":        "EV-SMOOTH-T12345-001",
            "device_event_id": "DEV-004",
            "trip_id":         "TRIP-T12345-2026-03-07-08:00",
            "driver_id":       "D6789",
            "truck_id":        "T12345",
            "event_type":      "smoothness_log",
            "category":        "normal_operation",
            "priority":        "low",
            "timestamp":       "2026-03-07T10:10:00Z",
            "offset_seconds":  7800,
            "trip_meter_km":   68.1,
            "odometer_km":     180268.1,
            "location":        {"lat": 1.3250, "lon": 103.8750},
            "details": {
                "sample_count":   600,
                "window_seconds": 600,
                "speed": {
                    "mean_kmh": 72.3,
                    "std_dev":  8.1,
                    "max_kmh":  94.0,
                    "variance": 65.6,
                },
                "longitudinal": {
                    "mean_accel_g":      0.04,
                    "std_dev":           0.12,
                    "max_decel_g":      -0.31,
                    "harsh_brake_count": 0,
                    "harsh_accel_count": 0,
                },
                "lateral": {
                    "mean_lateral_g":     0.02,
                    "max_lateral_g":      0.18,
                    "harsh_corner_count": 0,
                },
                "jerk": {
                    "mean":    0.008,
                    "max":     0.041,
                    "std_dev": 0.006,
                },
                "engine": {
                    "mean_rpm":             1820,
                    "max_rpm":              2340,
                    "idle_seconds":         45,
                    "idle_events":          1,
                    "longest_idle_seconds": 38,
                    "over_rev_count":       0,
                    "over_rev_seconds":     0,
                },
                "incident_event_ids": ["DEV-002", "DEV-003"],
                "raw_log_url": "s3://tracedata-sensors/T12345-batch-001.bin",
            },
        },
        "evidence": None,
    },

]


def seed_events(client: RedisClient) -> None:
    """
    Validates each event as a TelemetryPacket and pushes
    to the Redis priority buffer (Sorted Set).
    Priority score read from EVENT_MATRIX — not from raw event string.
    Higher priority events will be popped first by Ingestion Tool.
    """
    for raw in EVENTS:
        packet     = TelemetryPacket(**raw)
        device_id  = packet.event.truck_id
        key        = RedisSchema.Telemetry.buffer(device_id)

        # read priority from EVENT_MATRIX — source of truth
        # overrides whatever the device stamped
        event_type     = packet.event.event_type
        priority_str   = EVENT_MATRIX[event_type].priority
        priority_score = int(PRIORITY_MAP[priority_str])

        # zadd — lower score = higher priority = popped first by zpopmin
        client.push_to_buffer(key, packet.model_dump_json(), priority_score)

        print(f"  seeded → {packet.batch_id}")
        print(f"           source:     {packet.source.value}")
        print(f"           event_type: {event_type} [{priority_str}]")
        print(f"           score:      {priority_score}\n")


if __name__ == "__main__":
    print(">>> Seeding events into Redis priority buffer...\n")

    with RedisClient() as r:
        seed_events(r)

    print(">>> Done. Check Redis Insight → telemetry:T12345:buffer")
```