"""
VideoJob Model

Represents a video processing job that uses Google Colab for GPU-based
emotion detection. The processing workflow is:

1. User uploads video → Backend saves to Google Drive
2. Backend creates VideoJob with status=PENDING
3. User manually runs Colab notebook (clicks link)
4. Colab processes video and writes status updates to Google Drive
5. Frontend polls backend → Backend reads status from Google Drive
6. When done, backend retrieves results from Google Drive

CRITICAL: Backend does NOT run AI inference. It only manages files and status.
"""

from django.db import models
import uuid


class VideoJob(models.Model):
    """
    Tracks a video emotion detection job processed in Google Colab.
    
    Status Flow:
    PENDING → (user runs Colab) → PROCESSING → DONE or FAILED
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending - Waiting for Colab processing'),
        ('PROCESSING', 'Processing - Running in Colab'),
        ('DONE', 'Done - Results available'),
        ('FAILED', 'Failed - Error occurred'),
        ('CANCELLED', 'Cancelled - Job terminated by user'),
    ]
    
    # Primary key - unique job identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique job ID used for file naming in Google Drive"
    )
    
    # Job status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current processing status"
    )
    
    status_message = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed status message from Colab (e.g., 'Processing frame 45/120')"
    )
    
    # File paths in Google Drive
    # Format: /ai_emotion_project/input_videos/<job_id>.mp4
    input_video_path = models.CharField(
        max_length=500,
        help_text="Google Drive path to input video"
    )
    
    output_video_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Google Drive path to processed video with emotion annotations"
    )
    
    output_json_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Google Drive path to emotion detection results JSON"
    )
    
    # Colab notebook URL
    colab_notebook_url = models.CharField(
        max_length=500,
        help_text="Google Colab notebook URL for manual GPU processing"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the job was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last status update time"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Video Job"
        verbose_name_plural = "Video Jobs"
    
    def __str__(self):
        return f"Job {self.id} - {self.status}"
    
    def get_expected_output_paths(self):
        """
        Returns the expected output file paths in Google Drive.
        Colab will write results to these locations.
        """
        return {
            'output_video': f'/ai_emotion_project/output_videos/{self.id}.mp4',
            'output_json': f'/ai_emotion_project/output_json/{self.id}.json',
            'status_file': f'/ai_emotion_project/status/{self.id}.json',
        }
