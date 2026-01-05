# Emotion Screen Capture - Browser Extension

## Overview

This Chrome extension captures your screen or tab in real-time and sends frames to the Local Backend Frame API for emotion detection. It displays live emotion results and allows you to export data as CSV.

## Features

- ✅ Screen/Tab capture at 2 FPS
- ✅ Smart frame skipping (processes 1 out of 10 frames)
- ✅ Real-time emotion detection via Frame API
- ✅ Face tracking with Person IDs
- ✅ Live emotion logs
- ✅ CSV export for analysis

## Installation

### Prerequisites

The Local Backend must be running on port 8001:
```bash
cd /Users/shyamali/Documents/CIDM/Final-lab
./run.sh
```

### Install Extension

1. **Open Chrome Extensions**
   ```
   chrome://extensions/
   ```

2. **Enable Developer Mode**
   - Toggle the switch in the top-right corner

3. **Load Extension**
   - Click "Load unpacked"
   - Navigate to: `/Users/shyamali/Documents/CIDM/Final-lab/emotion`
   - Click "Select"

4. **Verify**
   - Extension should appear in your extensions list
   - Pin it to toolbar for easy access

## Usage

### 1. Start Capturing

1. Click the extension icon in your toolbar
2. A new tab opens with the dashboard
3. Click "Start Capture"
4. Select the screen/tab/window you want to capture
5. Click "Share"

### 2. Monitor Results

The dashboard shows:
- **Live Logs**: Real-time emotion detection results
- **Person ID**: Tracked person identifier
- **Dominant Emotion**: Primary detected emotion
- **Emotion Scores**: Confidence scores for each emotion

Example log entry:
```
12:34:56 PM — Person 1 | emotion=happy | angry=0.02 fear=0.01 happy=0.85 neutral=0.10 sad=0.02
```

### 3. Export Data

Click "Download CSV" to export all captured data:
- Timestamp
- Person ID
- Dominant emotion
- All emotion scores (angry, disgust, fear, happy, neutral, sad, surprise)

### 4. Stop Capturing

- Click "Stop" button
- Or close the captured tab/window

## Configuration

Edit `dashboard.js` to customize:

```javascript
const SERVER='http://localhost:8001/local/process-frame';
const FPS=2;              // Frames captured per second
const FRAME_SKIP=10;      // Process 1 out of every N frames
const MAX_WIDTH=640;      // Maximum frame width (pixels)
```

### Frame Processing Rate

- **Capture Rate**: 2 FPS (2 frames captured per second)
- **Processing Rate**: 0.2 FPS (1 out of 10 frames processed)
- **Effective Rate**: 1 frame processed every 5 seconds

This reduces CPU load while maintaining good emotion tracking.

## How It Works

```
┌─────────────────┐
│  Screen/Tab     │
│  Capture        │
└────────┬────────┘
         │ 2 FPS
         ▼
┌─────────────────┐
│  Frame Counter  │
│  (Skip 9/10)    │
└────────┬────────┘
         │ 0.2 FPS
         ▼
┌─────────────────┐
│  Frame API      │
│  localhost:8001 │
└────────┬────────┘
         │
         ├──▶ Face Detection (InsightFace)
         ├──▶ Face Tracking (Person IDs)
         └──▶ Emotion Detection (DeepFace)
         │
         ▼
┌─────────────────┐
│  Dashboard      │
│  (Live Logs)    │
└─────────────────┘
```

## API Integration

The extension calls the Frame API endpoint:

**Endpoint**: `POST http://localhost:8001/local/process-frame`

**Request**:
```javascript
FormData {
  frame: Blob (JPEG image)
}
```

**Response**:
```json
{
  "frame_processed": true,
  "faces": [
    {
      "person_id": 1,
      "bbox": {"x1": 150, "y1": 200, "x2": 350, "y2": 450},
      "confidence": 0.98,
      "emotion": "happy",
      "emotion_scores": {
        "angry": 0.02,
        "disgust": 0.01,
        "fear": 0.01,
        "happy": 0.85,
        "neutral": 0.10,
        "sad": 0.02,
        "surprise": 0.01
      }
    }
  ],
  "total_faces": 1
}
```

## Files

- `manifest.json` - Extension configuration
- `background.js` - Extension background script
- `dashboard.html` - Dashboard UI
- `dashboard.js` - Dashboard logic and API integration
- `dashboard.css` - Dashboard styles

## Troubleshooting

### Extension Not Working

**Problem**: No emotion results appearing

**Solutions**:
1. Check if Local Backend is running:
   ```bash
   curl http://localhost:8001/local/frame-api-status
   ```

2. Check browser console (F12) for errors

3. Verify extension has correct permissions:
   - Go to `chrome://extensions/`
   - Click "Details" on Emotion Screen Capture
   - Check "Permissions" section

### API Connection Failed

**Problem**: "POST error: Failed to fetch"

**Solutions**:
1. Ensure Local Backend is running on port 8001
2. Check CORS settings in `local_backend/main.py`
3. Verify firewall isn't blocking localhost:8001

### No Faces Detected

**Problem**: "No faces detected in frame"

**Solutions**:
1. Ensure your face is visible in the captured screen/tab
2. Improve lighting conditions
3. Move closer to the camera
4. Check ML libraries are installed:
   ```bash
   cd local_backend
   source venv/bin/activate
   python -c "import insightface; import deepface"
   ```

### Slow Performance

**Problem**: Extension is slow or laggy

**Solutions**:
1. Increase `FRAME_SKIP` value (process fewer frames)
2. Decrease `FPS` value (capture fewer frames)
3. Reduce `MAX_WIDTH` (smaller frame size)

Example for lower CPU usage:
```javascript
const FPS=1;              // 1 frame per second
const FRAME_SKIP=15;      // Process 1 out of 15 frames
const MAX_WIDTH=480;      // Smaller frames
```

## Privacy & Security

- All processing happens locally on your machine
- No data is sent to external servers
- Captured frames are processed in real-time and not stored
- CSV export contains only emotion data (no images)

## Permissions

The extension requires:
- `storage` - Save settings
- `http://localhost:8001/*` - Access Frame API

## Development

### Modify the Extension

1. Edit files in the `emotion/` directory
2. Go to `chrome://extensions/`
3. Click the reload icon on the extension card
4. Test your changes

### Debug

1. Right-click on extension icon → "Inspect popup"
2. Or open dashboard and press F12
3. Check Console tab for errors
4. Check Network tab for API calls

## Version History

- **v5.1** - Updated to use Frame API (port 8001)
  - Added frame skipping (1 out of 10 frames)
  - Added Person ID tracking
  - Updated API endpoint to `/local/process-frame`
  - Added CSV export with Person IDs

## Support

For issues or questions:
1. Check Local Backend logs: `logs/local_backend.log`
2. Check browser console for errors
3. Verify ML libraries are installed
4. See main project README for setup instructions
