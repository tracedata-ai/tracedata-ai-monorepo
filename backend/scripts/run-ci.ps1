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

# Track checks and timing
$StartTime = Get-Date
$Checks = @()

function LogCheck([string]$name, [bool]$passed) {
    $Checks += @{
        name = $name
        passed = $passed
    }
}

try {
    Write-Step "Syncing dependencies with uv..."
    uv sync --frozen --extra dev
    Write-Success "Dependencies synced (frozen)."
    LogCheck "Dependencies Sync" $true

    Write-Step "Checking lockfile sync..."
    uv lock --check
    Write-Success "Lockfile is healthy."
    LogCheck "Lockfile Check" $true

    Write-Step "Running full backend format/lint pass (all Python files)..."
    uv run black .
    uv run ruff check . --fix
    Write-Success "All Python files formatted and linted."
    LogCheck "Full Backend Format/Lint" $true

    Write-Step "Running isort (Auto-fix imports) on API+Agents CI scope..."
    uv run isort @CiPythonFiles
    Write-Success "Import sorting applied."
    LogCheck "Import Sorting (isort)" $true

    Write-Step "Running Black (Auto-format) on API+Agents CI scope..."
    uv run black @CiPythonFiles
    Write-Success "Formatting applied."
    LogCheck "Code Formatting (Black)" $true

    Write-Step "Running Ruff (Auto-fix lint) on API+Agents CI scope..."
    uv run ruff check @CiPythonFiles --fix
    Write-Success "Ruff auto-fixes applied."
    LogCheck "Linting Auto-fix (Ruff)" $true

    Write-Step "Running Black (Formatter Check) on API+Agents CI scope..."
    uv run black --check @CiPythonFiles
    Write-Success "Formatting check passed."
    LogCheck "Formatter Check" $true

    Write-Step "Running Ruff (Linter Check) on API+Agents CI scope..."
    uv run ruff check @CiPythonFiles --no-fix
    Write-Success "Linting check passed."
    LogCheck "Linter Check" $true

    Write-Step "Running Bandit (Security Scan)..."
    uv run bandit -r api/ -ll
    Write-Success "Security scan passed."
    LogCheck "Security Scan (Bandit)" $true

    Write-Step "Running Mypy (Type Check)..."
    uv run mypy api --ignore-missing-imports --no-error-summary
    Write-Success "Type check passed."
    LogCheck "Type Check (Mypy)" $true

    Write-Step "Running Unit Tests (Pytest)..."
    Write-Host "NOTE: Requires PostgreSQL with pgvector on port 5432." -ForegroundColor Gray
    uv run pytest --cov=api --cov-report=term-missing --cov-fail-under=1 -v tests/
    Write-Success "All tests passed."
    LogCheck "Unit Tests (Pytest)" $true

} catch {
    Write-Failure "CI check failed at the current step."
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    LogCheck "Failed Step" $false
}

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

$EndTime = Get-Date
$Duration = $EndTime - $StartTime

$PassedCount = ($Checks | Where-Object { $_.passed } | Measure-Object).Count
$FailedCount = ($Checks | Where-Object { -not $_.passed } | Measure-Object).Count
$TotalCount = $Checks.Count

Write-Host "`n$('=' * 80)" -ForegroundColor Cyan
Write-Host "CI CHECK SUMMARY" -ForegroundColor Cyan
Write-Host "$('=' * 80)" -ForegroundColor Cyan

foreach ($check in $Checks) {
    if ($check.passed) {
        Write-Host "[PASS] $($check.name)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $($check.name)" -ForegroundColor Red
    }
}

Write-Host "`n$('-' * 80)" -ForegroundColor Cyan
Write-Host "Results: $PassedCount/$TotalCount checks passed" -ForegroundColor $(if ($FailedCount -eq 0) { "Green" } else { "Red" })
Write-Host "Duration: $([Math]::Round($Duration.TotalSeconds, 2))s" -ForegroundColor Cyan
Write-Host "$('=' * 80)" -ForegroundColor Cyan

if ($FailedCount -eq 0) {
    Write-Host "`n=== All checks passed! Ready to push to origin. ===" -ForegroundColor Green -BackgroundColor Black
    exit 0
} else {
    Write-Host "`n=== $FailedCount check(s) failed. Please review above. ===" -ForegroundColor Red
    exit 1
}
