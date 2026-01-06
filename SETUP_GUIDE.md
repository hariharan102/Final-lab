# Complete Setup Guide - Emotion Detection System

## Quick Start (3 Steps)

### Step 1: Start All Servers
```bash
cd /Users/shyamali/Documents/CIDM/Final-lab
./run.sh
```

This single command starts:
- ✅ Django Backend (port 8000)
- ✅ Local Backend (port 8001) 
- ✅ React Frontend (port 3000)

### Step 2: Open the Web Application
Open your browser and visit:
```
http://localhost:3000
```

### Step 3: Install Browser Extension (Optional)
See "Browser Extension Setup" section below.

---

## What Gets Started

When you run `./run.sh`, the following happens:

### 1. Django Backend (Port 8000)
- **Purpose**: Google Colab integration for GPU processing
- **URL**: http://localhost:8000
- **API**: http://localhost:8000/api/
- **Features**: Video upload to Google Drive, Colab notebook integration

### 2. Local Backend (Port 8001)
- **Purpose**: Local CPU processing + Frame-by-frame API
- **URL**: http://localhost:8001
- **Frame API**: http://localhost:8001/local/process-frame
- **API Docs**: http://localhost:8001/docs
- **Features**: 
  - Batch video processing (local)
  - Real-time frame-by-frame emotion detection
  - Face tracking across frames

### 3. React Frontend (Port 3000)
- **Purpose**: Web UI for video upload and results
- **URL**: http://localhost:3000
- **Features**:
  - Execution mode toggle (Local Machine / Google Colab)
  - Video upload interface
  - Live processing status
  - Results visualization

---

## Browser Extension Setup

The browser extension captures your screen/tab and sends frames to the Frame API for real-time emotion detection.

### Installation Steps

#### 1. Open Chrome Extensions Page
```
chrome://extensions/
```

#### 2. Enable Developer Mode
- Toggle "Developer mode" in the top-right corner

#### 3. Load Extension
- Click "Load unpacked"
- Navigate to: `/Users/shyamali/Documents/CIDM/Final-lab/emotion`
- Click "Select"

#### 4. Verify Installation
- You should see "Emotion Screen Capture" in your extensions list
- Pin the extension to your toolbar (optional)

### Using the Extension

#### 1. Start the Local Backend
The extension requires the local backend to be running:
```bash
cd /Users/shyamali/Documents/CIDM/Final-lab
./run.sh
```

#### 2. Open Extension Dashboard
- Click the extension icon in your toolbar
- A new tab will open with the dashboard

#### 3. Start Capturing
- Click "Start Capture"
- Select the screen/tab you want to capture
- The extension will:
  - Capture frames at 2 FPS
  - Process 1 out of every 10 frames (to reduce load)
  - Send frames to: `http://localhost:8001/local/process-frame`
  - Display emotion results in real-time

#### 4. View Results
- Live emotion logs appear in the dashboard
- Shows: Person ID, dominant emotion, emotion scores
- Click "Download CSV" to export data

#### 5. Stop Capturing
- Click "Stop" button
- Or close the captured tab/window

### Extension Configuration

The extension is configured in `emotion/dashboard.js`:

```javascript
const SERVER='http://localhost:8001/local/process-frame';
const FPS=2;              // Capture 2 frames per second
const FRAME_SKIP=10;      // Process 1 out of every 10 frames
const MAX_WIDTH=640;      // Max frame width
```

**Frame Processing Rate**: 
- Captures: 2 FPS
- Processes: 0.2 FPS (1 out of 10 frames)
- This reduces CPU load while maintaining good emotion tracking

---

## Stopping the Servers

Press `Ctrl+C` in the terminal where `run.sh` is running.

This will automatically stop all three servers.

---

## Troubleshooting

### Port Already in Use
If you see "port already in use" errors:
```bash
# Kill processes on specific ports
lsof -ti:8000 | xargs kill -9  # Django
lsof -ti:8001 | xargs kill -9  # Local Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

Then run `./run.sh` again.

### ML Libraries Not Installed (Local Backend)
The local backend requires ML libraries for emotion detection:

```bash
cd local_backend
source venv/bin/activate
pip install insightface deepface onnxruntime
```

**Note**: These require Python 3.9-3.12. If you have Python 3.14, you'll need to install an older Python version.

### Extension Not Working

**Check 1**: Is the local backend running?
```bash
curl http://localhost:8001/local/frame-api-status
```

**Check 2**: Check browser console for errors
- Right-click on extension dashboard → Inspect
- Look for network errors or API failures

**Check 3**: Verify extension permissions
- Go to `chrome://extensions/`
- Click "Details" on Emotion Screen Capture
- Ensure "http://localhost:8001/*" is in permissions

### Frontend Not Loading

**Check 1**: Is the server running?
```bash
curl http://localhost:3000
```

**Check 2**: Check logs
```bash
cat logs/frontend.log
```

**Check 3**: Reinstall dependencies
```bash
cd frontend
rm -rf node_modules
npm install
```

---

## File Structure

```
Final-lab/
├── run.sh                    # ⭐ MAIN STARTUP SCRIPT
├── backend/                  # Django backend (port 8000)
│   ├── venv/
│   ├── manage.py
│   └── ...
├── local_backend/            # Local backend (port 8001)
│   ├── venv/
│   ├── main.py
│   ├── frame_api.py         # Frame-by-frame API
│   └── run.sh               # Can also start local backend alone
├── frontend/                 # React frontend (port 3000)
│   ├── node_modules/
│   ├── src/
│   └── package.json
├── emotion/                  # Browser extension
│   ├── manifest.json
│   ├── dashboard.html
│   └── dashboard.js
└── logs/                     # Server logs (created automatically)
    ├── django.log
    ├── local_backend.log
    └── frontend.log
```

---

## API Endpoints Reference

### Django Backend (Port 8000)
```
POST   /api/jobs/upload          # Upload video to Google Drive
GET    /api/jobs/{id}/status     # Get job status
GET    /api/jobs/{id}/results    # Get processing results
```

### Local Backend (Port 8001)
```
# Video Processing
POST   /local/jobs/upload        # Upload video for local processing
GET    /local/jobs/{id}/status   # Get job status
GET    /local/jobs/{id}/results  # Get results

# Frame API (for extension)
POST   /local/process-frame      # Process single frame
POST   /local/reset-tracker      # Reset face tracker
GET    /local/frame-api-status   # Check API status

# Documentation
GET    /docs                     # Swagger UI
GET    /redoc                    # ReDoc
```

---

## Development Tips

### View Server Logs
```bash
# Django
tail -f logs/django.log

# Local Backend
tail -f logs/local_backend.log

# Frontend
tail -f logs/frontend.log
```

### Start Servers Individually

**Django only:**
```bash
cd backend
source venv/bin/activate
python manage.py runserver 8000
```

**Local Backend only:**
```bash
cd local_backend
./run.sh
```

**Frontend only:**
```bash
cd frontend
npm run dev
```

### Test Frame API
```bash
# Test with curl
curl -X POST http://localhost:8001/local/process-frame \
  -F "frame=@test_image.jpg"

# Check status
curl http://localhost:8001/local/frame-api-status
```

---

## Next Steps

1. **Start the system**: `./run.sh`
2. **Open web app**: http://localhost:3000
3. **Install extension**: Load from `emotion/` folder
4. **Test frame API**: Use extension to capture screen

For detailed API documentation, visit:
- http://localhost:8001/docs (when server is running)

For frame API examples and advanced usage:
- See `local_backend/FRAME_API_GUIDE.md`
