Events

<!-- ───────────────────────────────────────────────────────────────────────────
  SINGLE-TRIP WORKFLOW FIXTURE — replay JSON objects in order for integration tests.

  trip_id:     TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6
  truck_id:    T12345
  driver_id:   DRV-ANON-7829
  anchor:      trip start 2026-03-07T08:00:00Z (all offsets / times derive from this)

  Order: start_of_trip → smoothness windows → harsh_accel → harsh_brake →
         end_of_trip → driver_feedback
────────────────────────────────────────────────────────────────────────── -->

### App contract (same shape for prod, scripts, and tests)

Each block below is a **`TelemetryPacket`**: top-level `ping_type`, `source`, `is_emergency`, nested **`event`** (`TripEvent`), and optional top-level **`evidence`**. Ingestion validates with `TelemetryPacket.model_validate(...)`, then **`PacketTransformer`** emits a flat **`TripEvent`** for Redis / orchestrator (category may be overwritten from `EVENT_MATRIX`).

**Use this everywhere** you mean “device / app sent telemetry”: push scripts, integration tests, and fixtures. Prefer loading JSON and validating with Pydantic rather than hand-building divergent dicts.

**How to push sequences to Redis / reset DB:** [`backend/docs/workflow_testing.md`](../../backend/docs/workflow_testing.md) (`play_workflow.py`, `common/workflow_fixtures/`).

**Must match the models:**

| Field | Rule |
|--------|------|
| `event.priority` | String enum only: **`"critical"` \| `"high"` \| `"medium"` \| `"low"`** — not numeric queue scores (those are derived later). |
| `event.offset_seconds` | **Integer** seconds since trip start (use `0` or a concrete offset; avoid `null` — the model requires `int`). |
| Inner `event.batch_id` | Optional convenience; **ignored** by Pydantic if present (not stored on `TripEvent`). |
| Extra keys (e.g. `video_codec` on `evidence`) | Ignored by validation unless you add them to the model. |

---

// 1 — START OF TRIP EVENT
```
{
  "batch_id": "BAT-550e8400-e29b-41d4-a716-446655440000",
  "ping_type": "start_of_trip",
  "source": "driver_app",
  "is_emergency": false,
  "event": {
    "event_id": "EVT-6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "device_event_id": "TEL-6ba7b811-9dad-11d1-80b4-00c04fd430c8",
    "trip_id": "TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "driver_id": "DRV-ANON-7829",
    "truck_id": "T12345",
    "batch_id": "BAT-550e8400-e29b-41d4-a716-446655440000",
    "event_type": "start_of_trip",
    "category": "trip_lifecycle",
    "priority": 9,
    "timestamp": "2026-03-07T08:00:00Z",
    "offset_seconds": 0,
    "trip_meter_km": 0.0,
    "odometer_km": 180200.0,
    "location": { "lat": 1.3456, "lon": 103.8301 },
    "schema_version": "event_v1",
    "details": {
      "odometer_km": 180200.0,
      "fuel_level_litres": 45,
      "vehicle_status": "ready",
      "driver_confirmation": true,
      "intended_destination": "Port of Singapore",
      "estimated_distance_km": 78
    },
    "evidence": null
  }
}
```


// 2 — SMOOTHNESS LOG EVENT (first 10 min window)
```
{
  "batch_id": "BAT-6ba7b812-9dad-11d1-80b4-00c04fd430c8",
  "ping_type": "batch",
  "source": "telematics_device",
  "is_emergency": false,
  "event": {
    "event_id": "EVT-6ba7b813-9dad-11d1-80b4-00c04fd430c8",
    "device_event_id": "TEL-6ba7b814-9dad-11d1-80b4-00c04fd430c8",
    "trip_id": "TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "driver_id": "DRV-ANON-7829",
    "truck_id": "T12345",
    "batch_id": "BAT-6ba7b812-9dad-11d1-80b4-00c04fd430c8",
    "event_type": "smoothness_log",
    "category": "normal_operation",
    "priority": "low",
    "timestamp": "2026-03-07T08:10:00Z",
    "offset_seconds": 600,
    "trip_meter_km": 12.4,
    "odometer_km": 180212.4,
    "location": { "lat": 1.3470, "lon": 103.8340 },
    "schema_version": "event_v1",
    "details": {
      "sample_count": 600,
      "window_seconds": 600,
      "speed": {
        "mean_kmh": 74.4,
        "std_dev": 5.2,
        "max_kmh": 88.0,
        "variance": 27.04
      },
      "longitudinal": {
        "mean_accel_g": 0.02,
        "std_dev": 0.08,
        "max_decel_g": -0.15,
        "harsh_brake_count": 0,
        "harsh_accel_count": 0
      },
      "lateral": {
        "mean_lateral_g": 0.01,
        "max_lateral_g": 0.12,
        "harsh_corner_count": 0
      },
      "jerk": {
        "mean": 0.005,
        "max": 0.028,
        "std_dev": 0.004
      },
      "engine": {
        "mean_rpm": 1850,
        "max_rpm": 2200,
        "idle_seconds": 12,
        "idle_events": 1,
        "longest_idle_seconds": 10,
        "over_rev_count": 0,
        "over_rev_seconds": 0
      },
      "incident_event_ids": [],
      "raw_log_url": "s3://tracedata-sensors/T12345-batch-20260307-0810.bin"
    },
    "evidence": null
  }
}
```

// 3 — SMOOTHNESS LOG EVENT (20 min mark)
```
{
  "batch_id": "BAT-6ba7b815-9dad-11d1-80b4-00c04fd430c8",
  "ping_type": "batch",
  "source": "telematics_device",
  "is_emergency": false,
  "event": {
    "event_id": "EVT-6ba7b816-9dad-11d1-80b4-00c04fd430c8",
    "device_event_id": "TEL-6ba7b817-9dad-11d1-80b4-00c04fd430c8",
    "trip_id": "TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "driver_id": "DRV-ANON-7829",
    "truck_id": "T12345",
    "batch_id": "BAT-6ba7b815-9dad-11d1-80b4-00c04fd430c8",
    "event_type": "smoothness_log",
    "category": "normal_operation",
    "priority": "low",
    "timestamp": "2026-03-07T08:20:00Z",
    "offset_seconds": 1200,
    "trip_meter_km": 24.8,
    "odometer_km": 180224.8,
    "location": { "lat": 1.3485, "lon": 103.8380 },
    "schema_version": "event_v1",
    "details": {
      "sample_count": 600,
      "window_seconds": 600,
      "speed": {
        "mean_kmh": 72.3,
        "std_dev": 8.1,
        "max_kmh": 94.0,
        "variance": 65.61
      },
      "longitudinal": {
        "mean_accel_g": 0.04,
        "std_dev": 0.12,
        "max_decel_g": -0.31,
        "harsh_brake_count": 0,
        "harsh_accel_count": 0
      },
      "lateral": {
        "mean_lateral_g": 0.02,
        "max_lateral_g": 0.18,
        "harsh_corner_count": 0
      },
      "jerk": {
        "mean": 0.008,
        "max": 0.041,
        "std_dev": 0.006
      },
      "engine": {
        "mean_rpm": 1820,
        "max_rpm": 2340,
        "idle_seconds": 45,
        "idle_events": 1,
        "longest_idle_seconds": 38,
        "over_rev_count": 0,
        "over_rev_seconds": 0
      },
      "incident_event_ids": [],
      "raw_log_url": "s3://tracedata-sensors/T12345-batch-20260307-0820.bin"
    },
    "evidence": null
  }
}
```

// 4 — HARSH ACCELERATION EVENT (mid-trip)
```
{
  "batch_id": "BAT-7ca7b800-9dad-11d1-80b4-00c04fd430c8",
  "ping_type": "high_speed",
  "source": "telematics_device",
  "is_emergency": false,
  "event": {
    "event_id": "EVT-7ca7b801-9dad-11d1-80b4-00c04fd430c8",
    "device_event_id": "TEL-7ca7b802-9dad-11d1-80b4-00c04fd430c8",
    "trip_id": "TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "driver_id": "DRV-ANON-7829",
    "truck_id": "T12345",
    "batch_id": "BAT-7ca7b800-9dad-11d1-80b4-00c04fd430c8",
    "event_type": "hard_accel",
    "category": "harsh_events",
    "priority": "high",
    "timestamp": "2026-03-07T09:35:00Z",
    "offset_seconds": 5700,
    "trip_meter_km": 56.1,
    "odometer_km": 180256.1,
    "location": { "lat": 1.3100, "lon": 103.8600 },
    "schema_version": "event_v1",
    "details": {
      "g_force_x": 0.82,
      "speed_kmh": 42,
      "duration_seconds": 3,
      "confidence": 0.91
    },
    "evidence": null
  },
  "evidence": {
    "video_url": "s3://tracedata-clips/BAT-7ca7b800-9dad-11d1-80b4-00c04fd430c8.mp4",
    "video_duration_seconds": 30,
    "capture_offset_seconds": -15,
    "video_codec": "h264",
    "video_resolution": "1280x720"
  }
}
```

// 5 — HARSH BRAKE EVENT (~7 min after harsh accel on same trip)
```
{
  "batch_id": "BAT-7ca7b803-9dad-11d1-80b4-00c04fd430c8",
  "ping_type": "high_speed",
  "source": "telematics_device",
  "is_emergency": false,
  "event": {
    "event_id": "EVT-7ca7b804-9dad-11d1-80b4-00c04fd430c8",
    "device_event_id": "TEL-7ca7b805-9dad-11d1-80b4-00c04fd430c8",
    "trip_id": "TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "driver_id": "DRV-ANON-7829",
    "truck_id": "T12345",
    "batch_id": "BAT-7ca7b803-9dad-11d1-80b4-00c04fd430c8",
    "event_type": "harsh_brake",
    "category": "harsh_events",
    "priority": "high",
    "timestamp": "2026-03-07T09:42:18Z",
    "offset_seconds": 6138,
    "trip_meter_km": 58.2,
    "odometer_km": 180258.2,
    "location": { "lat": 1.3112, "lon": 103.8610 },
    "schema_version": "event_v1",
    "details": {
      "g_force_x": -0.82,
      "speed_kmh": 42,
      "duration_seconds": 3,
      "confidence": 0.91
    },
    "evidence": null
  },
  "evidence": {
    "video_url": "s3://tracedata-clips/BAT-7ca7b803-9dad-11d1-80b4-00c04fd430c8.mp4",
    "video_duration_seconds": 30,
    "capture_offset_seconds": -15,
    "video_codec": "h264",
    "video_resolution": "1280x720"
  }
}
```

// 6 — END OF TRIP EVENT
```
{
  "batch_id": "BAT-6ba7b818-9dad-11d1-80b4-00c04fd430c8",
  "ping_type": "end_of_trip",
  "source": "driver_app",
  "is_emergency": false,
  "event": {
    "event_id": "EVT-6ba7b819-9dad-11d1-80b4-00c04fd430c8",
    "device_event_id": "TEL-6ba7b81a-9dad-11d1-80b4-00c04fd430c8",
    "trip_id": "TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "driver_id": "DRV-ANON-7829",
    "truck_id": "T12345",
    "batch_id": "BAT-6ba7b818-9dad-11d1-80b4-00c04fd430c8",
    "event_type": "end_of_trip",
    "category": "trip_lifecycle",
    "priority": "low",
    "timestamp": "2026-03-07T10:45:32Z",
    "offset_seconds": 9932,
    "trip_meter_km": 78.3,
    "odometer_km": 180278.3,
    "location": { "lat": 1.2900, "lon": 103.8500 },
    "schema_version": "event_v1",
    "details": {
      "duration_minutes": 165,
      "distance_km": 78.3,
      "harsh_events_total": 2,
      "speeding_events": 0,
      "safe_operation_checkpoints": 28,
      "total_checkpoints": 28,
      "safety_percentage": 92.9,
      "fuel_consumed_litres": 9.8,
      "avg_speed_kmh": 28.5,
      "max_speed_kmh": 94.0
    },
    "evidence": null
  }
}
```

// 7 — DRIVER FEEDBACK EVENT (after trip ends; offset_seconds = seconds since same trip start)
```
{
  "batch_id": "BAT-6ba7b81b-9dad-11d1-80b4-00c04fd430c8",
  "ping_type": "medium_speed",
  "source": "driver_app",
  "is_emergency": false,
  "event": {
    "event_id": "EVT-6ba7b81c-9dad-11d1-80b4-00c04fd430c8",
    "device_event_id": "TEL-6ba7b81d-9dad-11d1-80b4-00c04fd430c8",
    "trip_id": "TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "driver_id": "DRV-ANON-7829",
    "truck_id": "T12345",
    "batch_id": "BAT-6ba7b81b-9dad-11d1-80b4-00c04fd430c8",
    "event_type": "driver_feedback",
    "category": "driver_feedback",
    "priority": "medium",
    "timestamp": "2026-03-07T11:00:00Z",
    "offset_seconds": 10800,
    "trip_meter_km": null,
    "odometer_km": null,
    "location": null,
    "schema_version": "event_v1",
    "details": {
      "trip_rating": 4,
      "message": "Long trip today but manageable. Traffic on AYE was bad around 9am.",
      "fatigue_self_report": "mild"
    },
    "evidence": null
  }
}
```

