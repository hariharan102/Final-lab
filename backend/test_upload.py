"""
Simple test script to verify the upload endpoint works.
Run this to test the backend upload functionality directly.
"""

import requests
import io

# Create a small dummy video file
dummy_video = io.BytesIO(b'This is a fake video file for testing')
dummy_video.name = 'test.mp4'
dummy_video.seek(0)

try:
    print("Testing upload endpoint...")
    response = requests.post(
        'http://localhost:8000/api/jobs/upload/',
        files={'video': ('test.mp4', dummy_video, 'video/mp4')}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        print("\n✅ Upload successful!")
    else:
        print(f"\n❌ Upload failed: {response.text}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
