@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title TasteWise

cd /d "%~dp0"

echo ============================================
echo    TasteWise - Recipes Recommendation
echo ============================================
echo.

:: ---- Find Python ----
set PY_CMD=python
python --version >nul 2>&1
if not errorlevel 1 goto :FOUND_PY

py -3 --version >nul 2>&1
if not errorlevel 1 set PY_CMD=py -3 & goto :FOUND_PY

echo [ERROR] Python 3.10+ not found.
echo   Download: https://www.python.org/downloads/
pause
exit /b 1

:FOUND_PY
%PY_CMD% --version

:: ---- Virtual Environment ----
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment ...
    %PY_CMD% -m venv .venv
    if not errorlevel 1 goto :VENV_OK
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
) else (
    echo Virtual environment exists
)
:VENV_OK

call .venv\Scripts\activate.bat
if not errorlevel 1 goto :DEPS_CHECK
echo [ERROR] Failed to activate virtual environment
pause
exit /b 1

:: ---- Dependencies ----
:DEPS_CHECK
echo Checking dependencies ...

python _check_deps.py >nul 2>&1
if not errorlevel 1 goto :DEPS_OK

echo Installing dependencies (first run may take a while)...
pip install -r requirements.txt
if not errorlevel 1 goto :DEPS_OK
echo [ERROR] Dependency installation failed
pause
exit /b 1

:DEPS_OK

echo ============================================
setlocal disabledelayedexpansion
echo    [OK] Ready! Starting TasteWise ...
setlocal enabledelayedexpansion
echo    Browser: http://localhost:8501
echo    Close this window to stop the app
echo ============================================
echo.

streamlit run app.py

echo.
echo App stopped
pause
