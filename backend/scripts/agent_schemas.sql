-- Agent-owned tables (used by Safety, Support, Sentiment repos).
-- Apply after bootstrap_e2e.sql in Docker/local full reset.

CREATE SCHEMA IF NOT EXISTS safety_schema;

CREATE TABLE IF NOT EXISTS safety_schema.harsh_events_analysis (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(80) NOT NULL,
  trip_id VARCHAR(100) NOT NULL,
  event_type VARCHAR(80),
  severity VARCHAR(50),
  event_timestamp TIMESTAMP,
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,
  traffic_conditions TEXT,
  weather_conditions TEXT,
  analysis JSONB,
  created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS safety_schema.safety_decisions (
  decision_id SERIAL PRIMARY KEY,
  event_id VARCHAR(80),
  trip_id VARCHAR(100) NOT NULL,
  decision VARCHAR(255),
  action VARCHAR(255),
  reason TEXT,
  recommended_action TEXT,
  created_at TIMESTAMP
);

CREATE SCHEMA IF NOT EXISTS coaching_schema;

CREATE TABLE IF NOT EXISTS coaching_schema.coaching (
  coaching_id SERIAL PRIMARY KEY,
  trip_id VARCHAR(80) NOT NULL,
  driver_id VARCHAR(80) NOT NULL,
  coaching_category VARCHAR(80),
  message TEXT,
  priority VARCHAR(20),
  created_at TIMESTAMP
);

CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS sentiment_schema;

CREATE TABLE IF NOT EXISTS sentiment_schema.feedback_sentiment (
  sentiment_id SERIAL PRIMARY KEY,
  trip_id VARCHAR(80) NOT NULL,
  driver_id VARCHAR(80) NOT NULL,
  event_id VARCHAR(80),
  device_event_id VARCHAR(80),
  submission_timestamp TIMESTAMP,
  feedback_text TEXT,
  feedback_embedding vector(1536),
  sentiment_score DOUBLE PRECISION,
  sentiment_label VARCHAR(50),
  analysis JSONB,
  created_at TIMESTAMP
);

ALTER TABLE sentiment_schema.feedback_sentiment
  ADD COLUMN IF NOT EXISTS event_id VARCHAR(80),
  ADD COLUMN IF NOT EXISTS device_event_id VARCHAR(80),
  ADD COLUMN IF NOT EXISTS submission_timestamp TIMESTAMP,
  ADD COLUMN IF NOT EXISTS feedback_embedding vector(1536);

CREATE TABLE IF NOT EXISTS sentiment_schema.emotion_anchor_embeddings (
  anchor_key VARCHAR(80) PRIMARY KEY,
  emotion VARCHAR(50) NOT NULL,
  anchor_text TEXT NOT NULL,
  embedding vector(1536) NOT NULL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_feedback_sentiment_driver_submission_ts
  ON sentiment_schema.feedback_sentiment (driver_id, submission_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_emotion_anchor_embeddings_emotion
  ON sentiment_schema.emotion_anchor_embeddings (emotion);
