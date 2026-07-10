param(
    [switch]$RecommenderOnly,
    [string]$Python
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$appRoot = Join-Path $repoRoot "TasteWise"
$venvPython = Join-Path $appRoot ".venv\Scripts\python.exe"

function Resolve-Python {
    if ($Python) {
        return $Python
    }

    if (Test-Path $venvPython) {
        return $venvPython
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        return $pythonCommand.Source
    }

    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCommand) {
        return $pyCommand.Source
    }

    throw "Python was not found. Activate a virtual environment or pass -Python <path-to-python.exe>."
}

$pythonExe = Resolve-Python

Push-Location $appRoot
try {
    Write-Host "Checking Python syntax..."
    & $pythonExe -m py_compile app.py data_importer.py data_manager.py recommender.py utils\explanation.py utils\similarity.py

    if (Test-Path "utils\hometown.py") {
        & $pythonExe -m py_compile utils\hometown.py
    }

    Write-Host "Running tests..."
    if ($RecommenderOnly) {
        & $pythonExe -m pytest tests\test_recommender.py
    } else {
        & $pythonExe -m pytest
    }
}
finally {
    Pop-Location
}
