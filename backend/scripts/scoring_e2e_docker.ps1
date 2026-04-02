<#
.SYNOPSIS
  Reset Docker stack (optional), apply DB bootstrap, flush Redis, run multi-truck scoring seed, print counts.

.DESCRIPTION
  One-shot E2E smoke for ingestion → orchestrator → scoring without involving an AI assistant.
  Run from repo root:
    pwsh -File backend/scripts/scoring_e2e_docker.ps1
  Or from backend:
    pwsh -File scripts/scoring_e2e_docker.ps1 -RepoRoot ..

.PARAMETER RepoRoot
  Path to tracedata-ai-monorepo root (folder containing docker-compose.yml). Default: two levels above this script.

.PARAMETER SkipReset
  If set, skip "docker compose down -v" (reuse volumes; faster, dirtier).

.PARAMETER WaitSeconds
  Seconds to wait after seeding Redis before querying Postgres (pipeline needs time to drain).

.PARAMETER ApplyAgentSchemas
  Also run agent_schemas.sql after bootstrap_e2e.sql (safety/coaching/sentiment tables).
#>
param(
    [string] $RepoRoot = "",
    [switch] $SkipReset,
    [int] $WaitSeconds = 90,
    [switch] $ApplyAgentSchemas
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}
Set-Location $RepoRoot

Write-Host "Repo root: $RepoRoot"

if (-not $SkipReset) {
    Write-Host "`n=== docker compose down -v ===" -ForegroundColor Cyan
    docker compose down -v
}

Write-Host "`n=== docker compose up -d --build ===" -ForegroundColor Cyan
docker compose up -d --build

Write-Host "`n=== waiting for Postgres (30s) ===" -ForegroundColor Cyan
Start-Sleep -Seconds 30

$bootstrap = Join-Path $RepoRoot "backend/scripts/bootstrap_e2e.sql"
if (-not (Test-Path $bootstrap)) {
    throw "Missing $bootstrap"
}

Write-Host "`n=== apply bootstrap_e2e.sql ===" -ForegroundColor Cyan
Get-Content -Raw $bootstrap | docker compose exec -T db psql -U postgres -d tracedata

if ($ApplyAgentSchemas) {
    $agentSql = Join-Path $RepoRoot "backend/scripts/agent_schemas.sql"
    if (Test-Path $agentSql) {
        Write-Host "`n=== apply agent_schemas.sql ===" -ForegroundColor Cyan
        Get-Content -Raw $agentSql | docker compose exec -T db psql -U postgres -d tracedata
    }
}

Write-Host "`n=== Redis FLUSHALL ===" -ForegroundColor Cyan
docker compose exec -T redis redis-cli FLUSHALL | Out-Host

Write-Host "`n=== push_multi_truck_scoring_seed.py (via api container) ===" -ForegroundColor Cyan
docker compose exec -T api python scripts/push_multi_truck_scoring_seed.py

Write-Host "`n=== wait ${WaitSeconds}s for workers ===" -ForegroundColor Cyan
Start-Sleep -Seconds $WaitSeconds

Write-Host "`n=== Postgres counts ===" -ForegroundColor Green
$sql = @"
SELECT 'pipeline_events' AS t, COUNT(*)::text AS n FROM pipeline_events
UNION ALL
SELECT 'trip_scores', COUNT(*)::text FROM scoring_schema.trip_scores
UNION ALL
SELECT 'pipeline_events_processed', COUNT(*)::text FROM pipeline_events WHERE status = 'processed';
"@
docker compose exec -T db psql -U postgres -d tracedata -c $sql

Write-Host "`nDone. Tune -WaitSeconds if counts look low (workers still draining)." -ForegroundColor Yellow
