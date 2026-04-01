-- Agent-owned tables (used by Safety, Support, Sentiment repos).
-- Apply after bootstrap_e2e.sql in Docker/local full reset.

CREATE SCHEMA IF NOT EXISTS safety_schema;

CREATE TABLE IF NOT EXISTS safety_schema.harsh_events_analysis (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(80) NOT NULL,
  trip_id VARCHAR(100) NOT NULL,
  event_type VARCHAR(80),
  severity VARCHAR(50),
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

CREATE SCHEMA IF NOT EXISTS sentiment_schema;

CREATE TABLE IF NOT EXISTS sentiment_schema.feedback_sentiment (
  sentiment_id SERIAL PRIMARY KEY,
  trip_id VARCHAR(80) NOT NULL,
  driver_id VARCHAR(80) NOT NULL,
  feedback_text TEXT,
  sentiment_score DOUBLE PRECISION,
  sentiment_label VARCHAR(50),
  analysis JSONB,
  created_at TIMESTAMP
);
