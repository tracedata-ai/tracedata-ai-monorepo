-- Minimal schema for ingestion → orchestrator → scoring (local Docker).
DROP TABLE IF EXISTS pipeline_events CASCADE;
DROP TABLE IF EXISTS pipeline_trips CASCADE;

CREATE TABLE pipeline_trips (
  id SERIAL PRIMARY KEY,
  trip_id VARCHAR(100) UNIQUE NOT NULL,
  driver_id VARCHAR(50) NOT NULL,
  truck_id VARCHAR(50) NOT NULL,
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  duration_minutes INT,
  distance_km DOUBLE PRECISION,
  route_type VARCHAR(30),
  avg_speed_kmh DOUBLE PRECISION,
  max_speed_kmh DOUBLE PRECISION,
  fuel_consumed_litres DOUBLE PRECISION,
  total_checkpoints INT,
  safe_checkpoints INT,
  safety_percentage DOUBLE PRECISION,
  status VARCHAR(30) DEFAULT 'active',
  action_sla VARCHAR(20),
  escalated BOOLEAN DEFAULT FALSE,
  capsule_closed BOOLEAN DEFAULT FALSE,
  closed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE pipeline_events (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(36) UNIQUE NOT NULL,
  device_event_id VARCHAR(50) UNIQUE NOT NULL,
  trip_id VARCHAR(100) NOT NULL,
  truck_id VARCHAR(50) NOT NULL,
  driver_id VARCHAR(50) NOT NULL,
  event_type VARCHAR(50) NOT NULL,
  category VARCHAR(50),
  priority VARCHAR(20),
  ping_type VARCHAR(30),
  source VARCHAR(30),
  is_emergency BOOLEAN DEFAULT FALSE,
  timestamp TIMESTAMP NOT NULL,
  offset_seconds INT,
  trip_meter_km DOUBLE PRECISION,
  odometer_km DOUBLE PRECISION,
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,
  details JSONB,
  raw_payload TEXT,
  status VARCHAR(20) DEFAULT 'received',
  locked_by VARCHAR(50),
  locked_at TIMESTAMP,
  retry_count INT DEFAULT 0,
  processed_at TIMESTAMP,
  ingested_at TIMESTAMP DEFAULT NOW()
);

DROP SCHEMA IF EXISTS scoring_schema CASCADE;
CREATE SCHEMA scoring_schema;

CREATE TABLE scoring_schema.trip_scores (
  score_id SERIAL PRIMARY KEY,
  trip_id VARCHAR(80) NOT NULL UNIQUE,
  driver_id VARCHAR(80) NOT NULL,
  score DOUBLE PRECISION NOT NULL,
  score_breakdown JSONB,
  created_at TIMESTAMP
);

CREATE TABLE scoring_schema.shap_explanations (
  id SERIAL PRIMARY KEY,
  score_id INTEGER NOT NULL REFERENCES scoring_schema.trip_scores(score_id),
  trip_id VARCHAR(80) NOT NULL UNIQUE,
  explanations JSONB,
  created_at TIMESTAMP
);

CREATE TABLE scoring_schema.fairness_audit (
  id SERIAL PRIMARY KEY,
  score_id INTEGER NOT NULL REFERENCES scoring_schema.trip_scores(score_id),
  trip_id VARCHAR(80) NOT NULL UNIQUE,
  driver_id VARCHAR(80) NOT NULL,
  audit_result JSONB,
  created_at TIMESTAMP
);
