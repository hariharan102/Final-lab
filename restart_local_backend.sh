#!/bin/bash

# Restart Local Backend Script
# Use this when you make changes to local_backend code

echo "🔄 Restarting Local Backend..."

# Kill existing local backend process
pkill -f "uvicorn main:app.*8001"
sleep 2

# Start local backend
cd local_backend
source venv/bin/activate
nohup venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001 > ../logs/local_backend.log 2>&1 &
LOCAL_PID=$!
cd ..

echo "✅ Local Backend restarted (PID: $LOCAL_PID)"
echo "📝 Logs: logs/local_backend.log"
echo ""
echo "Wait 5-10 seconds for TensorFlow to load, then process a new video."
