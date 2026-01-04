"""
URL routing for jobs app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Video upload
    path('upload/', views.upload_video, name='upload_video'),
    
    # Job status polling
    path('<uuid:job_id>/status/', views.get_job_status, name='get_job_status'),
    
    # Job results
    path('<uuid:job_id>/results/', views.get_job_results, name='get_job_results'),
    
    # Video streaming
    path('<uuid:job_id>/stream/', views.stream_video, name='stream_video'),
    
    # Optional: List all jobs and get job detail
    path('', views.list_jobs, name='list_jobs'),
    path('<uuid:job_id>/', views.get_job_detail, name='get_job_detail'),
    path('<uuid:job_id>/terminate/', views.terminate_job, name='terminate-job'),
]
