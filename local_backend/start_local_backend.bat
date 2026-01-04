@echo off
REM ============================================
REM Local Emotion Detection Backend - Startup Script
REM ============================================
REM 
REM This script starts the LOCAL backend on port 8001.
REM Run this ALONGSIDE the existing Colab backend (port 8000).
REM
REM Both backends can run simultaneously for dual-mode support.
REM ============================================

echo.
echo ============================================
echo   LOCAL EMOTION DETECTION BACKEND
echo   FastAPI on port 8001
echo ============================================
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies if needed
if not exist "venv\Lib\site-packages\fastapi" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting Local Backend...
echo API will be available at: http://localhost:8001
echo API docs: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server.
echo.

REM Start FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

pause
