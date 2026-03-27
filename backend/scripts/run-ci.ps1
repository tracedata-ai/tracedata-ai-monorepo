# -----------------------------------------------------------------------------
# Backend CI Runner - Local Pre-Push Verification
# -----------------------------------------------------------------------------
#
# Runs all checks defined in .github/workflows/ci-backend-api.yaml
#
# Usage:
#   ./scripts/run-ci.ps1
# -----------------------------------------------------------------------------

$ErrorActionPreference = "Stop"

# Ensure we are running from the backend root (where pyproject.toml is)
$BackendRoot = Resolve-Path "$PSScriptRoot/.."
Set-Location $BackendRoot
Write-Host "Working Directory: $BackendRoot" -ForegroundColor Gray

function Write-Step ([string]$msg) {
    Write-Host "`n>> $msg" -ForegroundColor Cyan
}

function Write-Success ([string]$msg) {
    Write-Host "OK: $msg" -ForegroundColor Green
}

function Write-Failure ([string]$msg) {
    Write-Host "ERR: $msg" -ForegroundColor Red
}

try {
    Write-Step "Syncing dependencies with uv..."
    # --frozen ensures we use the exact versions in uv.lock
    uv sync --frozen --extra dev
    Write-Success "Dependencies synced (frozen)."

    Write-Step "Checking lockfile sync..."
    uv lock --check
    Write-Success "Lockfile is healthy."

    Write-Step "Running Black (Formatter Check)..."
    # Black ensures the code follows the 88-char style
    uv run black --check .
    Write-Success "Formatting check passed."

    Write-Step "Running Ruff (Linter Check)..."
    # --no-fix ensures we fail if issues exist, matching CI behavior
    uv run ruff check . --no-fix
    Write-Success "Linting check passed."

    Write-Step "Running Bandit (Security Scan)..."
    uv run bandit -r api/ -ll
    Write-Success "Security scan passed."

    Write-Step "Running Mypy (Type Check)..."
    uv run mypy api --ignore-missing-imports --no-error-summary
    Write-Success "Type check passed."

    Write-Step "Running Unit Tests (Pytest)..."
    Write-Host "NOTE: Requires PostgreSQL with pgvector on port 5432." -ForegroundColor Gray
    # Pass --cov flags to match CI and verify coverage locally
    uv run pytest --cov=api --cov-report=term-missing --cov-fail-under=1 -v tests/
    Write-Success "All tests passed."

    Write-Host "`nCI Checks Passed Locally! Ready to push." -ForegroundColor Green -BackgroundColor Black
} catch {
    Write-Failure "CI check failed at the current step."
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    exit 1
}
