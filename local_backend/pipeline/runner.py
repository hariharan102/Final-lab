"""
Pipeline Runner - Orchestrates the full emotion detection pipeline.

This module runs the complete pipeline in order:
1. Face Detection + Tracking (InsightFace)
2. Emotion Detection (DeepFace)
3. Video Annotation (OpenCV)

IMPORTANT: The ML logic is IDENTICAL to the Colab notebook.
Only infrastructure code (file paths, status updates) is different.
"""

import os
import json
import traceback
from datetime import datetime

from .face_detection import process_video_faces
from .emotion_detection import analyze_emotions


def run_emotion_pipeline(
    input_video_path: str,
    output_video_path: str,
    output_json_path: str,
    status_file_path: str,
    temp_dir: str
):
    """
    Run the complete emotion detection pipeline.
    
    This is the main entry point for local video processing.
    It mirrors the exact execution flow of the Colab notebook.
    
    Args:
        input_video_path: Path to uploaded input video
        output_video_path: Path to save final annotated video
        output_json_path: Path to save emotion detections JSON
        status_file_path: Path to write status updates (for frontend polling)
        temp_dir: Directory for intermediate files
    
    Returns:
        dict: Pipeline result with success status and output paths
    """
    
    def update_status(message: str, progress: int, status: str = "PROCESSING"):
        """Write status update to file for frontend polling."""
        status_data = {
            "status": status,
            "message": message,
            "progress": progress,
            "updated_at": datetime.utcnow().isoformat()
        }
        with open(status_file_path, 'w') as f:
            json.dump(status_data, f, indent=2)
        print(f"[Status] {status} - {message} ({progress}%)")
    
    try:
        # Create temp directory if needed
        os.makedirs(temp_dir, exist_ok=True)
        
        # Intermediate file paths
        face_json_path = os.path.join(temp_dir, "face_detections.json")
        face_video_path = os.path.join(temp_dir, "face_tracking_output.mp4")
        
        # ============================================
        # STEP 1: Face Detection + Tracking
        # ============================================
        update_status("Starting face detection with InsightFace...", 5)
        
        print("\n" + "="*60)
        print("STEP 1: Face Detection + Tracking (InsightFace)")
        print("="*60)
        
        face_detections = process_video_faces(
            video_path=input_video_path,
            output_json=face_json_path,
            status_callback=lambda msg, prog: update_status(msg, prog)
        )
        
        update_status(f"Face detection complete. Found {len(face_detections)} face detections.", 40)
        
        # ============================================
        # STEP 2: Emotion Detection
        # ============================================
        update_status("Starting emotion detection with DeepFace...", 45)
        
        print("\n" + "="*60)
        print("STEP 2: Emotion Detection (DeepFace)")
        print("="*60)
        
        # Use temporary path for initial output, then convert for browser
        temp_video_path = os.path.join(temp_dir, "temp_output.mp4")
        
        emotion_detections = analyze_emotions(
            input_video=input_video_path,
            input_json=face_json_path,
            output_json=output_json_path,
            output_video=temp_video_path,
            status_callback=lambda msg, prog: update_status(msg, prog)
        )
        
        # ============================================
        # STEP 3: Convert video for browser compatibility
        # ============================================
        update_status("Converting video for browser playback...", 95)
        
        print("\n" + "="*60)
        print("STEP 3: Video Conversion (Browser Compatibility)")
        print("="*60)
        
        # Try to convert using ffmpeg for H.264 browser-compatible format
        import subprocess
        import shutil as shutil_module
        
        ffmpeg_success = False
        if shutil_module.which("ffmpeg"):
            try:
                print("[Video Conversion] Using ffmpeg to convert to H.264...")
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-i", temp_video_path,
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-crf", "23",
                    "-c:a", "aac",
                    "-movflags", "+faststart",  # Enable streaming
                    output_video_path
                ]
                result_ffmpeg = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=600)
                if result_ffmpeg.returncode == 0 and os.path.exists(output_video_path):
                    ffmpeg_success = True
                    print("[Video Conversion] ✓ Successfully converted to H.264")
                    # Remove temp file
                    os.remove(temp_video_path)
                else:
                    print(f"[Video Conversion] ffmpeg error: {result_ffmpeg.stderr}")
            except Exception as ffmpeg_err:
                print(f"[Video Conversion] ffmpeg failed: {ffmpeg_err}")
        else:
            print("[Video Conversion] ffmpeg not found in PATH")
        
        # If ffmpeg failed, just copy the original file
        if not ffmpeg_success:
            print("[Video Conversion] Using original OpenCV output (may not play in some browsers)")
            shutil_module.copy(temp_video_path, output_video_path)
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
        
        # ============================================
        # STEP 4: Finalize
        # ============================================
        update_status("Processing complete!", 100, status="DONE")
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETE")
        print("="*60)
        print(f"✓ Output video: {output_video_path}")
        print(f"✓ Emotion JSON: {output_json_path}")
        print(f"✓ Total emotions detected: {len(emotion_detections)}")
        
        return {
            "success": True,
            "output_video_path": output_video_path,
            "output_json_path": output_json_path,
            "total_detections": len(emotion_detections),
            "face_detections": len(face_detections)
        }
        
    except Exception as e:
        error_message = f"Pipeline failed: {str(e)}"
        print(f"\n❌ ERROR: {error_message}")
        traceback.print_exc()
        
        update_status(error_message, 0, status="FAILED")
        
        return {
            "success": False,
            "error": error_message,
            "traceback": traceback.format_exc()
        }


# For command-line testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m pipeline.runner <input_video>")
        sys.exit(1)
    
    input_video = sys.argv[1]
    output_dir = os.path.dirname(input_video)
    
    result = run_emotion_pipeline(
        input_video_path=input_video,
        output_video_path=os.path.join(output_dir, "output_video.mp4"),
        output_json_path=os.path.join(output_dir, "emotions.json"),
        status_file_path=os.path.join(output_dir, "status.json"),
        temp_dir=os.path.join(output_dir, "temp")
    )
    
    print("\nResult:", json.dumps(result, indent=2))
