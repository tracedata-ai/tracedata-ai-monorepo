"""
LAYER 3 ENFORCEMENT: Database Role Permissions

SQL script to set up database roles with proper permissions.
One-time setup in production. Defense-in-depth enforcement.

Execution:
  psql -U postgres -d tracedata_db -f database_permissions.sql

Result: Database itself enforces ownership rules.
  If a layer 1-2 check fails, DB permissions still protect!
"""

# ──────────────────────────────────────────────────────────────────────────────
# SETUP: Create roles and schemas
# ──────────────────────────────────────────────────────────────────────────────

SQL_CREATE_SCHEMAS = """
-- Create schemas if they don't exist
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS safety_schema;
CREATE SCHEMA IF NOT EXISTS scoring_schema;
CREATE SCHEMA IF NOT EXISTS sentiment_schema;
CREATE SCHEMA IF NOT EXISTS coaching_schema;
"""

# ──────────────────────────────────────────────────────────────────────────────
# ROLES: Create agent-specific database users
# ──────────────────────────────────────────────────────────────────────────────

SQL_CREATE_ROLES = """
-- Create roles (lowercase, no password - use cert auth in production)

CREATE ROLE safety_agent NOLOGIN;
CREATE ROLE scoring_agent NOLOGIN;
CREATE ROLE sentiment_agent NOLOGIN;
CREATE ROLE support_agent NOLOGIN;
CREATE ROLE db_manager NOLOGIN;

-- Roles that can perform administrative tasks
GRANT CREATEROLE, CREATEDB ON DATABASE tracedata_db TO db_manager;
"""

# ──────────────────────────────────────────────────────────────────────────────
# SAFETY AGENT PERMISSIONS
# ──────────────────────────────────────────────────────────────────────────────

SQL_SAFETY_AGENT_PERMISSIONS = """
-- SafetyAgent: can READ shared tables, WRITE to safety_schema only

-- Read shared tables
GRANT SELECT ON public.trips TO safety_agent;
GRANT SELECT ON public.events TO safety_agent;

-- OWN all safety_schema tables
GRANT USAGE ON SCHEMA safety_schema TO safety_agent;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA safety_schema TO safety_agent;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA safety_schema TO safety_agent;

-- Explicitly DENY write access to other agent schemas
REVOKE ALL ON SCHEMA scoring_schema FROM safety_agent;
REVOKE ALL ON SCHEMA sentiment_schema FROM safety_agent;
REVOKE ALL ON SCHEMA coaching_schema FROM safety_agent;

-- Deny write to shared tables
REVOKE INSERT, UPDATE, DELETE ON public.trips FROM safety_agent;
REVOKE INSERT, UPDATE, DELETE ON public.events FROM safety_agent;
"""

# ──────────────────────────────────────────────────────────────────────────────
# SCORING AGENT PERMISSIONS
# ──────────────────────────────────────────────────────────────────────────────

SQL_SCORING_AGENT_PERMISSIONS = """
-- ScoringAgent: can READ shared tables, WRITE to scoring_schema only

-- Read shared tables
GRANT SELECT ON public.trips TO scoring_agent;
GRANT SELECT ON public.events TO scoring_agent;

-- OWN all scoring_schema tables
GRANT USAGE ON SCHEMA scoring_schema TO scoring_agent;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA scoring_schema TO scoring_agent;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA scoring_schema TO scoring_agent;

-- Explicitly DENY write access to other agent schemas
REVOKE ALL ON SCHEMA safety_schema FROM scoring_agent;
REVOKE ALL ON SCHEMA sentiment_schema FROM scoring_agent;
REVOKE ALL ON SCHEMA coaching_schema FROM scoring_agent;

-- Deny write to shared tables
REVOKE INSERT, UPDATE, DELETE ON public.trips FROM scoring_agent;
REVOKE INSERT, UPDATE, DELETE ON public.events FROM scoring_agent;
"""

# ──────────────────────────────────────────────────────────────────────────────
# SENTIMENT AGENT PERMISSIONS
# ──────────────────────────────────────────────────────────────────────────────

SQL_SENTIMENT_AGENT_PERMISSIONS = """
-- SentimentAgent: can READ shared tables, WRITE to sentiment_schema only

-- Read shared tables
GRANT SELECT ON public.trips TO sentiment_agent;
GRANT SELECT ON public.events TO sentiment_agent;

-- OWN all sentiment_schema tables
GRANT USAGE ON SCHEMA sentiment_schema TO sentiment_agent;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA sentiment_schema TO sentiment_agent;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sentiment_schema TO sentiment_agent;

-- Explicitly DENY write access to other agent schemas
REVOKE ALL ON SCHEMA safety_schema FROM sentiment_agent;
REVOKE ALL ON SCHEMA scoring_schema FROM sentiment_agent;
REVOKE ALL ON SCHEMA coaching_schema FROM sentiment_agent;

-- Deny write to shared tables
REVOKE INSERT, UPDATE, DELETE ON public.trips FROM sentiment_agent;
REVOKE INSERT, UPDATE, DELETE ON public.events FROM sentiment_agent;
"""

# ──────────────────────────────────────────────────────────────────────────────
# SUPPORT AGENT PERMISSIONS
# ──────────────────────────────────────────────────────────────────────────────

SQL_SUPPORT_AGENT_PERMISSIONS = """
-- SupportAgent: can READ shared tables, WRITE to coaching_schema only

-- Read shared tables
GRANT SELECT ON public.trips TO support_agent;
GRANT SELECT ON public.events TO support_agent;

-- OWN all coaching_schema tables
GRANT USAGE ON SCHEMA coaching_schema TO support_agent;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA coaching_schema TO support_agent;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA coaching_schema TO support_agent;

-- Explicitly DENY write access to other agent schemas
REVOKE ALL ON SCHEMA safety_schema FROM support_agent;
REVOKE ALL ON SCHEMA scoring_schema FROM support_agent;
REVOKE ALL ON SCHEMA sentiment_schema FROM support_agent;

-- Deny write to shared tables
REVOKE INSERT, UPDATE, DELETE ON public.trips FROM support_agent;
REVOKE INSERT, UPDATE, DELETE ON public.events FROM support_agent;
"""

# ──────────────────────────────────────────────────────────────────────────────
# DB MANAGER PERMISSIONS
# ──────────────────────────────────────────────────────────────────────────────

SQL_DB_MANAGER_PERMISSIONS = """
-- DBManager: FULL access to shared tables + all agent schemas
-- DBManager is the orchestrator's database coordinator

-- Full access to shared tables
GRANT ALL PRIVILEGES ON public.trips TO db_manager;
GRANT ALL PRIVILEGES ON public.events TO db_manager;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO db_manager;

-- Full access to all agent schemas (for audit, recovery, etc.)
GRANT USAGE ON SCHEMA safety_schema TO db_manager;
GRANT USAGE ON SCHEMA scoring_schema TO db_manager;
GRANT USAGE ON SCHEMA sentiment_schema TO db_manager;
GRANT USAGE ON SCHEMA coaching_schema TO db_manager;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA safety_schema TO db_manager;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA scoring_schema TO db_manager;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sentiment_schema TO db_manager;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA coaching_schema TO db_manager;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA safety_schema TO db_manager;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA scoring_schema TO db_manager;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sentiment_schema TO db_manager;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA coaching_schema TO db_manager;
"""

# ──────────────────────────────────────────────────────────────────────────────
# DEFAULT PRIVILEGES FOR FUTURE TABLES
# ──────────────────────────────────────────────────────────────────────────────

SQL_DEFAULT_PRIVILEGES = """
-- Ensure future tables in agent schemas follow the same permissions

-- SafetyAgent
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA safety_schema
  GRANT SELECT, INSERT, UPDATE ON TABLES TO safety_agent;

-- ScoringAgent
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA scoring_schema
  GRANT SELECT, INSERT, UPDATE ON TABLES TO scoring_agent;

-- SentimentAgent
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA sentiment_schema
  GRANT SELECT, INSERT, UPDATE ON TABLES TO sentiment_agent;

-- SupportAgent
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA coaching_schema
  GRANT SELECT, INSERT, UPDATE ON TABLES TO support_agent;

-- DBManager gets full access
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA public
  GRANT ALL PRIVILEGES ON TABLES TO db_manager;
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA safety_schema
  GRANT ALL PRIVILEGES ON TABLES TO db_manager;
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA scoring_schema
  GRANT ALL PRIVILEGES ON TABLES TO db_manager;
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA sentiment_schema
  GRANT ALL PRIVILEGES ON TABLES TO db_manager;
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA coaching_schema
  GRANT ALL PRIVILEGES ON TABLES TO db_manager;
"""

# ──────────────────────────────────────────────────────────────────────────────
# EXECUTE ALL
# ──────────────────────────────────────────────────────────────────────────────

COMPLETE_SETUP_SCRIPT = f"""
-- Database Role & Permission Setup for TraceData
-- Layer 3: Defense-in-depth enforcement
-- Generated: 2024
-- Usage: psql -U postgres -d tracedata_db -f database_permissions.sql

BEGIN TRANSACTION;

-- Step 1: Create schemas
{SQL_CREATE_SCHEMAS}

-- Step 2: Create roles
{SQL_CREATE_ROLES}

-- Step 3: Set up agent permissions
{SQL_SAFETY_AGENT_PERMISSIONS}
{SQL_SCORING_AGENT_PERMISSIONS}
{SQL_SENTIMENT_AGENT_PERMISSIONS}
{SQL_SUPPORT_AGENT_PERMISSIONS}
{SQL_DB_MANAGER_PERMISSIONS}

-- Step 4: Set default privileges for future tables
{SQL_DEFAULT_PRIVILEGES}

COMMIT;

-- Verify setup
SELECT 'Setup complete!' AS status;
"""


if __name__ == "__main__":
    # For reference/documentation purposes
    print("=" * 80)
    print("DATABASE PERMISSIONS SETUP")
    print("=" * 80)
    print()
    print("To apply this setup:")
    print("  1. Save this file as 'database_permissions.sql'")
    print("  2. Run: psql -U postgres -d tracedata_db -f database_permissions.sql")
    print()
    print("=" * 80)
    print("COMPLETE SCRIPT:")
    print("=" * 80)
    print(COMPLETE_SETUP_SCRIPT)
