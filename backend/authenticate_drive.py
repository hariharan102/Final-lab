#!/usr/bin/env python
"""
One-time Google Drive Authentication Script

This script authenticates with Google Drive and saves the token for future use.
Run this once to create token.json, then uploads will work automatically.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emotion_backend.settings')

import django
django.setup()

from jobs.google_drive_service import GoogleDriveService

if __name__ == '__main__':
    try:
        print("🔐 Starting Google Drive Authentication...")
        print("A browser window will open shortly. Please login with your Google account.")
        print()
        
        # This will trigger the OAuth flow
        service = GoogleDriveService()
        
        print("\n✅ SUCCESS! Google Drive authentication complete!")
        print("📝 Token saved to: backend/token.json")
        print("\n✨ You can now upload videos without manual authentication!")
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        sys.exit(1)
