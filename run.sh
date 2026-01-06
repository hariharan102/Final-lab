#!/bin/bash

###############################################################################
# Unified Startup Script - Emotion Detection System
#
# This script starts ALL required servers:
# 1. Django Backend (port 8000) - Google Colab integration
# 2. Local Backend (port 8001) - Local CPU processing + Frame API
# 3. React Frontend (port 3000) - Web UI
#
# Usage:
#   ./run.sh                    # Start all servers
#   ./run.sh --help             # Show help
###############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
DJANGO_PORT=8000
LOCAL_PORT=8001
FRONTEND_PORT=3000

# Parse arguments
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Unified Startup Script - Emotion Detection System"
    echo ""
    echo "Usage: ./run.sh"
    echo ""
    echo "This script starts all required servers:"
    echo "  - Django Backend (port 8000)"
    echo "  - Local Backend (port 8001)"
    echo "  - React Frontend (port 3000)"
    echo ""
    echo "Press Ctrl+C to stop all servers"
    exit 0
fi

# Print banner
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║     EMOTION DETECTION SYSTEM - UNIFIED STARTUP SCRIPT         ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}⚠️  Port $port is in use (PID: $pid). Killing process...${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Create logs directory if it doesn't exist
mkdir -p logs

# Check and clean up ports
echo -e "${BLUE}🔍 Checking ports...${NC}"
for port in $DJANGO_PORT $LOCAL_PORT $FRONTEND_PORT; do
    if check_port $port; then
        kill_port $port
    fi
done
echo -e "${GREEN}✅ All ports are available${NC}"
echo ""

# ============================================================================
# 1. DJANGO BACKEND (Port 8000)
# ============================================================================
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}1. DJANGO BACKEND (Google Colab Integration)${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

cd backend

# Check virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Django venv not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate and check dependencies
source venv/bin/activate
if ! python -c "import django" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing Django dependencies...${NC}"
    pip install -q Django djangorestframework django-cors-headers google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv Pillow opencv-python numpy requests
fi

# Run migrations if needed
if [ ! -f "db.sqlite3" ]; then
    echo -e "${BLUE}📦 Running Django migrations...${NC}"
    python manage.py migrate --noinput
fi

# Start Django backend in background
echo -e "${GREEN}🚀 Starting Django backend on port $DJANGO_PORT...${NC}"
python manage.py runserver $DJANGO_PORT > ../logs/django.log 2>&1 &
DJANGO_PID=$!
echo -e "${GREEN}✅ Django backend started (PID: $DJANGO_PID)${NC}"
echo ""

cd ..

# ============================================================================
# 2. LOCAL BACKEND (Port 8001)
# ============================================================================
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}2. LOCAL BACKEND (CPU Processing + Frame API)${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

cd local_backend

# Check virtual environment - use Python 3.12 for ML library compatibility
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Local backend venv not found. Creating with Python 3.12...${NC}"
    if command -v /usr/local/bin/python3.12 &> /dev/null; then
        /usr/local/bin/python3.12 -m venv venv
    elif command -v python3.12 &> /dev/null; then
        python3.12 -m venv venv
    else
        echo -e "${RED}❌ Python 3.12 not found. ML libraries require Python 3.9-3.12${NC}"
        python3 -m venv venv
    fi
fi

# Activate and check dependencies
source venv/bin/activate
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing FastAPI dependencies...${NC}"
    pip install -q fastapi uvicorn python-multipart python-dotenv aiofiles opencv-python numpy Pillow
fi

# Upgrade SQLAlchemy for Python 3.14 compatibility
if ! python -c "import sqlalchemy; assert sqlalchemy.__version__ >= '2.0.45'" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Upgrading SQLAlchemy for Python 3.14...${NC}"
    pip install -q --upgrade sqlalchemy
fi

# Check and install ML libraries if missing
ML_READY=true
if ! python -c "import insightface" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  InsightFace not installed. Installing ML libraries...${NC}"
    pip install -q numpy opencv-python insightface onnxruntime deepface tf-keras 'numpy<2.0,>=1.26' 'ml-dtypes~=0.3.1'
    ML_READY=false
fi
if ! python -c "import deepface" 2>/dev/null; then
    if [ "$ML_READY" = true ]; then
        echo -e "${YELLOW}⚠️  DeepFace not installed. Installing...${NC}"
        pip install -q deepface tf-keras 'numpy<2.0,>=1.26' 'ml-dtypes~=0.3.1'
    fi
    ML_READY=false
fi

# Verify installation
if python -c "import insightface; import deepface" 2>/dev/null; then
    echo -e "${GREEN}✅ ML libraries available and working${NC}"
else
    echo -e "${YELLOW}⚠️  ML libraries installation incomplete. Frame API may not work.${NC}"
fi

# Start local backend in background
echo -e "${GREEN}🚀 Starting Local backend on port $LOCAL_PORT...${NC}"
uvicorn main:app --host 0.0.0.0 --port $LOCAL_PORT > ../logs/local_backend.log 2>&1 &
LOCAL_PID=$!
echo -e "${GREEN}✅ Local backend started (PID: $LOCAL_PID)${NC}"
echo ""

cd ..

# ============================================================================
# 3. REACT FRONTEND (Port 3000)
# ============================================================================
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}3. REACT FRONTEND (Web UI)${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

cd frontend

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing...${NC}"
    npm install
fi

# Start frontend in background
echo -e "${GREEN}🚀 Starting React frontend on port $FRONTEND_PORT...${NC}"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ React frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

cd ..

# ============================================================================
# SUMMARY
# ============================================================================
sleep 3  # Give servers time to start

echo -e "${MAGENTA}════════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}                    ALL SERVERS RUNNING                         ${NC}"
echo -e "${MAGENTA}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✅ Django Backend:${NC}       http://localhost:$DJANGO_PORT"
echo -e "${GREEN}✅ Local Backend:${NC}        http://localhost:$LOCAL_PORT"
echo -e "${GREEN}✅ React Frontend:${NC}       http://localhost:$FRONTEND_PORT"
echo ""
echo -e "${BLUE}📡 Available APIs:${NC}"
echo -e "   ${CYAN}Django API:${NC}           http://localhost:$DJANGO_PORT/api/"
echo -e "   ${CYAN}Local Video API:${NC}      http://localhost:$LOCAL_PORT/local/jobs/upload"
echo -e "   ${CYAN}Frame API:${NC}            http://localhost:$LOCAL_PORT/local/process-frame"
echo -e "   ${CYAN}API Docs:${NC}             http://localhost:$LOCAL_PORT/docs"
echo ""
echo -e "${BLUE}🌐 Browser Extension:${NC}"
echo -e "   The extension at ${CYAN}emotion/${NC} is configured to use:"
echo -e "   ${CYAN}http://localhost:$LOCAL_PORT/local/process-frame${NC}"
echo ""
echo -e "${YELLOW}📝 Process IDs:${NC}"
echo -e "   Django:   $DJANGO_PID"
echo -e "   Local:    $LOCAL_PID"
echo -e "   Frontend: $FRONTEND_PID"
echo ""
echo -e "${YELLOW}📋 Logs:${NC}"
echo -e "   Django:   logs/django.log"
echo -e "   Local:    logs/local_backend.log"
echo -e "   Frontend: logs/frontend.log"
echo ""
echo -e "${RED}Press Ctrl+C to stop all servers${NC}"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping all servers...${NC}"
    
    if [ ! -z "$DJANGO_PID" ]; then
        kill $DJANGO_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Django backend stopped${NC}"
    fi
    
    if [ ! -z "$LOCAL_PID" ]; then
        kill $LOCAL_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Local backend stopped${NC}"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ React frontend stopped${NC}"
    fi
    
    # Kill any remaining processes on the ports
    kill_port $DJANGO_PORT
    kill_port $LOCAL_PORT
    kill_port $FRONTEND_PORT
    
    echo -e "${GREEN}✅ All servers stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Wait for all background processes
wait
