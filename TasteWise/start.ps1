<#
.SYNOPSIS
    TasteWise - Recipes Recommendation System (One-click startup)
.DESCRIPTION
    Detects Python, creates/activates virtual environment, installs dependencies,
    and launches the Streamlit app.
.NOTES
    If you encounter execution policy errors, run:
        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    Or use start.bat instead.
#>

#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptRoot -ErrorAction Stop

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   TasteWise - Recipes Recommendation"        -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ---- Find Python ----
function Find-Python {
    $candidates = @("python", "py -3", "python3")
    foreach ($cmd in $candidates) {
        try {
            $ver = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $ver -match '(\d+)\.(\d+)') {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
                    return @{ Command = $cmd; Version = $ver.Trim() }
                }
            }
        } catch { continue }
    }
    return $null
}

$python = Find-Python
if (-not $python) {
    Write-Host "[ERROR] Python 3.10+ not found." -ForegroundColor Red
    Write-Host "  Download: https://www.python.org/downloads/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ("[OK] Python: " + $python.Version) -ForegroundColor Green

# ---- Virtual Environment ----
$venvPath = Join-Path $scriptRoot ".venv"
$activateScript = Join-Path $venvPath "Scripts" "Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "[....] Creating virtual environment ..." -ForegroundColor Yellow
    & $python.Command "-m" "venv" $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[OK] Virtual environment exists" -ForegroundColor Green
}

try {
    & $activateScript
    Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "  Try: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# ---- Dependencies ----
Write-Host "[....] Checking dependencies ..." -ForegroundColor Yellow

$result = & $python.Command "_check_deps.py" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[....] Installing dependencies (first run may take a while)..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Dependency installation failed" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[OK] All dependencies ready" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   [OK] Ready! Starting TasteWise ..."        -ForegroundColor Green
Write-Host "   Browser: http://localhost:8501"            -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to stop the app"              -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

try {
    streamlit run app.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Streamlit exited with code: $LASTEXITCODE" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Streamlit failed: $_" -ForegroundColor Red
}

Read-Host "App stopped. Press Enter to exit"
