# Frame-by-Frame Emotion Detection API

## Quick Start

### Start the Server
```bash
cd /Users/shyamali/Documents/CIDM/Final-lab/local_backend
./run.sh
```

Server runs on: **http://localhost:8001**

### Test the API
```bash
# Process a single frame
curl -X POST http://localhost:8001/local/process-frame \
  -F "frame=@your_image.jpg"
```

## What This API Does

This API exposes a **frame-by-frame emotion detection endpoint** that:
- ✅ Accepts individual image frames
- ✅ Detects faces using InsightFace (same as core pipeline)
- ✅ Tracks faces across frames (maintains person IDs)
- ✅ Detects emotions using DeepFace (same as core pipeline)
- ✅ Returns JSON with face locations and emotions
- ✅ **Does NOT modify core ML code** - only wraps existing functionality

## Key Endpoints

### 1. Process Frame (Main Endpoint)
```
POST /local/process-frame
```

**Parameters:**
- `frame`: Image file (JPEG, PNG, etc.)
- `reset_tracker`: Boolean (optional, default: false)

**Response:**
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
        "happy": 0.85,
        "neutral": 0.10,
        "sad": 0.03
      }
    }
  ],
  "total_faces": 1
}
```

### 2. Reset Tracker
```
POST /local/reset-tracker
```
Call this when starting a new video sequence.

### 3. API Status
```
GET /local/frame-api-status
```
Check if models are loaded and ready.

## Python Example

```python
import requests
import cv2

# Reset tracker for new video
requests.post('http://localhost:8001/local/reset-tracker')

# Open video
cap = cv2.VideoCapture('video.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Encode frame as JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    
    # Send to API
    response = requests.post(
        'http://localhost:8001/local/process-frame',
        files={'frame': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
    )
    
    result = response.json()
    
    # Process results
    for face in result['faces']:
        print(f"Person {face['person_id']}: {face['emotion']}")

cap.release()
```

## Architecture

```
┌─────────────────┐
│  Your App       │
│  (Python/JS)    │
└────────┬────────┘
         │ HTTP POST
         │ (frame image)
         ▼
┌─────────────────┐
│  Frame API      │
│  /process-frame │
└────────┬────────┘
         │
         ├──▶ InsightFace (face detection)
         │
         ├──▶ FaceTracker (person IDs)
         │
         └──▶ DeepFace (emotion detection)
```

## Important Notes

1. **Core Code Untouched**: The frame API uses the existing ML pipeline from `pipeline/face_detection.py` and `pipeline/emotion_detection.py` without modifications.

2. **Face Tracking**: Person IDs persist across frames. The same person keeps the same ID throughout the video.

3. **Performance**: CPU-based processing runs at ~1-3 FPS. For real-time applications, consider:
   - Processing every 3rd or 5th frame
   - Reducing frame resolution
   - Using the batch video API for offline processing

4. **Python Version**: ML libraries (InsightFace, DeepFace) require Python 3.9-3.12.

## Files Created

- `frame_api.py` - Frame processing endpoint implementation
- `run.sh` - Startup script with configuration options
- `FRAME_API_GUIDE.md` - Comprehensive usage guide with examples

## Interactive Documentation

Visit these URLs when the server is running:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Troubleshooting

**Models not loading?**
```bash
pip install insightface deepface onnxruntime
```

**Slow processing?**
- Reduce frame size before sending
- Skip frames (process every Nth frame)
- Use batch video API for offline processing

**Tracking issues?**
- Call `/local/reset-tracker` when starting new videos
- Ensure frames are sent in sequence

For detailed examples and advanced usage, see `FRAME_API_GUIDE.md`.
