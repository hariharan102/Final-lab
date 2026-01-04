"""
Serializers for VideoJob API endpoints.
"""

from rest_framework import serializers
from .models import VideoJob


class VideoJobSerializer(serializers.ModelSerializer):
    """
    Standard serializer for VideoJob model.
    Used for general CRUD operations.
    """
    
    class Meta:
        model = VideoJob
        fields = [
            'id',
            'status',
            'status_message',
            'input_video_path',
            'output_video_path',
            'output_json_path',
            'colab_notebook_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VideoUploadSerializer(serializers.Serializer):
    """
    Serializer for video upload endpoint.
    Accepts a video file and creates a new VideoJob.
    """
    
    video = serializers.FileField(
        required=True,
        help_text="Video file to process (MP4, AVI, MOV, etc.)"
    )
    
    def validate_video(self, value):
        """
        Validate uploaded video file.
        """
        # Check file size (max 500MB)
        max_size = 500 * 1024 * 1024  # 500MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Video file too large. Maximum size is 500MB. Your file is {value.size / (1024*1024):.1f}MB"
            )
        
        # Check file extension
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        file_ext = value.name.lower()[value.name.rfind('.'):]
        if file_ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value


class VideoJobStatusSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for status polling.
    Returns only essential status information.
    """
    
    class Meta:
        model = VideoJob
        fields = [
            'id',
            'status',
            'status_message',
            'updated_at',
        ]


class VideoJobResultSerializer(serializers.ModelSerializer):
    """
    Serializer for results endpoint.
    Includes output file paths and emotion data.
    """
    
    emotion_data = serializers.SerializerMethodField()
    output_video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoJob
        fields = [
            'id',
            'status',
            'output_video_path',
            'output_json_path',
            'output_video_url',
            'emotion_data',
            'created_at',
            'updated_at',
        ]
    
    def get_output_video_url(self, obj):
        """
        Generate a URL to access the output video.
        In production, this would be a Google Drive download link.
        """
        # Placeholder - will be replaced with actual Google Drive link
        if obj.output_video_path:
            return f"/api/jobs/{obj.id}/download/video/"
        return None
    
    def get_emotion_data(self, obj):
        """
        Parse and return emotion detection results.
        This will be populated from the JSON file in Google Drive.
        """
        # Placeholder - actual implementation will read from Google Drive
        # The JSON structure from Colab should contain:
        # {
        #   "person_1": {
        #     "frames": [...],
        #     "emotions": {"happy": 120, "sad": 30, ...}
        #   },
        #   ...
        # }
        return {
            "status": "Results will be loaded from Google Drive",
            "json_path": obj.output_json_path
        }
