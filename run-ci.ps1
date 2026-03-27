# ─────────────────────────────────────────────────────────────────────────────
# 🚀 TraceData Monorepo — Unified CI Orchestrator
# ─────────────────────────────────────────────────────────────────────────────
#
# Launches both Backend and Frontend CI runners simultaneously.
# Prefers Windows Terminal (split panes) if available.
#
# Usage:
#   ./run-ci.ps1
# ─────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

$BackendScript = Join-Path $PSScriptRoot "backend\scripts\run-ci.ps1"
$FrontendScript = Join-Path $PSScriptRoot "frontend\scripts\run-ci.ps1"
$BackendDir = Join-Path $PSScriptRoot "backend"
$FrontendDir = Join-Path $PSScriptRoot "frontend"

Write-Host "🔍 Locating CI Runners..." -ForegroundColor Cyan
if (-not (Test-Path $BackendScript)) { throw "Backend runner not found at $BackendScript" }
if (-not (Test-Path $FrontendScript)) { throw "Frontend runner not found at $FrontendScript" }

$WT = Get-Command wt -ErrorAction SilentlyContinue

if ($WT) {
    Write-Host "📟 Launching Windows Terminal with split panes..." -ForegroundColor Green
    
    $WTArgs = "-w 0 nt -d `"$BackendDir`" powershell -NoExit -Command `"./scripts/run-ci.ps1`" `; split-pane -v -d `"$FrontendDir`" powershell -NoExit -Command `"./scripts/run-ci.ps1`""
    Start-Process wt -ArgumentList $WTArgs
} else {
    Write-Host "🪟 Windows Terminal not found. Falling back to separate PowerShell windows..." -ForegroundColor Yellow
    
    Start-Process powershell -ArgumentList "-NoExit -Command `"Set-Location '$BackendDir'; ./scripts/run-ci.ps1`""
    Start-Process powershell -ArgumentList "-NoExit -Command `"Set-Location '$FrontendDir'; ./scripts/run-ci.ps1`""
}

Write-Host "`n✅ CI Orchestration complete. Monitor the new windows/panes for results." -ForegroundColor Cyan
