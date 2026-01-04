@echo off
REM Quick Setup Script for Emotion Detection System
REM This script helps set up both backend and frontend

echo ========================================
echo Emotion Detection System - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

echo Python and Node.js detected!
echo.

REM Setup backend
echo ========================================
echo Setting up Django Backend...
echo ========================================
cd backend

echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Running Django migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo ========================================
echo Backend setup complete!
echo ========================================
echo.

REM Setup frontend
echo ========================================
echo Setting up React Frontend...
echo ========================================
cd ..\frontend

echo Installing Node.js dependencies...
call npm install

echo.
echo ========================================
echo Frontend setup complete!
echo ========================================
echo.

cd ..

REM Final instructions
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo NEXT STEPS:
echo.
echo 1. Set up Google Drive API:
echo    - Go to https://console.cloud.google.com/
echo    - Create project and enable Google Drive API
echo    - Download credentials.json to backend/
echo    - See backend/README.md for details
echo.
echo 2. Update Colab notebook URL:
echo    - Edit backend/emotion_backend/settings.py
echo    - Set COLAB_NOTEBOOK_URL
echo.
echo 3. Upload colab_template.ipynb to Google Colab
echo.
echo 4. Start the application:
echo.
echo    Backend:
echo      cd backend
echo      venv\Scripts\activate
echo      python manage.py runserver
echo.
echo    Frontend (in new terminal):
echo      cd frontend
echo      npm run dev
echo.
echo 5. Open http://localhost:3000 in your browser
echo.
echo ========================================
echo For detailed instructions, see README.md
echo ========================================
echo.
pause
