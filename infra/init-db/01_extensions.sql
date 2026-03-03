-- ─────────────────────────────────────────────────────────────────────────────
--  TraceData.ai — PostgreSQL First-Boot Initialisation
--
--  This script runs ONCE via docker-entrypoint-initdb.d on the first container
--  start. It will NOT re-run if the postgres_data volume already exists.
--
--  WHY HERE AND NOT IN CODE:
--    CREATE EXTENSION requires superuser. Running it here guarantees the
--    extension is available before Alembic migrations run and before the
--    backend application connects for the first time. This prevents the
--    "type 'vector' does not exist" error that appears when Alembic tries to
--    create the TelemetryRaw.location column before the extension is loaded.
-- ─────────────────────────────────────────────────────────────────────────────

-- pgvector: enables VECTOR column type and ANN index operators (<-> <=> <#>)
-- Used by: TelemetryRaw.location (geospatial), future embedding storage
CREATE EXTENSION IF NOT EXISTS vector;

-- uuid-ossp: gen_random_uuid() is built-in PG13+, but explicit is better
-- Enables server-side UUID generation as column defaults
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
