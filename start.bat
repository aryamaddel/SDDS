@echo off
title SDDS — Smart Defence Decision Systems
color 02

echo.
echo  ================================================
echo   SDDS // ATLAS — Startup
echo  ================================================
echo.

REM ── Check uv is available ──────────────────────────
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERR] uv not found. Install it from https://docs.astral.sh/uv/
    echo        or run:  winget install astral-sh.uv
    pause
    exit /b 1
)

REM ── Check Local Model file ──────────────────────────
echo  [..] Checking local LLM model...
if not defined SDDS_MODEL_PATH (
    set "SDDS_MODEL_PATH=%~dp0models\qwen2.5-3b-instruct-q4_k_m.gguf"
)
if not exist "%SDDS_MODEL_PATH%" (
    echo  [!]  Local GGUF model file not found at:
    echo       %SDDS_MODEL_PATH%
    echo.
    echo       You need to download the model file of approximately 2.2 GB before running SDDS.
    echo.
    choice /m "Would you like to download the recommended model now?" /c YN
    if errorlevel 2 (
        echo  [ERR] Cannot run SDDS without a local model file.
        pause
        exit /b 1
    )
    echo  [..] Starting model downloader...
    call "%~dp0download_model.bat"
    if errorlevel 1 (
        echo  [ERR] Model download failed.
        pause
        exit /b 1
    )
)

echo  [OK] Local model ready: %SDDS_MODEL_PATH%
echo.

REM ── Sync backend deps with uv ───────────────────────
echo  [..] Syncing backend dependencies with uv...
cd /d "%~dp0backend"
uv sync --quiet
if %errorlevel% neq 0 (
    echo  [ERR] uv sync failed. Check pyproject.toml.
    pause
    exit /b 1
)
echo  [OK] Dependencies ready.
echo.

REM ── Start backend in new window ─────────────────────
echo  [..] Starting ATLAS backend on port 8000...
start "SDDS Backend — port 8000" /D "%~dp0backend" cmd /k "uv run uvicorn main:app --reload --port 8000 --log-level warning"

REM ── Brief pause so backend has time to bind ─────────
timeout /t 3 /nobreak >nul

REM ── Start frontend HTTP server in new window ────────
echo  [..] Starting frontend server on port 3000...
start "SDDS Frontend — port 3000" /D "%~dp0frontend" cmd /k "uv run python -m http.server 3000"

timeout /t 2 /nobreak >nul

REM ── Open browser ────────────────────────────────────
echo  [..] Opening browser...
start http://localhost:3000

echo.
echo  ================================================
echo   SDDS running:
echo     Frontend : http://localhost:3000
echo     Backend  : http://localhost:8000
echo     API docs : http://localhost:8000/docs
echo  ================================================
echo.
echo  Close the two terminal windows to stop SDDS.
echo.
pause
