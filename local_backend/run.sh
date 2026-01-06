#!/bin/bash

###############################################################################
# Local Backend Startup Script
#
# This script starts the Local Emotion Detection Backend (FastAPI) with:
# - Video processing API (batch upload)
# - Frame-by-frame emotion detection API (real-time)
#
# The frame API exposes an endpoint to process individual frames without
# touching the core ML pipeline code.
#
# Usage:
#   ./run.sh                    # Start server on port 8001
#   ./run.sh --port 8002        # Start on custom port
#   ./run.sh --help             # Show help
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
PORT=8001
HOST="0.0.0.0"
RELOAD="--reload"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --no-reload)
            RELOAD=""
            shift
            ;;
        --help|-h)
            echo "Local Backend Startup Script"
            echo ""
            echo "Usage: ./run.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --port PORT       Port to run on (default: 8001)"
            echo "  --host HOST       Host to bind to (default: 0.0.0.0)"
            echo "  --no-reload       Disable auto-reload on code changes"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run.sh                    # Start on port 8001 with auto-reload"
            echo "  ./run.sh --port 8002        # Start on port 8002"
            echo "  ./run.sh --no-reload        # Production mode (no auto-reload)"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Print banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        LOCAL EMOTION DETECTION BACKEND - STARTUP SCRIPT       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found!${NC}"
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
    echo ""
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if dependencies are installed
echo -e "${BLUE}🔍 Checking dependencies...${NC}"
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependencies not installed!${NC}"
    echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
    echo ""
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
    echo ""
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}🐍 Python version: ${PYTHON_VERSION}${NC}"

# Check if ML libraries are available
echo -e "${BLUE}🤖 Checking ML libraries...${NC}"
ML_READY=true

if ! python -c "import insightface" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  InsightFace not installed (face detection will fail)${NC}"
    ML_READY=false
fi

if ! python -c "import deepface" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  DeepFace not installed (emotion detection will fail)${NC}"
    ML_READY=false
fi

if [ "$ML_READY" = false ]; then
    echo -e "${YELLOW}⚠️  Some ML libraries are missing!${NC}"
    echo -e "${YELLOW}   The server will start, but ML processing will fail.${NC}"
    echo -e "${YELLOW}   Install with: pip install insightface deepface onnxruntime${NC}"
    echo -e "${YELLOW}   Note: These require Python 3.9-3.12${NC}"
    echo ""
else
    echo -e "${GREEN}✅ ML libraries available${NC}"
    echo ""
fi

# Display configuration
echo -e "${BLUE}⚙️  Configuration:${NC}"
echo -e "   Host: ${GREEN}${HOST}${NC}"
echo -e "   Port: ${GREEN}${PORT}${NC}"
echo -e "   Auto-reload: ${GREEN}$([ -n "$RELOAD" ] && echo "enabled" || echo "disabled")${NC}"
echo ""

# Display available endpoints
echo -e "${BLUE}📡 Available API Endpoints:${NC}"
echo -e "   ${GREEN}POST${NC}   http://localhost:${PORT}/local/jobs/upload"
echo -e "          → Upload video for batch processing"
echo -e ""
echo -e "   ${GREEN}POST${NC}   http://localhost:${PORT}/local/process-frame"
echo -e "          → Process single frame (real-time emotion detection)"
echo -e ""
echo -e "   ${GREEN}GET${NC}    http://localhost:${PORT}/local/jobs/{id}/status"
echo -e "          → Get job status"
echo -e ""
echo -e "   ${GREEN}GET${NC}    http://localhost:${PORT}/local/jobs/{id}/results"
echo -e "          → Get processing results"
echo -e ""
echo -e "   ${GREEN}POST${NC}   http://localhost:${PORT}/local/reset-tracker"
echo -e "          → Reset face tracker (for new video sequence)"
echo -e ""
echo -e "   ${GREEN}GET${NC}    http://localhost:${PORT}/docs"
echo -e "          → Interactive API documentation (Swagger UI)"
echo -e ""

# Display frame API usage example
echo -e "${BLUE}💡 Frame API Usage Example:${NC}"
echo -e "${YELLOW}curl -X POST http://localhost:${PORT}/local/process-frame \\${NC}"
echo -e "${YELLOW}  -F 'frame=@/path/to/image.jpg' \\${NC}"
echo -e "${YELLOW}  -F 'reset_tracker=false'${NC}"
echo ""

# Start the server
echo -e "${GREEN}🚀 Starting Local Backend Server...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Run uvicorn
uvicorn main:app --host "$HOST" --port "$PORT" $RELOAD --log-level info
