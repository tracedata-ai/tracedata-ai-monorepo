# ─────────────────────────────────────────────────────────────────────────────
# 🏗️ Frontend CI Runner — Local Pre-Push Verification
# ─────────────────────────────────────────────────────────────────────────────
#
# Runs all checks defined in .github/workflows/ci-frontend.yaml
#
# Usage:
#   ./scripts/run-ci.ps1
# ─────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

function Write-Step([string]$msg) {
    Write-Host "`n🚀 $msg" -ForegroundColor Cyan
}

function Write-Success([string]$msg) {
    Write-Host "✅ $msg" -ForegroundColor Green
}

function Write-Failure([string]$msg) {
    Write-Host "❌ $msg" -ForegroundColor Red
}

try {
    Write-Step "Installing dependencies with npm ci..."
    npm ci
    Write-Success "Dependencies installed."

    Write-Step "Running ESLint..."
    npm run lint
    Write-Success "Linting passed."

    Write-Step "Running TypeScript Type Check..."
    npx tsc --noEmit
    Write-Success "Type check passed."

    Write-Step "Running npm audit..."
    npm audit --audit-level=high
    Write-Success "Security audit passed."

    Write-Step "Building production bundle..."
    npm run build
    Write-Success "Build successful."

    Write-Host "`n✨ CI Checks Passed Locally! Ready to push." -ForegroundColor Green -BackgroundColor Black
}
catch {
    Write-Failure "CI check failed at the current step."
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    exit 1
}
