"""
Test script to simulate a frontend upload with a real video file.
This mimics what happens when a user uploads through the web interface.
"""

import requests
import io

# Create a more realistic fake video file (MP4 header)
# This is a minimal valid MP4 file header
fake_mp4_data = (
    b'\x00\x00\x00\x20\x66\x74\x79\x70\x69\x73\x6f\x6d\x00\x00\x02\x00'
    b'\x69\x73\x6f\x6d\x69\x73\x6f\x32\x61\x76\x63\x31\x6d\x70\x34\x31'
    b'\x00\x00\x00\x08\x66\x72\x65\x65' + b'\x00' * 1000  # Add some padding
)

print("=" * 60)
print("Testing Frontend Upload Flow")
print("=" * 60)

try:
    # Simulate FormData upload from React
    files = {
        'video': ('test_video.mp4', io.BytesIO(fake_mp4_data), 'video/mp4')
    }
    
    print("\n1. Sending POST request to /api/jobs/upload/...")
    print(f"   File size: {len(fake_mp4_data)} bytes")
    
    response = requests.post(
        'http://localhost:8000/api/jobs/upload/',
        files=files,
        headers={
            'Origin': 'http://localhost:3001'  # Simulate CORS request
        }
    )
    
    print(f"\n2. Response Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("\n✅ SUCCESS! Upload completed")
        print(f"\n   Job ID: {data['job_id']}")
        print(f"   Status: {data['status']}")
        print(f"   Message: {data['message']}")
        print(f"   Colab URL: {data['colab_url']}")
        print(f"   Input Path: {data['input_path']}")
        print("\n" + "=" * 60)
        print("The upload is working correctly! ✅")
        print("=" * 60)
    else:
        print(f"\n❌ FAILED with status {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ CONNECTION ERROR: Cannot connect to backend")
    print(f"   Make sure Django server is running on http://localhost:8000")
    print(f"   Error: {e}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
