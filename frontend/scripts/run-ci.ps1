# ─────────────────────────────────────────────────────────────────────────────
# 🏗️ Optimized Frontend CI Runner — Local Pre-Push Verification
# ─────────────────────────────────────────────────────────────────────────────
#
# Runs all checks in parallel where possible to maximize efficiency.
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

    Write-Step "Starting Parallel Static Analysis (Lint, Type Check, Audit)..."
    
    # Define tasks to run in parallel
    $Tasks = @(
        @{ Name = "Linting"; Command = "npm run lint" },
        @{ Name = "Type Checking"; Command = "npm run type-check" },
        @{ Name = "Security Audit"; Command = "npm audit --audit-level=high" }
    )

    $Jobs = @()
    foreach ($Task in $Tasks) {
        Write-Host "   -> Starting $($Task.Name)..." -ForegroundColor Gray
        $Jobs += Start-Job -ScriptBlock { 
            param($cmd, $path) 
            Set-Location $path
            # Run command and capture exit code
            cmd /c "$cmd 2>&1"
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        } -ArgumentList $Task.Command, $FrontendRoot -Name $Task.Name
    }

    Write-Host "`n⌛ Waiting for parallel tasks to complete..." -ForegroundColor Yellow
    $null = Wait-Job $Jobs

    $Failed = $false
    foreach ($Job in $Jobs) {
        $ExitCode = $Job.ChildJobs[0].ExitCode
        if ($ExitCode -ne 0) {
            Write-Failure "$($Job.Name) failed (Exit Code: $ExitCode)!"
            Receive-Job -Job $Job -Keep | Write-Host -ForegroundColor Yellow
            $Failed = $true
        } else {
            Write-Success "$($Job.Name) passed."
        }
    }

    if ($Failed) {
        throw "One or more static analysis tasks failed."
    }

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
} finally {
    if ($Jobs) { 
        Get-Job | Stop-Job
        Get-Job | Remove-Job -Force 
    }
}
