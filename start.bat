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

REM ── Check Ollama is reachable ───────────────────────
echo  [..] Checking Ollama...
curl -sf http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!]  Ollama not detected on localhost:11434
    echo       Make sure Ollama is running before starting SDDS.
    echo       Download: https://ollama.com
    echo.
    choice /m "Continue anyway?" /c YN
    if errorlevel 2 exit /b 1
)

echo  [OK] Ollama check complete.
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
start "SDDS Backend — port 8000" cmd /k "cd /d "%~dp0backend" && uv run uvicorn main:app --reload --port 8000 --log-level warning"

REM ── Brief pause so backend has time to bind ─────────
timeout /t 3 /nobreak >nul

REM ── Start frontend HTTP server in new window ────────
echo  [..] Starting frontend server on port 3000...
start "SDDS Frontend — port 3000" cmd /k "cd /d "%~dp0frontend" && uv run python -m http.server 3000"

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
