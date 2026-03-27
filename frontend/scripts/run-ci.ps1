# ─────────────────────────────────────────────────────────────────────────────
# 🏗️ Optimized Frontend CI Runner — Local Pre-Push Verification
# ─────────────────────────────────────────────────────────────────────────────
#
# Runs all checks in parallel using npm-run-all for maximum efficiency.
#
# Usage:
#   ./scripts/run-ci.ps1
# ─────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

# Ensure we are running from the frontend root
$FrontendRoot = Resolve-Path "$PSScriptRoot/.."
Set-Location $FrontendRoot

function Write-Step ([string]$msg) {
    Write-Host "`n🚀 $msg" -ForegroundColor Cyan
}

function Write-Success ([string]$msg) {
    Write-Host "✅ $msg" -ForegroundColor Green
}

function Write-Failure ([string]$msg) {
    Write-Host "❌ $msg" -ForegroundColor Red
}

try {
    Write-Step "Installing dependencies (npm ci)..."
    npm ci
    Write-Success "Dependencies installed."

    Write-Step "Running Parallel Static Analysis (Lint, Type Check, Audit)..."
    # We use 'npm run validate' which uses npm-run-all for robust parallel execution
    npm run validate
    Write-Success "Static analysis passed."

    Write-Step "Running logic checks (npm test)..."
    npm test
    Write-Success "All tests passed."

    Write-Step "Building production bundle (npm run build)..."
    npm run build
    Write-Success "Build successful."

    Write-Host "`n✨ CI Checks Passed Locally! Ready to push." -ForegroundColor Green -BackgroundColor Black
} catch {
    Write-Failure "CI check failed at the current step."
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    exit 1
}
