"""
API Routes for Local Emotion Detection Backend

This module defines the REST API endpoints for local video processing.
These are SEPARATE from the Colab backend endpoints.

Endpoints:
    POST /local/jobs/upload     - Upload video and start processing
    GET  /local/jobs/{id}/status - Get job status
    GET  /local/jobs/{id}/results - Get processing results
    GET  /local/jobs/{id}/stream - Stream processed video
"""

import os
import json
import uuid
import shutil
import threading
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from models import (
    LocalJob, get_db, init_db,
    INPUT_VIDEOS_DIR, OUTPUT_VIDEOS_DIR, OUTPUT_JSON_DIR, STATUS_DIR, TEMP_DIR
)
from pipeline.runner import run_emotion_pipeline

# Create API router with prefix for local backend
router = APIRouter(prefix="/local", tags=["Local Jobs"])


# ============================================
# LIST ALL JOBS - Use /jobs-list to avoid conflict with /jobs/{job_id}
# ============================================
@router.get("/jobs-list")
async def list_all_jobs(db: Session = Depends(get_db)):
    """
    List all local jobs for history display.
    
    Returns all jobs ordered by creation date (newest first).
    """
    jobs = db.query(LocalJob).order_by(LocalJob.created_at.desc()).all()
    
    return {
        "jobs": [
            {
                "job_id": str(job.id),
                "status": job.status,
                "status_message": job.status_message,
                "original_filename": os.path.basename(job.input_video_path) if job.input_video_path else "Unknown",
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                "execution_mode": "local"
            }
            for job in jobs
        ],
        "total": len(jobs)
    }


def run_pipeline_background(job_id: str, input_path: str, output_video_path: str, 
                           output_json_path: str, status_path: str, temp_dir: str):
    """
    Background task to run the emotion detection pipeline.
    
    This function is executed in a separate thread to avoid blocking the API.
    Status updates are written to a JSON file that the frontend can poll.
    """
    # Get a new database session for this thread
    from models import SessionLocal
    db = SessionLocal()
    
    try:
        # Update job status to PROCESSING
        job = db.query(LocalJob).filter(LocalJob.id == job_id).first()
        if job:
            job.status = "PROCESSING"
            job.status_message = "Pipeline started. Processing video..."
            job.updated_at = datetime.utcnow()
            db.commit()
        
        # Run the pipeline
        result = run_emotion_pipeline(
            input_video_path=input_path,
            output_video_path=output_video_path,
            output_json_path=output_json_path,
            status_file_path=status_path,
            temp_dir=temp_dir
        )
        
        # Update job with results
        job = db.query(LocalJob).filter(LocalJob.id == job_id).first()
        if job:
            if result["success"]:
                job.status = "DONE"
                job.status_message = f"Processing complete! Detected {result['total_detections']} emotions."
                job.output_video_path = output_video_path
                job.output_json_path = output_json_path
                job.progress = "100"
            else:
                job.status = "FAILED"
                job.status_message = result.get("error", "Unknown error occurred")
                job.progress = "0"
            job.updated_at = datetime.utcnow()
            db.commit()
            
    except Exception as e:
        # Handle any unexpected errors
        job = db.query(LocalJob).filter(LocalJob.id == job_id).first()
        if job:
            job.status = "FAILED"
            job.status_message = f"Pipeline error: {str(e)}"
            job.progress = "0"
            job.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.post("/jobs/upload")
async def upload_video(
    video: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a video file and start automatic local processing.
    
    Unlike the Colab backend, this endpoint:
    - Saves video locally (no Google Drive)
    - Automatically starts processing (no manual Colab step)
    - Uses CPU execution (no GPU required)
    
    Returns:
        job_id: UUID of the created job
        status: Initial status (PENDING)
        message: Confirmation message
    """
    print(f"📥 [Local Backend] Received upload: {video.filename}")
    
    # Validate file type
    if not video.content_type or not video.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a video file."
        )
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Define file paths
    input_filename = f"{job_id}.mp4"
    input_path = os.path.join(INPUT_VIDEOS_DIR, input_filename)
    output_video_path = os.path.join(OUTPUT_VIDEOS_DIR, f"{job_id}.mp4")
    output_json_path = os.path.join(OUTPUT_JSON_DIR, f"{job_id}.json")
    status_path = os.path.join(STATUS_DIR, f"{job_id}.json")
    temp_dir = os.path.join(TEMP_DIR, job_id)
    
    try:
        # Save uploaded video
        print(f"💾 Saving video to: {input_path}")
        with open(input_path, "wb") as f:
            content = await video.read()
            f.write(content)
        print(f"✅ Video saved ({len(content)} bytes)")
        
        # Create job record
        job = LocalJob(
            id=job_id,
            status="PENDING",
            status_message="Video uploaded. Starting automatic processing...",
            input_video_path=input_path,
            progress="0"
        )
        db.add(job)
        db.commit()
        
        # Write initial status file
        with open(status_path, 'w') as f:
            json.dump({
                "status": "PENDING",
                "message": "Video uploaded. Starting processing...",
                "progress": 0,
                "updated_at": datetime.utcnow().isoformat()
            }, f)
        
        # Start background processing
        # Using threading instead of BackgroundTasks for long-running ML tasks
        print(f"🚀 Starting background pipeline for job {job_id}")
        pipeline_thread = threading.Thread(
            target=run_pipeline_background,
            args=(job_id, input_path, output_video_path, output_json_path, status_path, temp_dir),
            daemon=True
        )
        pipeline_thread.start()
        
        return {
            "job_id": job_id,
            "status": "PENDING",
            "message": "Video uploaded successfully. Processing started automatically.",
            "execution_mode": "local",
            "note": "No manual Colab step required. Processing runs on your local CPU."
        }
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload video: {str(e)}"
        )


@router.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get the current status of a local processing job.
    
    Frontend should poll this endpoint every 1-2 seconds during processing.
    Status is read from both database and status file for latest updates.
    
    Returns:
        status: Current job status (PENDING/PROCESSING/DONE/FAILED)
        status_message: Human-readable status message
        progress: Processing progress (0-100)
        updated_at: Last update timestamp
    """
    # Get job from database
    job = db.query(LocalJob).filter(LocalJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Also read from status file for most recent progress
    status_path = os.path.join(STATUS_DIR, f"{job_id}.json")
    file_status = None
    if os.path.exists(status_path):
        try:
            with open(status_path, 'r') as f:
                file_status = json.load(f)
        except:
            pass
    
    # Prefer file status for progress (more granular updates)
    progress = job.progress
    message = job.status_message
    if file_status:
        progress = str(file_status.get("progress", progress))
        if file_status.get("message"):
            message = file_status["message"]
    
    return {
        "job_id": job_id,
        "status": job.status,
        "status_message": message,
        "progress": int(progress) if progress else 0,
        "execution_mode": "local",
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None
    }


@router.get("/jobs/{job_id}/results")
async def get_job_results(job_id: str, db: Session = Depends(get_db)):
    """
    Get the processing results for a completed job.
    
    Only available when job status is DONE.
    
    Returns:
        job_id: Job identifier
        status: Job status
        emotion_data: Array of emotion detections
        output_video_url: URL to stream/download processed video
    """
    job = db.query(LocalJob).filter(LocalJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "DONE":
        raise HTTPException(
            status_code=400,
            detail=f"Results not available. Job status: {job.status}"
        )
    
    # Load emotion data from JSON file
    raw_detections = []
    if job.output_json_path and os.path.exists(job.output_json_path):
        with open(job.output_json_path, 'r') as f:
            raw_detections = json.load(f)
    
    # Process emotion data for frontend display
    # Group by person and calculate distribution - MATCH COLAB FORMAT!
    # Frontend expects: emotion_data = { "person_1": { frame_count: N, emotions: {...}, frames: [...] }, ... }
    summary_by_person = {}
    for detection in raw_detections:
        pid = detection["person_id"]
        emotion = detection["emotion"]
        
        if pid not in summary_by_person:
            summary_by_person[pid] = {
                "frame_count": 0,
                "emotions": {},
                "frames": []
            }
        
        summary_by_person[pid]["frame_count"] += 1
        
        if emotion not in summary_by_person[pid]["emotions"]:
            summary_by_person[pid]["emotions"][emotion] = 0
        summary_by_person[pid]["emotions"][emotion] += 1
        
        # Add frame details
        summary_by_person[pid]["frames"].append({
            "timestamp": detection.get("timestamp"),
            "emotion": emotion,
            "confidence": detection.get("confidence"),
            "coordinates": detection.get("coordinates_pixels")
        })
    
    # Calculate total frames processed from the video
    total_frames = 0
    if raw_detections:
        # Get unique timestamps to estimate frame count
        timestamps = set(d.get("timestamp", 0) for d in raw_detections)
        total_frames = len(timestamps)
    
    return {
        "job_id": job_id,
        "status": job.status,
        "execution_mode": "local",
        "emotion_data": summary_by_person,  # Frontend expects this format
        "summary_by_person": summary_by_person,  # Also provide as summary_by_person for compatibility
        "detections": raw_detections,  # Raw detection list if needed
        "total_detections": len(raw_detections),
        "total_frames": total_frames,
        "output_video_url": f"/local/jobs/{job_id}/stream",
        "download_url": f"/local/jobs/{job_id}/stream"
    }


@router.get("/jobs/{job_id}/stream")
async def stream_video(job_id: str, db: Session = Depends(get_db)):
    """
    Stream or download the processed video file.
    
    Returns the video file directly for playback in browser or download.
    """
    job = db.query(LocalJob).filter(LocalJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "DONE":
        raise HTTPException(
            status_code=400,
            detail=f"Video not available. Job status: {job.status}"
        )
    
    if not job.output_video_path or not os.path.exists(job.output_video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    # Return file as streaming response
    def iterfile():
        with open(job.output_video_path, mode="rb") as file:
            while chunk := file.read(1024 * 1024):  # 1MB chunks
                yield chunk
    
    file_size = os.path.getsize(job.output_video_path)
    
    return StreamingResponse(
        iterfile(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": f"attachment; filename=emotion_detection_{job_id}.mp4",
            "Content-Length": str(file_size)
        }
    )


@router.get("/jobs/{job_id}/json")
async def download_json(job_id: str, db: Session = Depends(get_db)):
    """
    Download the emotion detection JSON file.
    
    Returns the JSON file with all emotion detection data.
    """
    job = db.query(LocalJob).filter(LocalJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "DONE":
        raise HTTPException(
            status_code=400,
            detail=f"JSON not available. Job status: {job.status}"
        )
    
    if not job.output_json_path or not os.path.exists(job.output_json_path):
        raise HTTPException(status_code=404, detail="JSON file not found")
    
    return FileResponse(
        job.output_json_path,
        media_type="application/json",
        filename=f"emotion_data_{job_id}.json",
        headers={
            "Content-Disposition": f"attachment; filename=emotion_data_{job_id}.json"
        }
    )


@router.post("/jobs/{job_id}/terminate")
async def terminate_job(job_id: str, db: Session = Depends(get_db)):
    """
    Terminate/cancel a running job.
    
    Note: This marks the job as cancelled but may not immediately stop
    the background pipeline thread.
    """
    job = db.query(LocalJob).filter(LocalJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status in ["DONE", "FAILED", "CANCELLED"]:
        return {
            "job_id": job_id,
            "status": job.status,
            "message": f"Job already in terminal state: {job.status}"
        }
    
    job.status = "CANCELLED"
    job.status_message = "Job cancelled by user"
    job.updated_at = datetime.utcnow()
    db.commit()
    
    # Update status file
    status_path = os.path.join(STATUS_DIR, f"{job_id}.json")
    with open(status_path, 'w') as f:
        json.dump({
            "status": "CANCELLED",
            "message": "Job cancelled by user",
            "progress": 0,
            "updated_at": datetime.utcnow().isoformat()
        }, f)
    
    return {
        "job_id": job_id,
        "status": "CANCELLED",
        "message": "Job has been cancelled"
    }
