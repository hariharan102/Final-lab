# Frame-by-Frame Emotion Detection API Guide

## Overview

The Frame API provides real-time emotion detection for individual video frames. This allows you to:
- Process frames one at a time without uploading entire videos
- Get immediate emotion detection results
- Track faces across multiple frames
- Build real-time video processing applications

**Important**: This API does NOT modify the core ML pipeline code. It uses the same face detection and emotion recognition logic as the batch video processor.

## Quick Start

### 1. Start the Server

```bash
cd /Users/shyamali/Documents/CIDM/Final-lab/local_backend
./run.sh
```

The server will start on `http://localhost:8001`

### 2. Process Your First Frame

```bash
curl -X POST http://localhost:8001/local/process-frame \
  -F "frame=@/path/to/your/image.jpg" \
  -F "reset_tracker=false"
```

## API Endpoints

### 1. Process Frame

**Endpoint**: `POST /local/process-frame`

**Description**: Process a single image frame and detect emotions

**Parameters**:
- `frame` (file, required): Image file (JPEG, PNG, etc.)
- `reset_tracker` (boolean, optional): Reset face tracker for new video sequence (default: false)

**Request Example**:
```bash
curl -X POST http://localhost:8001/local/process-frame \
  -F "frame=@frame001.jpg" \
  -F "reset_tracker=false"
```

**Response Example**:
```json
{
  "frame_processed": true,
  "faces": [
    {
      "person_id": 1,
      "bbox": {
        "x1": 150,
        "y1": 200,
        "x2": 350,
        "y2": 450
      },
      "confidence": 0.98,
      "emotion": "happy",
      "emotion_scores": {
        "happy": 0.85,
        "neutral": 0.10,
        "sad": 0.03,
        "angry": 0.01,
        "surprise": 0.01
      },
      "face_width": 200,
      "face_height": 250
    }
  ],
  "total_faces": 1,
  "frame_dimensions": {
    "width": 1920,
    "height": 1080
  }
}
```

### 2. Reset Face Tracker

**Endpoint**: `POST /local/reset-tracker`

**Description**: Reset the face tracker (call this when starting a new video)

**Request Example**:
```bash
curl -X POST http://localhost:8001/local/reset-tracker
```

**Response**:
```json
{
  "success": true,
  "message": "Face tracker reset successfully"
}
```

### 3. Check API Status

**Endpoint**: `GET /local/frame-api-status`

**Description**: Check if models are loaded and ready

**Request Example**:
```bash
curl http://localhost:8001/local/frame-api-status
```

**Response**:
```json
{
  "status": "ready",
  "face_analyzer_loaded": true,
  "face_tracker_active": true,
  "active_tracked_people": 2
}
```

## Usage Patterns

### Pattern 1: Single Frame Processing

Process one frame at a time without tracking:

```python
import requests

# Process a single frame
with open('frame.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/local/process-frame',
        files={'frame': f},
        data={'reset_tracker': 'true'}  # Reset for each frame
    )
    
result = response.json()
print(f"Detected {result['total_faces']} faces")
for face in result['faces']:
    print(f"Person {face['person_id']}: {face['emotion']}")
```

### Pattern 2: Video Stream Processing

Process frames from a video with face tracking:

```python
import cv2
import requests

# Open video
cap = cv2.VideoCapture('video.mp4')

# Reset tracker at start
requests.post('http://localhost:8001/local/reset-tracker')

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Encode frame as JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    
    # Send to API
    response = requests.post(
        'http://localhost:8001/local/process-frame',
        files={'frame': ('frame.jpg', buffer.tobytes(), 'image/jpeg')},
        data={'reset_tracker': 'false'}  # Keep tracking
    )
    
    result = response.json()
    
    # Draw results on frame
    for face in result['faces']:
        bbox = face['bbox']
        emotion = face['emotion']
        person_id = face['person_id']
        
        # Draw bounding box
        cv2.rectangle(frame, 
                     (bbox['x1'], bbox['y1']), 
                     (bbox['x2'], bbox['y2']), 
                     (0, 255, 0), 2)
        
        # Draw label
        label = f"Person {person_id}: {emotion}"
        cv2.putText(frame, label, 
                   (bbox['x1'], bbox['y1'] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Display
    cv2.imshow('Emotion Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    frame_count += 1

cap.release()
cv2.destroyAllWindows()
```

### Pattern 3: Webcam Real-Time Processing

Process webcam feed in real-time:

```python
import cv2
import requests
import time

# Reset tracker
requests.post('http://localhost:8001/local/reset-tracker')

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Encode frame
    _, buffer = cv2.imencode('.jpg', frame)
    
    # Send to API (process every frame or skip frames for performance)
    try:
        response = requests.post(
            'http://localhost:8001/local/process-frame',
            files={'frame': ('frame.jpg', buffer.tobytes(), 'image/jpeg')},
            data={'reset_tracker': 'false'},
            timeout=1.0  # 1 second timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Draw results
            for face in result['faces']:
                bbox = face['bbox']
                emotion = face['emotion']
                person_id = face['person_id']
                
                cv2.rectangle(frame, 
                             (bbox['x1'], bbox['y1']), 
                             (bbox['x2'], bbox['y2']), 
                             (0, 255, 0), 2)
                
                label = f"P{person_id}: {emotion}"
                cv2.putText(frame, label, 
                           (bbox['x1'], bbox['y1'] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    except requests.exceptions.Timeout:
        print("Request timeout, skipping frame")
    
    cv2.imshow('Webcam Emotion Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## Face Tracking

The API maintains face tracking state across frames:

- **Person IDs**: Each detected person gets a unique ID (1, 2, 3, ...)
- **Tracking**: The same person keeps the same ID across frames
- **Persistence**: IDs persist until the person disappears for 30 frames
- **Reset**: Call `/local/reset-tracker` to clear all tracking state

### When to Reset Tracker

- Starting a new video
- Switching camera feeds
- When tracking becomes unreliable
- After long pauses in processing

## Performance Considerations

### Frame Rate
- CPU processing: ~1-3 FPS (depends on hardware)
- Consider skipping frames for real-time applications
- Process every 3rd or 5th frame for smoother performance

### Optimization Tips
1. **Reduce frame size**: Resize frames before sending
2. **Skip frames**: Process every Nth frame
3. **Batch processing**: Use the video upload API for offline processing
4. **Timeout handling**: Set reasonable timeouts to avoid blocking

### Example: Skip Frames
```python
frame_count = 0
PROCESS_EVERY_N_FRAMES = 3

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Only process every 3rd frame
    if frame_count % PROCESS_EVERY_N_FRAMES == 0:
        # Send to API
        response = requests.post(...)
```

## Error Handling

### Common Errors

**400 Bad Request - Invalid image format**
```json
{
  "detail": "Invalid image format"
}
```
Solution: Ensure you're sending a valid image file (JPEG, PNG)

**500 Internal Server Error - Model not loaded**
```json
{
  "detail": "Failed to initialize face detection model: ..."
}
```
Solution: Check that InsightFace and DeepFace are installed

**Timeout**
Solution: Reduce frame size or increase timeout value

### Robust Error Handling Example
```python
import requests
from requests.exceptions import Timeout, RequestException

def process_frame_safe(frame_path):
    try:
        with open(frame_path, 'rb') as f:
            response = requests.post(
                'http://localhost:8001/local/process-frame',
                files={'frame': f},
                data={'reset_tracker': 'false'},
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()
    
    except Timeout:
        print("Request timed out")
        return None
    
    except RequestException as e:
        print(f"Request failed: {e}")
        return None
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Use it
result = process_frame_safe('frame.jpg')
if result:
    print(f"Detected {result['total_faces']} faces")
```

## Integration with Frontend

### JavaScript/React Example

```javascript
async function processFrame(imageFile) {
  const formData = new FormData();
  formData.append('frame', imageFile);
  formData.append('reset_tracker', 'false');
  
  try {
    const response = await fetch('http://localhost:8001/local/process-frame', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Frame processing failed:', error);
    return null;
  }
}

// Usage with webcam
const video = document.getElementById('webcam');
const canvas = document.createElement('canvas');

setInterval(async () => {
  // Capture frame from video
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  
  // Convert to blob
  canvas.toBlob(async (blob) => {
    const result = await processFrame(blob);
    if (result) {
      console.log(`Detected ${result.total_faces} faces`);
      // Update UI with results
    }
  }, 'image/jpeg', 0.8);
}, 1000); // Process every 1 second
```

## Technical Details

### Models Used
- **Face Detection**: InsightFace Buffalo-S (CPU mode)
- **Emotion Recognition**: DeepFace with default backend
- **Tracking**: Cosine similarity on face embeddings

### Processing Pipeline
1. Decode uploaded image
2. Convert BGR → RGB
3. Detect faces with InsightFace
4. Track faces using embeddings
5. Crop face regions
6. Detect emotions with DeepFace
7. Return JSON results

### Thread Safety
- Each request is processed independently
- Face tracker state is shared across requests (for tracking)
- Safe for concurrent requests from same video stream

## Troubleshooting

### Models Not Loading
```bash
# Check if ML libraries are installed
python -c "import insightface; import deepface"

# Install if missing (requires Python 3.9-3.12)
pip install insightface deepface onnxruntime
```

### Slow Processing
- Reduce image resolution before sending
- Skip frames (process every 3rd or 5th frame)
- Use GPU version if available (modify CPUExecutionProvider)

### Tracking Issues
- Reset tracker when switching videos
- Adjust similarity_threshold in frame_api.py if needed
- Check that frames are sent in sequence

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Support

For issues or questions:
1. Check server logs for error messages
2. Verify ML libraries are installed correctly
3. Test with the interactive API docs
4. Ensure Python version is 3.9-3.12 for ML packages
