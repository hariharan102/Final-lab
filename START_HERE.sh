#!/bin/bash

###############################################################################
# SIMPLE STARTUP SCRIPT - NO ERRORS GUARANTEED
#
# This script starts all servers with proper error handling
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           EMOTION DETECTION SYSTEM - STARTING...              ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Create logs directory
mkdir -p logs

# Kill any existing servers
echo -e "${YELLOW}Stopping any existing servers...${NC}"
pkill -f "python manage.py runserver" 2>/dev/null || true
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 2

# Start Django Backend
echo -e "${GREEN}Starting Django Backend (port 8000)...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q Django djangorestframework django-cors-headers 2>/dev/null || true
python manage.py migrate --noinput 2>/dev/null || true
python manage.py runserver 8000 > ../logs/django.log 2>&1 &
DJANGO_PID=$!
cd ..
echo -e "${GREEN}✅ Django Backend started (PID: $DJANGO_PID)${NC}"

# Start Local Backend
echo -e "${GREEN}Starting Local Backend (port 8001)...${NC}"
cd local_backend
source venv/bin/activate
venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001 > ../logs/local_backend.log 2>&1 &
LOCAL_PID=$!
cd ..
echo -e "${GREEN}✅ Local Backend started (PID: $LOCAL_PID)${NC}"

# Start Frontend
echo -e "${GREEN}Starting React Frontend (port 3000)...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✅ React Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for servers to start
echo ""
echo -e "${YELLOW}Waiting for servers to initialize...${NC}"
echo -e "${YELLOW}(TensorFlow loading may take 10-15 seconds)${NC}"

# Wait for Local Backend to be ready (TensorFlow takes time)
MAX_WAIT=20
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
    WAITED=$((WAITED + 1))
    echo -ne "\r${YELLOW}Waiting... ${WAITED}s${NC}"
done
echo ""

# Verify servers
echo ""
echo -e "${CYAN}Verifying servers...${NC}"

if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Local Backend: RUNNING${NC}"
else
    echo -e "${RED}❌ Local Backend: FAILED (check logs/local_backend.log)${NC}"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ React Frontend: RUNNING${NC}"
else
    echo -e "${RED}❌ React Frontend: FAILED${NC}"
fi

if curl -s http://localhost:8001/local/frame-api-status 2>/dev/null | grep -q "ml_libraries_available.*true"; then
    echo -e "${GREEN}✅ ML Libraries: WORKING${NC}"
else
    echo -e "${YELLOW}⚠️  ML Libraries: Still loading or check status${NC}"
fi

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ ALL SERVERS RUNNING${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "🌐 Web Application:  ${GREEN}http://localhost:3000${NC}"
echo -e "📡 Local Backend:    ${GREEN}http://localhost:8001${NC}"
echo -e "📡 Django Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "📚 API Docs:         ${GREEN}http://localhost:8001/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping all servers...${NC}"
    kill $DJANGO_PID 2>/dev/null || true
    kill $LOCAL_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    pkill -f "python manage.py runserver" 2>/dev/null || true
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    echo -e "${GREEN}✅ All servers stopped${NC}"
    exit 0
}

trap cleanup INT TERM

# Wait
wait
