@echo off
REM ============================================
REM Dual Backend Startup Script
REM ============================================
REM
REM This script starts BOTH backends:
REM   - Colab Backend (Django) on port 8000
REM   - Local Backend (FastAPI) on port 8001
REM
REM You can then switch between modes in the frontend.
REM ============================================

echo.
echo ============================================
echo   DUAL BACKEND STARTUP
echo ============================================
echo.
echo Starting both backends for full dual-mode support...
echo.

REM Start Colab Backend (Django) in a new terminal
echo Starting Colab Backend (port 8000)...
start "Colab Backend (8000)" cmd /k "cd backend && python manage.py runserver 8000"

REM Wait a moment for Django to start
timeout /t 3 /nobreak >nul

REM Start Local Backend (FastAPI) in a new terminal  
echo Starting Local Backend (port 8001)...
start "Local Backend (8001)" cmd /k "cd local_backend && call start_local_backend.bat"

echo.
echo ============================================
echo   BACKENDS STARTING...
echo ============================================
echo.
echo   Colab Backend (Django):  http://localhost:8000
echo   Local Backend (FastAPI): http://localhost:8001
echo.
echo   Frontend should be started separately:
echo   cd frontend ^&^& npm run dev
echo.
echo ============================================
echo.

pause
