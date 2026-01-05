#!/usr/bin/env python3
"""
Test script for frame API emotion detection
"""
import cv2
import requests
import numpy as np

# Create a simple test image with a face-like pattern
def create_test_frame():
    # Create a 640x480 color image
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200
    
    # Draw a simple face
    cv2.circle(img, (320, 240), 100, (255, 200, 150), -1)  # Face
    cv2.circle(img, (290, 220), 15, (0, 0, 0), -1)  # Left eye
    cv2.circle(img, (350, 220), 15, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(img, (320, 270), (40, 20), 0, 0, 180, (0, 0, 0), 2)  # Smile
    
    # Encode as JPEG
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

# Test the API
print("Testing Frame API...")
print("=" * 60)

# Create test frame
frame_data = create_test_frame()
print(f"✓ Created test frame ({len(frame_data)} bytes)")

# Send to API
url = "http://localhost:8001/local/process-frame"
files = {'frame': ('test.jpg', frame_data, 'image/jpeg')}

print(f"✓ Sending to {url}...")

try:
    response = requests.post(url, files=files)
    print(f"✓ Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + "=" * 60)
        print("RESULT:")
        print("=" * 60)
        print(f"Frame processed: {result.get('frame_processed')}")
        print(f"Total faces: {result.get('total_faces')}")
        
        for face in result.get('faces', []):
            print(f"\nPerson {face.get('person_id')}:")
            print(f"  Emotion: {face.get('emotion')}")
            print(f"  Confidence: {face.get('confidence', 0):.2f}")
            
            scores = face.get('emotion_scores', {})
            if scores:
                print("  Emotion scores:")
                for emotion, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                    print(f"    {emotion}: {score:.2f}%")
            
            if 'error' in face:
                print(f"  ERROR: {face['error']}")
        
        print("\n" + "=" * 60)
        if result.get('total_faces', 0) > 0:
            print("✅ SUCCESS: Emotion detection is working!")
        else:
            print("⚠️  No faces detected (this is expected for simple test image)")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
