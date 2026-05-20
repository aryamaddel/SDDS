@echo off
title SDDS — Model Downloader
color 02

echo.
echo  ================================================
echo   SDDS // ATLAS — Model Downloader
echo  ================================================
echo.

cd /d "%~dp0backend"
echo [..] Checking python virtual environment...
uv run python "%~dp0download_model.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERR] Model download failed. Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Done. You can now start SDDS using start.bat
echo.
pause
