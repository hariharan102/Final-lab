"""
Django admin configuration for VideoJob model.
"""

from django.contrib import admin
from .models import VideoJob


@admin.register(VideoJob)
class VideoJobAdmin(admin.ModelAdmin):
    """
    Admin interface for managing VideoJob records.
    """
    
    list_display = [
        'id',
        'status',
        'status_message',
        'created_at',
        'updated_at',
    ]
    
    list_filter = ['status', 'created_at']
    
    search_fields = ['id', 'status_message']
    
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Job Information', {
            'fields': ['id', 'status', 'status_message']
        }),
        ('File Paths', {
            'fields': [
                'input_video_path',
                'output_video_path',
                'output_json_path',
            ]
        }),
        ('Colab Integration', {
            'fields': ['colab_notebook_url']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at']
        }),
    ]
