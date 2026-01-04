"""
API Views for Video Job Management

This backend does NOT run AI inference. It only:
1. Uploads videos to local storage for testing (Google Drive requires OAuth verification)
2. Reads status updates from local/Google Drive (written by Colab)
3. Retrieves results from local/Google Drive (written by Colab)

The actual GPU processing happens MANUALLY in Google Colab.
"""

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import VideoJob
from .serializers import (
    VideoUploadSerializer,
    VideoJobStatusSerializer,
    VideoJobResultSerializer,
    VideoJobSerializer
)
from .google_drive_service import GoogleDriveService, MockGoogleDriveService
import os
from pathlib import Path


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_video(request):
    """
    POST /api/jobs/upload/
    
    Upload a video file and create a new processing job.
    
    Workflow:
    1. Validate uploaded video file
    2. Create VideoJob record with status=PENDING
    3. Upload video to local storage (or Google Drive if configured)
    4. Return job_id and Colab notebook URL
    
    The user must then manually open and run the Colab notebook.
    """
    
    print(f"📥 Received upload request from {request.META.get('REMOTE_ADDR')}")
    print(f"   Request data keys: {list(request.data.keys())}")
    
    serializer = VideoUploadSerializer(data=request.data)
    if not serializer.is_valid():
        print(f"❌ Validation failed: {serializer.errors}")
        return Response(
            {"error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    video_file = serializer.validated_data['video']
    print(f"✅ Validation passed. Video file: {video_file.name}, Size: {video_file.size} bytes")
    
    # Create VideoJob record
    job = VideoJob.objects.create(
        status='PENDING',
        status_message='Video uploaded. Waiting for Colab processing.',
        input_video_path='',  # Will be set after upload
        colab_notebook_url=settings.COLAB_NOTEBOOK_URL
    )
    print(f"✅ Created job with ID: {job.id}")
    
    # Define file path
    input_path = f'/ai_emotion_project/input_videos/{job.id}.mp4'
    
    try:
        # Try Google Drive first, fallback to local storage
        try:
            print(f"📤 Uploading video to Google Drive...")
            drive_service = GoogleDriveService()
            drive_service.upload_video(video_file, input_path, job.id)
            job.status_message = 'Video uploaded to Google Drive. Ready for Colab processing.'
            print(f"✅ Video uploaded to Google Drive: {input_path}")
        except Exception as drive_error:
            print(f"⚠️ Google Drive upload failed: {str(drive_error)}")
            print(f"📤 Falling back to local storage...")
            try:
                drive_service = MockGoogleDriveService()
                drive_service.upload_video(video_file, input_path, job.id)
                job.status_message = 'Video uploaded to local storage. Ready for Colab processing.'
                print(f"✅ Video saved locally: {input_path}")
            except Exception as mock_error:
                print(f"❌ Local storage also failed: {str(mock_error)}")
                raise Exception(f"Both upload methods failed. Drive: {drive_error}, Mock: {mock_error}")
        
        # Update job with input path
        job.input_video_path = input_path
        job.save()
        
        return Response({
            'job_id': str(job.id),
            'status': job.status,
            'colab_url': job.colab_notebook_url,
            'message': 'Video uploaded successfully. Please open Colab to start GPU processing.',
            'input_path': input_path,
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        # If upload fails, mark job as failed
        job.status = 'FAILED'
        job.status_message = f'Upload failed: {str(e)}'
        job.save()
        
        print(f"❌ Upload error: {str(e)}")
        
        return Response({
            'error': 'Failed to upload video',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_job_status(request, job_id):
    """
    GET /api/jobs/<job_id>/status/
    
    Get the current status of a processing job.
    
    Workflow:
    1. Fetch VideoJob from database
    2. Read status file from storage: /status/<job_id>.json
    3. Update database with latest status
    4. Return status to frontend
    
    Frontend polls this endpoint every 2-3 seconds during processing.
    
    Status file format (written by Colab):
    {
        "status": "PROCESSING|DONE|FAILED",
        "message": "Current processing status",
        "progress": 45
    }
    """
    job = get_object_or_404(VideoJob, id=job_id)
    
    try:
        # Try Google Drive first, then fallback to local storage
        try:
            drive_service = GoogleDriveService()
            status_data = drive_service.read_status_file(job.id)
        except Exception:
            # Fallback to local storage
            drive_service = MockGoogleDriveService()
            status_data = drive_service.read_status_file(job.id)
        
        if status_data:
            # Update job with latest status from Colab
            job.status = status_data.get('status', job.status)
            job.status_message = status_data.get('message', job.status_message)
            
            # If processing is done, update output paths
            if job.status == 'DONE':
                expected_paths = job.get_expected_output_paths()
                job.output_video_path = expected_paths['output_video']
                job.output_json_path = expected_paths['output_json']
            
            job.save()
    
    except Exception as e:
        # If we can't read status file, continue with database status
        print(f"Warning: Could not read status file: {e}")
    
    serializer = VideoJobStatusSerializer(job)
    return Response(serializer.data)


@api_view(['GET'])
def get_job_results(request, job_id):
    """
    GET /api/jobs/<job_id>/results/
    
    Get the processing results (only available when status=DONE).
    
    Workflow:
    1. Verify job status is DONE
    2. Read emotion detection JSON from storage
    3. Generate download URL for output video
    4. Return results to frontend
    
    Returns:
    - Output video URL
    - Parsed emotion data (per person_id)
    - Emotion distribution statistics
    """
    
    job = get_object_or_404(VideoJob, id=job_id)
    
    # Check if processing is complete
    if job.status != 'DONE':
        return Response({
            'error': 'Results not available yet',
            'current_status': job.status,
            'job_id': str(job.id)
        }, status=status.HTTP_202_ACCEPTED)
    
    try:
        # Try Google Drive first, then fallback to local storage
        try:
            drive_service = GoogleDriveService()
            raw_emotion_data = drive_service.read_emotion_results(job.id)
            output_video_url = drive_service.get_video_download_url(job.id, 'output')
        except Exception as e:
            print(f"⚠️ Google Drive failed: {e}, falling back to local storage")
            # Fallback to local storage
            drive_service = MockGoogleDriveService()
            raw_emotion_data = drive_service.read_emotion_results(job.id)
            output_video_url = drive_service.get_video_download_url(job.id, 'output')
        
        # Extract emotion data - handle both formats from Colab
        # Format 1: {"summary_by_person": {...}, "total_frames": N}
        # Format 2: Direct person data {"person_1": {...}, "person_2": {...}}
        if isinstance(raw_emotion_data, dict):
            if 'summary_by_person' in raw_emotion_data:
                emotion_data = raw_emotion_data.get('summary_by_person', {})
                total_frames = raw_emotion_data.get('total_frames', 0)
                total_detections = raw_emotion_data.get('total_detections', 0)
            else:
                emotion_data = raw_emotion_data
                total_frames = 0
                total_detections = 0
        else:
            emotion_data = {}
            total_frames = 0
            total_detections = 0
        
        print(f"📊 Results for job {job.id}: {len(emotion_data)} persons, {total_frames} frames")
        
        return Response({
            'job_id': str(job.id),
            'status': job.status,
            'output_video_url': output_video_url,
            'emotion_data': emotion_data,
            'total_frames': total_frames,
            'total_detections': total_detections,
            'created_at': job.created_at,
            'updated_at': job.updated_at,
        })
        
    except Exception as e:
        return Response({
            'error': 'Failed to retrieve results from storage',
            'details': str(e),
            'job_id': str(job.id)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_jobs(request):
    """
    GET /api/jobs/
    
    List all video processing jobs (optional - for debugging/admin).
    """
    jobs = VideoJob.objects.all()
    serializer = VideoJobSerializer(jobs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_job_detail(request, job_id):
    """
    GET /api/jobs/<job_id>/
    
    Get detailed information about a specific job.
    """
    job = get_object_or_404(VideoJob, id=job_id)
    serializer = VideoJobSerializer(job)
    return Response(serializer.data)


@api_view(['POST'])
def terminate_job(request, job_id):
    """
    POST /api/jobs/<job_id>/terminate/
    
    Terminate/cancel a running or pending job.
    """
    job = get_object_or_404(VideoJob, id=job_id)
    
    # Only allow terminating PENDING or PROCESSING jobs
    if job.status in ['DONE', 'FAILED', 'CANCELLED']:
        return Response(
            {
                'error': 'Cannot terminate job',
                'message': f'Job is already {job.status}',
                'current_status': job.status
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update job status to CANCELLED
    job.status = 'CANCELLED'
    job.status_message = 'Job cancelled by user'
    job.save()
    
    print(f"🛑 Job {job.id} terminated by user")
    
    return Response({
        'job_id': str(job.id),
        'status': job.status,
        'message': 'Job terminated successfully'
    })


from django.http import FileResponse, HttpResponse
import mimetypes

@api_view(['GET'])
def stream_video(request, job_id):
    """
    GET /api/jobs/<job_id>/stream/
    
    Stream the processed output video file.
    Downloads from Google Drive or serves from local storage.
    """
    job = get_object_or_404(VideoJob, id=job_id)
    
    try:
        # Try Google Drive first
        try:
            print(f"📥 Attempting to download video from Google Drive for job {job_id}")
            drive_service = GoogleDriveService()
            
            # Download video to temp location
            temp_video_path = settings.TEMP_VIDEO_DIR / f"{job_id}_output.mp4"
            drive_service.download_video(job_id, 'output', temp_video_path)
            
            if temp_video_path.exists():
                print(f"✅ Video downloaded from Google Drive: {temp_video_path}")
                response = FileResponse(
                    open(temp_video_path, 'rb'),
                    content_type='video/mp4'
                )
                response['Content-Disposition'] = f'inline; filename="{job_id}_processed.mp4"'
                response['Content-Length'] = temp_video_path.stat().st_size
                return response
            else:
                raise FileNotFoundError("Downloaded file not found")
                
        except Exception as drive_error:
            print(f"⚠️ Google Drive download failed: {drive_error}")
            
            # Fallback to local storage
            local_video_path = Path(settings.MEDIA_ROOT) / 'mock_drive' / 'output_videos' / f'{job_id}.mp4'
            
            if local_video_path.exists():
                print(f"✅ Serving video from local storage: {local_video_path}")
                response = FileResponse(
                    open(local_video_path, 'rb'),
                    content_type='video/mp4'
                )
                response['Content-Disposition'] = f'inline; filename="{job_id}_processed.mp4"'
                response['Content-Length'] = local_video_path.stat().st_size
                return response
            else:
                print(f"❌ Video not found locally: {local_video_path}")
                raise FileNotFoundError(f"Video file not found: {local_video_path}")
    
    except FileNotFoundError as e:
        return Response(
            {'error': 'Video file not found', 'details': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"❌ Error streaming video: {e}")
        return Response(
            {'error': 'Failed to stream video', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
