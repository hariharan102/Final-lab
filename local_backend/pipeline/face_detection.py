"""
Face Detection and Tracking Module

IMPORTANT: This code is a DIRECT COPY of the Colab notebook face detection logic.
DO NOT modify the ML algorithms, thresholds, or processing order.

The only change is: GPU → CPU execution (using CPUExecutionProvider).

Original source: final_code_emotion_detectionipynb.ipynb (Cell 1)
"""

import cv2
import json
import numpy as np
from collections import defaultdict
from insightface.app import FaceAnalysis
import os


class FaceTracker:
    """
    Face tracking using cosine similarity on embeddings.
    
    COPIED DIRECTLY FROM COLAB NOTEBOOK - DO NOT MODIFY LOGIC.
    """
    def __init__(self, similarity_threshold=0.65, max_disappeared=30, update_alpha=0.9):
        self.next_person_id = 1
        self.active_people = {}
        self.similarity_threshold = float(similarity_threshold)
        self.max_disappeared = int(max_disappeared)
        self.update_alpha = float(update_alpha)
        self.disappeared_frames = defaultdict(int)
        self.reusable_ids = []  # Pool of IDs that can be reused

    def _normalize(self, emb):
        emb = np.asarray(emb, dtype=np.float32).reshape(-1)
        norm = float(np.linalg.norm(emb) + 1e-12)
        return emb / norm

    def get_cosine_similarity(self, embedding1, embedding2):
        e1 = self._normalize(embedding1)
        e2 = self._normalize(embedding2)
        return float(np.dot(e1, e2))

    def _register(self, embedding, timestamp):
        # Reuse IDs from disappeared people if available
        if self.reusable_ids:
            person_id = self.reusable_ids.pop(0)
        else:
            person_id = self.next_person_id
            self.next_person_id += 1
        
        self.active_people[person_id] = {
            "embedding": self._normalize(embedding),
            "last_seen": float(timestamp),
        }
        self.disappeared_frames[person_id] = 0
        return person_id

    def _mark_disappeared(self):
        for person_id in list(self.active_people.keys()):
            self.disappeared_frames[person_id] += 1
            if self.disappeared_frames[person_id] > self.max_disappeared:
                del self.active_people[person_id]
                del self.disappeared_frames[person_id]
                # Add ID to reusable pool (keep sorted)
                if person_id not in self.reusable_ids:
                    self.reusable_ids.append(person_id)
                    self.reusable_ids.sort()

    def update(self, faces, timestamp):
        if not faces:
            self._mark_disappeared()
            return []

        if not self.active_people:
            assigned = []
            for face_data in faces:
                assigned.append(self._register(face_data["embedding"], timestamp))
            return assigned

        person_ids = list(self.active_people.keys())
        stored = np.stack([self.active_people[pid]["embedding"] for pid in person_ids], axis=0)

        new_embeddings = [self._normalize(f["embedding"]) for f in faces]
        new_mat = np.stack(new_embeddings, axis=0)

        sim = new_mat @ stored.T

        assigned_ids = [None] * len(faces)
        used_people = set()
        used_faces = set()

        candidates = []
        for i in range(sim.shape[0]):
            for j in range(sim.shape[1]):
                candidates.append((float(sim[i, j]), i, j))
        candidates.sort(reverse=True, key=lambda x: x[0])

        for s, i, j in candidates:
            if s < self.similarity_threshold:
                break
            if i in used_faces:
                continue
            pid = person_ids[j]
            if pid in used_people:
                continue

            assigned_ids[i] = pid
            used_faces.add(i)
            used_people.add(pid)

            old_emb = self.active_people[pid]["embedding"]
            new_emb = new_embeddings[i]
            updated = self.update_alpha * old_emb + (1.0 - self.update_alpha) * new_emb
            self.active_people[pid]["embedding"] = self._normalize(updated)
            self.active_people[pid]["last_seen"] = float(timestamp)
            self.disappeared_frames[pid] = 0

        for i, face_data in enumerate(faces):
            if assigned_ids[i] is None:
                assigned_ids[i] = self._register(face_data["embedding"], timestamp)

        for pid in list(self.active_people.keys()):
            if pid not in used_people:
                self.disappeared_frames[pid] += 1
                if self.disappeared_frames[pid] > self.max_disappeared:
                    del self.active_people[pid]
                    del self.disappeared_frames[pid]
                    # Add ID to reusable pool
                    if pid not in self.reusable_ids:
                        self.reusable_ids.append(pid)
                        self.reusable_ids.sort()

        return assigned_ids


def _bbox_xywh_from_insightface(bbox, frame_width, frame_height):
    """Convert InsightFace bbox format to x,y,w,h format."""
    x1, y1, x2, y2 = bbox
    x1 = int(round(float(x1)))
    y1 = int(round(float(y1)))
    x2 = int(round(float(x2)))
    y2 = int(round(float(y2)))

    x1 = max(0, min(x1, frame_width - 1))
    y1 = max(0, min(y1, frame_height - 1))
    x2 = max(0, min(x2, frame_width - 1))
    y2 = max(0, min(y2, frame_height - 1))

    w = max(0, x2 - x1)
    h = max(0, y2 - y1)
    return int(x1), int(y1), int(w), int(h)


def process_video_faces(video_path, output_json, status_callback=None, similarity_threshold=0.65, max_disappeared=30):
    """
    Process video for face detection and tracking.
    
    COPIED DIRECTLY FROM COLAB NOTEBOOK - DO NOT MODIFY LOGIC.
    Only change: Uses CPUExecutionProvider instead of CUDAExecutionProvider.
    
    Args:
        video_path: Path to input video file
        output_json: Path to save face detections JSON
        status_callback: Optional callback function for progress updates
        similarity_threshold: Threshold for face matching
        max_disappeared: Max frames before removing tracked face
    
    Returns:
        List of all face detections
    """
    print(f"[Face Detection] Processing {video_path}...")

    # LOCAL EXECUTION: Always use CPU
    # This is the ONLY change from Colab notebook
    import onnxruntime as ort
    available_providers = ort.get_available_providers()
    
    providers_to_use = []
    if "CUDAExecutionProvider" in available_providers:
        providers_to_use.append("CUDAExecutionProvider")
        print("✓ GPU detected, using CUDA acceleration")
    else:
        providers_to_use.append("CPUExecutionProvider")
        print("✓ Using CPU execution (local mode)")

    # Initialize InsightFace with buffalo_s model
    app = FaceAnalysis(name="buffalo_s", providers=providers_to_use)
    app.prepare(ctx_id=0, det_size=(640, 640))

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    # Get video properties for progress tracking
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Lower threshold prevents ID switching when faces turn slightly
    tracker = FaceTracker(similarity_threshold=0.45, max_disappeared=50)
    all_detections = []
    frame_count = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_count += 1
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

        try:
            faces = app.get(frame)
            frame_h, frame_w = frame.shape[:2]

            face_items = []
            for f in faces:
                if getattr(f, "embedding", None) is None:
                    continue
                x, y, w, h = _bbox_xywh_from_insightface(f.bbox, frame_w, frame_h)
                if w <= 0 or h <= 0:
                    continue
                face_items.append({
                    "embedding": np.asarray(f.embedding, dtype=np.float32),
                    "bbox": [int(x), int(y), int(w), int(h)],
                })

            assigned_ids = tracker.update(face_items, timestamp)

            # Verbose logging for every frame
            ids_str = ", ".join([f"person_{pid}" for pid in assigned_ids]) if assigned_ids else "none"
            print(f"[Frame {frame_count:04d}] time={timestamp:.2f}s | faces_detected={len(face_items)} | assigned_ids=[{ids_str}] | total_active={len(tracker.active_people)})")

            for face, person_id in zip(face_items, assigned_ids):
                if person_id is None:
                    continue
                detection = {
                    "timestamp": round(float(timestamp), 2),
                    "person_id": f"person_{int(person_id)}",
                    "coordinates_pixels": [int(v) for v in face["bbox"]],
                }
                all_detections.append(detection)

            # Report progress via callback
            if status_callback and total_frames > 0:
                progress = int((frame_count / total_frames) * 40)  # Face detection is 0-40%
                status_callback(f"Face detection: frame {frame_count}/{total_frames}", progress)

        except Exception as e:
            print(f"Error processing frame {frame_count}: {str(e)}")
            continue

    cap.release()

    with open(output_json, "w") as f:
        json.dump(all_detections, f, indent=4)

    print(f"\n[Face Detection] Complete! Saved {len(all_detections)} detections to {output_json}")
    return all_detections


def create_unique_color(identifier):
    """Create a unique color based on the identifier."""
    hash_val = hash(identifier)
    r = (hash_val & 0xFF0000) >> 16
    g = (hash_val & 0x00FF00) >> 8
    b = hash_val & 0x0000FF
    return (b, g, r)


def visualize_tracking(input_video, input_json, output_video):
    """
    Visualize face tracking results on video.
    
    COPIED DIRECTLY FROM COLAB NOTEBOOK - DO NOT MODIFY LOGIC.
    """
    print(f"[Visualization] Loading data from {input_json}...")
    with open(input_json, "r") as f:
        all_detections = json.load(f)

    detections_map = {}
    for item in all_detections:
        ts_key = round(float(item["timestamp"]), 2)
        if ts_key not in detections_map:
            detections_map[ts_key] = []
        detections_map[ts_key].append(item)

    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {input_video}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    print(f"[Visualization] Generating debug video: {output_video}...")
    frame_idx = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        current_ts = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        ts_key = round(float(current_ts), 2)

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

        if current_faces:
            for face in current_faces:
                pid = face["person_id"]
                x, y, w, h = face["coordinates_pixels"]

                color = create_unique_color(pid)
                cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), color, 2)

                label = pid
                font_scale = 0.6
                thickness = 2
                font = cv2.FONT_HERSHEY_SIMPLEX

                (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)

                cv2.rectangle(
                    frame,
                    (int(x), int(y - text_height - 10)),
                    (int(x + text_width + 10), int(y)),
                    color,
                    -1,
                )

                cv2.putText(
                    frame,
                    label,
                    (int(x + 5), int(y - 5)),
                    font,
                    font_scale,
                    (255, 255, 255),
                    thickness,
                )

        cv2.putText(
            frame,
            f"Frame: {frame_idx}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        out.write(frame)
        frame_idx += 1

        if frame_idx % 100 == 0:
            print(f"[Visualization] Processed {frame_idx} frames...")

    cap.release()
    out.release()

    print(f"[Visualization] Done! Created '{output_video}'")
