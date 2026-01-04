"""
ASGI config for emotion_backend project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emotion_backend.settings')

application = get_asgi_application()
