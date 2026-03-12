# ADR 005: High-Resolution Telemetry Storage with TimescaleDB

## Context
TraceData AI receives high-frequency telemetry (1-10Hz) from thousands of vehicles. Each trip can generate tens of thousands of data points (GPS, Speed, Brake Pressure, G-Forces). Storing this in standard relational tables will lead to index bloat and degraded performance.

## Decision
We will use **TimescaleDB** (a PostgreSQL extension) to store all raw telemetry.

### 1. Hypertable Structure
We will define a `telemetry_events` hypertable partitioned by `time` (7-day chunks) and `trip_id`.

```sql
CREATE TABLE telemetry_events (
    time TIMESTAMPTZ NOT NULL,
    trip_id UUID NOT NULL,
    vehicle_id VARCHAR(50) NOT NULL,
    speed FLOAT,
    brake_pressure FLOAT,
    throttle_pos FLOAT,
    lat FLOAT,
    lng FLOAT,
    g_force_x FLOAT,
    g_force_y FLOAT
);

-- Convert to hypertable
SELECT create_hypertable('telemetry_events', 'time');
```

### 2. Retention & Compression
- **Raw Data**: Retain at full frequency for 30 days for forensic audits.
- **Compression**: Enable TimescaleDB native compression after 7 days, grouping by `trip_id` and `vehicle_id` for column-wise storage.
- **Aggregation**: Use **Continuous Aggregates** to pre-calculate 1-minute summaries for overview dashboards.

## Alternatives Considered
- **InfluxDB**: Excellent performance but adds another operational silo and lacks full SQL join capabilities with our `Booking` and `Fleet` schemas.
- **Standard S3/Parquet**: Good for deep analytics but slow for real-time frontend retrieval of specific trip segments.

## Tradeoffs
✅ **Pros**: Single database (Postgres), standard SQL interface, optimized for time-series, excellent compression.
❌ **Cons**: Requires TimescaleDB extension (managed service or custom Docker image).
