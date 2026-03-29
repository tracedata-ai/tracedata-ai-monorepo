# -----------------------------------------------------------------------------
# Backend CI Runner - Local Pre-Push Verification
# -----------------------------------------------------------------------------
#
# Runs local checks for files covered by:
#   - .github/workflows/ci-backend-api.yaml
#   - .github/workflows/ci-backend-agents.yaml
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

function Get-CiPythonFiles {
    # Union of backend paths watched by API CI + Agents CI workflows.
    # Includes: api, agents, common, core, tests, scripts, security, and root-level Python files.
    $ScopeRoots = @("api", "agents", "common", "core", "tests", "scripts", "security")

    $files = @()
    
    # Collect Python files from scope directories
    foreach ($root in $ScopeRoots) {
        if (Test-Path $root) {
            $files += Get-ChildItem -Path $root -Recurse -File -Filter *.py | ForEach-Object {
                $_.FullName
            }
        }
    }

    # Include root-level Python files (like check_redis.py, etc.)
    $files += Get-ChildItem -Path . -File -Filter *.py | ForEach-Object {
        $_.FullName
    }

    return $files | Sort-Object -Unique
}

$CiPythonFiles = Get-CiPythonFiles

if (-not $CiPythonFiles -or $CiPythonFiles.Count -eq 0) {
    Write-Failure "No Python files found in CI scope (api/agents/common/core/tests)."
    exit 1
}

try {
    Write-Step "Syncing dependencies with uv..."
    uv sync --frozen --extra dev
    Write-Success "Dependencies synced (frozen)."

    Write-Step "Checking lockfile sync..."
    uv lock --check
    Write-Success "Lockfile is healthy."

    Write-Step "Running full backend format/lint pass (all Python files)..."
    uv run black .
    uv run ruff check . --fix
    Write-Success "All Python files formatted and linted."

    Write-Step "Running isort (Auto-fix imports) on CI scope..."
    uv run isort @CiPythonFiles
    Write-Success "Import sorting applied."

    Write-Step "Running Black (Auto-format) on CI scope..."
    uv run black @CiPythonFiles
    Write-Success "Formatting applied."

    Write-Step "Running Ruff (Auto-fix lint) on CI scope..."
    uv run ruff check @CiPythonFiles --fix
    Write-Success "Ruff auto-fixes applied."

    Write-Step "Running Black (Formatter Check)..."
    uv run black --check @CiPythonFiles
    Write-Success "Formatting check passed."

    Write-Step "Running Ruff (Linter Check)..."
    uv run ruff check @CiPythonFiles --no-fix
    Write-Success "Linting check passed."

    Write-Step "Running Bandit (Security Scan)..."
    uv run bandit -r api/ -ll
    Write-Success "Security scan passed."

    Write-Step "Running Mypy (Type Check)..."
    uv run mypy api agents tests/agents --ignore-missing-imports --no-error-summary
    Write-Success "Type check passed."

    Write-Step "Running Unit Tests (Pytest)..."
    Write-Host "NOTE: Requires PostgreSQL with pgvector on port 5432." -ForegroundColor Gray
    uv run pytest --cov=api --cov-report=term-missing --cov-fail-under=1 -v tests/
    Write-Success "All tests passed."

} catch {
    Write-Failure "CI check failed at the current step."
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    exit 1
}
