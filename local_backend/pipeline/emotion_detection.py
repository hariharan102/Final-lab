"""
Emotion Detection Module

IMPORTANT: This code is a DIRECT COPY of the Colab notebook emotion detection logic.
DO NOT modify the ML algorithms, thresholds, or processing order.

Original source: final_code_emotion_detectionipynb.ipynb (Cell 4)
"""

import cv2
import json
import numpy as np
from collections import defaultdict
from deepface import DeepFace


# Emotion smoothing settings - COPIED FROM COLAB NOTEBOOK
EMOTION_WINDOW_SECONDS = 5.0  # Time window to accumulate emotion scores
MIN_CONFIDENCE_THRESHOLD = 30.0  # Minimum confidence to consider an emotion


def create_unique_color(identifier):
    """Create a unique color based on the identifier."""
    hash_val = hash(identifier)
    r = (hash_val & 0xFF0000) >> 16
    g = (hash_val & 0x00FF00) >> 8
    b = hash_val & 0x0000FF
    return (b, g, r)


def get_emotion_color(emotion):
    """Return color based on emotion type."""
    emotion_colors = {
        "angry": (0, 0, 255),      # Red
        "disgust": (0, 128, 0),    # Dark Green
        "fear": (128, 0, 128),     # Purple
        "happy": (0, 255, 255),    # Yellow
        "sad": (255, 0, 0),        # Blue
        "surprise": (0, 165, 255), # Orange
        "neutral": (128, 128, 128) # Gray
    }
    return emotion_colors.get(emotion.lower(), (255, 255, 255))


def analyze_emotions(input_video, input_json, output_json, output_video, status_callback=None):
    """
    Analyze emotions for each detected face using DeepFace.
    Uses face detections from InsightFace output JSON.
    
    COPIED DIRECTLY FROM COLAB NOTEBOOK - DO NOT MODIFY LOGIC.
    
    Args:
        input_video: Path to input video (with face tracking overlay)
        input_json: Path to face detections JSON
        output_json: Path to save emotion detections JSON
        output_video: Path to save emotion-annotated video
        status_callback: Optional callback function for progress updates
    
    Returns:
        List of all emotion detections
    """
    print(f"[Emotion Detection] Loading face detections from {input_json}...")
    with open(input_json, "r") as f:
        all_detections = json.load(f)

    # Organize detections by timestamp
    detections_map = {}
    for item in all_detections:
        ts_key = round(float(item["timestamp"]), 2)
        if ts_key not in detections_map:
            detections_map[ts_key] = []
        detections_map[ts_key].append(item)

    # Open video
    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {input_video}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create video writer with H.264 codec for browser compatibility
    # Try different codecs - avc1/H264 for browser playback, fall back to mp4v
    fourcc = cv2.VideoWriter_fourcc(*"avc1")  # H.264 codec - works in browsers
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    # If avc1 doesn't work, try other H.264 variants
    if not out.isOpened():
        print("[Emotion Detection] avc1 codec not available, trying H264...")
        fourcc = cv2.VideoWriter_fourcc(*"H264")
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("[Emotion Detection] H264 codec not available, trying X264...")
        fourcc = cv2.VideoWriter_fourcc(*"X264")
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("[Emotion Detection] Falling back to mp4v codec (may not play in browser)")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    print(f"[Emotion Detection] Processing {total_frames} frames for emotion detection...")
    print(f"[Emotion Detection] Output video: {output_video}")
    print(f"[Emotion Detection] Emotion smoothing: {EMOTION_WINDOW_SECONDS}s window (prevents rapid switching)")

    all_emotion_detections = []
    frame_idx = 0

    # Emotion history for smoothing: {person_id: [(timestamp, emotion_scores), ...]}
    emotion_history = defaultdict(list)
    # Current stable emotion for each person: {person_id: (emotion, confidence)}
    stable_emotions = {}

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_idx += 1
        current_ts = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        ts_key = round(float(current_ts), 2)

        # Find detections for this frame (with small tolerance)
        current_faces = []
        keys_to_check = [
            ts_key,
            round(ts_key - 0.03, 2),
            round(ts_key + 0.03, 2),
        ]
        for k in keys_to_check:
            if k in detections_map:
                current_faces = detections_map[k]
                break

        # Process each detected face
        for face in current_faces:
            pid = face["person_id"]
            x, y, w, h = face["coordinates_pixels"]

            # Ensure coordinates are within frame bounds
            x = max(0, int(x))
            y = max(0, int(y))
            w = min(int(w), width - x)
            h = min(int(h), height - y)

            if w <= 0 or h <= 0:
                continue

            # Extract face region
            face_roi = frame[y:y+h, x:x+w]

            if face_roi.size == 0:
                continue

            # Analyze emotion using DeepFace
            try:
                # Use enforce_detection=False since we already have detected faces
                result = DeepFace.analyze(
                    face_roi,
                    actions=["emotion"],
                    enforce_detection=False,
                    silent=True
                )

                # DeepFace returns a list, get first result
                if isinstance(result, list):
                    result = result[0]

                raw_emotion = result["dominant_emotion"]
                emotion_scores = result["emotion"]

                # Add to emotion history for this person
                emotion_history[pid].append((current_ts, emotion_scores))

                # Remove old entries outside the time window
                cutoff_time = current_ts - EMOTION_WINDOW_SECONDS
                emotion_history[pid] = [(ts, scores) for ts, scores in emotion_history[pid] if ts >= cutoff_time]

                # Calculate accumulated emotion scores over the time window
                accumulated_scores = defaultdict(float)
                for ts, scores in emotion_history[pid]:
                    for emotion, score in scores.items():
                        accumulated_scores[emotion] += score

                # Find the emotion with highest accumulated confidence
                dominant_emotion = max(accumulated_scores, key=accumulated_scores.get)
                confidence = emotion_scores[dominant_emotion]  # Use current frame's confidence for display

                # Store stable emotion
                stable_emotions[pid] = (dominant_emotion, confidence)

                # Save emotion detection
                emotion_detection = {
                    "timestamp": round(float(current_ts), 2),
                    "person_id": pid,
                    "coordinates_pixels": [int(x), int(y), int(w), int(h)],
                    "emotion": dominant_emotion,
                    "confidence": round(float(confidence), 2),
                    "all_emotions": {k: round(float(v), 2) for k, v in emotion_scores.items()}
                }
                all_emotion_detections.append(emotion_detection)

                # Draw on frame
                person_color = create_unique_color(pid)
                emotion_color = get_emotion_color(dominant_emotion)

                # Draw face rectangle with person color
                cv2.rectangle(frame, (x, y), (x + w, y + h), person_color, 2)

                # Draw person ID label
                label_pid = pid
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 2

                (text_w, text_h), _ = cv2.getTextSize(label_pid, font, font_scale, thickness)
                cv2.rectangle(frame, (x, y - text_h - 10), (x + text_w + 10, y), person_color, -1)
                cv2.putText(frame, label_pid, (x + 5, y - 5), font, font_scale, (255, 255, 255), thickness)

                # Draw emotion label below the box
                label_emotion = f"{dominant_emotion} ({confidence:.0f}%)"
                (emo_w, emo_h), _ = cv2.getTextSize(label_emotion, font, font_scale, thickness)
                cv2.rectangle(frame, (x, y + h), (x + emo_w + 10, y + h + emo_h + 10), emotion_color, -1)
                cv2.putText(frame, label_emotion, (x + 5, y + h + emo_h + 5), font, font_scale, (255, 255, 255), thickness)

            except Exception as e:
                # If emotion detection fails, just draw the box without emotion
                person_color = create_unique_color(pid)
                cv2.rectangle(frame, (x, y), (x + w, y + h), person_color, 2)
                cv2.putText(frame, pid, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, person_color, 2)

        # Add frame counter
        cv2.putText(
            frame,
            f"Frame: {frame_idx}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        out.write(frame)

        # Log progress every frame
        if current_faces:
            emotions_str = ", ".join([f"{d['person_id']}:{d.get('emotion', '?')}"
                                      for d in all_emotion_detections
                                      if d['timestamp'] == round(float(current_ts), 2)])
            print(f"[Frame {frame_idx:04d}] time={current_ts:.2f}s | faces={len(current_faces)} | emotions=[{emotions_str}]")
        else:
            print(f"[Frame {frame_idx:04d}] time={current_ts:.2f}s | faces=0")

        # Report progress via callback (emotion detection is 40-100%)
        if status_callback and total_frames > 0:
            progress = 40 + int((frame_idx / total_frames) * 60)
            status_callback(f"Emotion detection: frame {frame_idx}/{total_frames}", progress)

    cap.release()
    out.release()

    # Save emotion detections to JSON
    with open(output_json, "w") as f:
        json.dump(all_emotion_detections, f, indent=4)

    print(f"\n✓ [Emotion Detection] Processing complete!")
    print(f"  - Emotion detections saved to: {output_json}")
    print(f"  - Annotated video saved to: {output_video}")
    print(f"  - Total emotion detections: {len(all_emotion_detections)}")
    
    return all_emotion_detections
