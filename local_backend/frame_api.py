"""
Frame-by-Frame Emotion Detection API

This module provides a REST API endpoint for real-time frame-by-frame emotion detection.
It does NOT modify the core ML pipeline code - it only wraps the existing processing logic.

Endpoint:
    POST /local/process-frame - Process a single frame and return emotion data

Usage:
    Send a frame as multipart/form-data with field name 'frame'
    Returns JSON with detected faces and emotions for that frame
"""

import io
import cv2
import numpy as np
import base64
from typing import Optional, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from PIL import Image

# Import the core processing modules (DO NOT MODIFY THESE)
# Try to import ML modules, but allow server to start without them
try:
    from pipeline.face_detection import FaceTracker
    from deepface import DeepFace
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    ML_IMPORT_ERROR = str(e)

# Create router for frame-by-frame API
frame_router = APIRouter(prefix="/local", tags=["Frame Processing"])

# Global face tracker instance (maintains state across frames)
# This allows tracking the same person across multiple frame requests
_face_tracker = None
_face_analyzer = None


def get_face_analyzer():
    """
    Initialize and return the InsightFace analyzer (CPU mode).
    Lazy initialization to avoid loading models on import.
    """
    global _face_analyzer
    
    if not ML_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "ML libraries not available",
                "message": "InsightFace and DeepFace are not installed or incompatible with Python 3.14",
                "solution": "Install Python 3.9-3.12 and run: pip install insightface deepface onnxruntime",
                "import_error": ML_IMPORT_ERROR if 'ML_IMPORT_ERROR' in globals() else "Unknown"
            }
        )
    
    if _face_analyzer is None:
        try:
            from insightface.app import FaceAnalysis
            _face_analyzer = FaceAnalysis(
                name='buffalo_s',
                providers=['CPUExecutionProvider']
            )
            _face_analyzer.prepare(ctx_id=-1, det_size=(640, 640))
            print("[FrameAPI] InsightFace analyzer initialized (CPU mode)")
        except Exception as e:
            print(f"[FrameAPI] ERROR initializing InsightFace: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize face detection model: {str(e)}"
            )
    return _face_analyzer


def get_face_tracker():
    """
    Get or create the global face tracker instance.
    """
    global _face_tracker
    
    if not ML_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "ML libraries not available",
                "message": "Face tracking requires InsightFace which is not installed",
                "solution": "Install Python 3.9-3.12 and run: pip install insightface onnxruntime"
            }
        )
    
    if _face_tracker is None:
        _face_tracker = FaceTracker(
            similarity_threshold=0.65,
            max_disappeared=30,
            update_alpha=0.9
        )
        print("[FrameAPI] Face tracker initialized")
    return _face_tracker


@frame_router.post("/process-frame")
async def process_frame(
    frame: UploadFile = File(..., description="Image frame to process"),
    reset_tracker: bool = Form(False, description="Reset face tracker (for new video)")
):
    """
    Process a single frame and return emotion detection results.
    
    This endpoint:
    1. Accepts an image frame (JPEG, PNG, etc.)
    2. Detects faces using InsightFace (same as core pipeline)
    3. Tracks faces across frames using the same FaceTracker
    4. Detects emotions using DeepFace (same as core pipeline)
    5. Returns JSON with face locations, person IDs, and emotions
    
    Args:
        frame: Image file (multipart/form-data)
        reset_tracker: If true, resets the face tracker (use for new videos)
    
    Returns:
        JSON with:
        - frame_processed: true/false
        - faces: list of detected faces with emotions
        - total_faces: count of faces detected
        - timestamp: processing timestamp
    """
    global _face_tracker
    
    # Reset tracker if requested (for new video sequences)
    if reset_tracker:
        _face_tracker = None
        print("[FrameAPI] Face tracker reset")
    
    try:
        # Read the uploaded frame
        contents = await frame.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Convert BGR to RGB (InsightFace expects RGB)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Get face analyzer and tracker
        analyzer = get_face_analyzer()
        tracker = get_face_tracker()
        
        # Detect faces using InsightFace (same as core pipeline)
        faces = analyzer.get(img_rgb)
        
        if not faces:
            return {
                "frame_processed": True,
                "faces": [],
                "total_faces": 0,
                "message": "No faces detected in frame"
            }
        
        # Prepare face data for tracking (same format as core pipeline)
        face_data_list = []
        for face in faces:
            bbox = face.bbox.astype(int)
            face_data_list.append({
                "bbox": bbox.tolist(),
                "embedding": face.embedding,
                "det_score": float(face.det_score)
            })
        
        # Track faces (assigns person IDs)
        # Use frame timestamp = 0 for single frame processing
        person_ids = tracker.update(face_data_list, timestamp=0.0)
        
        # Detect emotions for each face (same as core pipeline)
        results = []
        for idx, (face_data, person_id) in enumerate(zip(face_data_list, person_ids)):
            bbox = face_data["bbox"]
            x1, y1, x2, y2 = bbox
            
            # Crop face region
            face_crop = img_rgb[y1:y2, x1:x2]
            
            if face_crop.size == 0:
                continue
            
            # Detect emotion using DeepFace (same as core pipeline)
            try:
                emotion_result = detect_emotions_batch([face_crop])
                
                if emotion_result and len(emotion_result) > 0:
                    emotion_data = emotion_result[0]
                    
                    results.append({
                        "person_id": person_id,
                        "bbox": {
                            "x1": int(x1),
                            "y1": int(y1),
                            "x2": int(x2),
                            "y2": int(y2)
                        },
                        "confidence": float(face_data["det_score"]),
                        "emotion": emotion_data.get("dominant_emotion", "unknown"),
                        "emotion_scores": emotion_data.get("emotion", {}),
                        "face_width": int(x2 - x1),
                        "face_height": int(y2 - y1)
                    })
            except Exception as e:
                print(f"[FrameAPI] Emotion detection failed for face {idx}: {e}")
                # Still return face detection result even if emotion fails
                results.append({
                    "person_id": person_id,
                    "bbox": {
                        "x1": int(x1),
                        "y1": int(y1),
                        "x2": int(x2),
                        "y2": int(y2)
                    },
                    "confidence": float(face_data["det_score"]),
                    "emotion": "error",
                    "emotion_scores": {},
                    "error": str(e)
                })
        
        return {
            "frame_processed": True,
            "faces": results,
            "total_faces": len(results),
            "frame_dimensions": {
                "width": img.shape[1],
                "height": img.shape[0]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[FrameAPI] Error processing frame: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Frame processing failed: {str(e)}"
        )


@frame_router.post("/reset-tracker")
async def reset_tracker():
    """
    Reset the face tracker.
    
    Call this endpoint when starting a new video sequence to clear
    the face tracking history.
    """
    global _face_tracker
    _face_tracker = None
    return {
        "success": True,
        "message": "Face tracker reset successfully"
    }


@frame_router.get("/frame-api-status")
async def frame_api_status():
    """
    Check if the frame API is ready and models are loaded.
    """
    global _face_analyzer, _face_tracker
    
    if not ML_AVAILABLE:
        return {
            "status": "unavailable",
            "ml_libraries_available": False,
            "error": "ML libraries not installed or incompatible with Python version",
            "solution": "Install Python 3.9-3.12 and run: pip install insightface deepface onnxruntime",
            "import_error": ML_IMPORT_ERROR if 'ML_IMPORT_ERROR' in globals() else "Unknown",
            "face_analyzer_loaded": False,
            "face_tracker_active": False,
            "active_tracked_people": 0
        }
    
    return {
        "status": "ready",
        "ml_libraries_available": True,
        "face_analyzer_loaded": _face_analyzer is not None,
        "face_tracker_active": _face_tracker is not None,
        "active_tracked_people": len(_face_tracker.active_people) if _face_tracker else 0
    }
