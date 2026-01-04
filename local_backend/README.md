# Local Emotion Detection Backend

## Overview

This is a **SEPARATE** backend for local CPU-based execution of the emotion detection pipeline.
It runs **independently** from the existing Colab/Google Drive backend.

## Architecture

```
Frontend (React)
     ↓
Execution Mode Toggle
     ↓
┌──────────────────────────────────────────────────┐
│  Mode = Colab                                    │
│  → Existing Django Backend (backend/)            │
│  → Google Drive + Manual Colab Execution         │
├──────────────────────────────────────────────────┤
│  Mode = Local                                    │
│  → THIS Backend (local_backend/)                 │
│  → Automatic CPU Execution (No GPU Required)     │
└──────────────────────────────────────────────────┘
```

## Key Differences from Colab Backend

| Aspect              | Colab Backend            | Local Backend           |
|---------------------|--------------------------|-------------------------|
| Execution           | Manual (user runs Colab) | Automatic (background)  |
| Hardware            | GPU (T4 in Colab)        | CPU only                |
| Storage             | Google Drive             | Local filesystem        |
| OAuth Required      | Yes                      | No                      |
| Framework           | Django + DRF             | FastAPI                 |
| Port                | 8000                     | 8001                    |

## API Endpoints

| Method | Endpoint                      | Description                    |
|--------|-------------------------------|--------------------------------|
| POST   | `/local/jobs/upload`          | Upload video, start processing |
| GET    | `/local/jobs/{job_id}/status` | Get job status                 |
| GET    | `/local/jobs/{job_id}/results`| Get results (video + JSON)     |
| GET    | `/local/jobs/{job_id}/stream` | Stream processed video         |

## Project Structure

```
local_backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── models.py               # Job model and database
├── routes.py               # API route handlers
├── pipeline/
│   ├── __init__.py
│   ├── face_detection.py   # InsightFace face tracking (from Colab)
│   └── emotion_detection.py # DeepFace emotion analysis (from Colab)
├── storage/
│   ├── input_videos/       # Uploaded videos
│   ├── output_videos/      # Processed videos
│   ├── output_json/        # Emotion detection results
│   └── status/             # Job status files
└── README.md
```

## Installation

```bash
cd local_backend
pip install -r requirements.txt
```

## Running

```bash
# From the local_backend directory
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Important Notes

1. **DO NOT** modify this backend to use GPU - it's designed for CPU-only execution
2. **DO NOT** merge this with the Colab backend - they are separate services
3. **DO NOT** add Google Drive/OAuth integration - this uses local storage only
4. The ML pipeline logic is **IDENTICAL** to the Colab notebook - just CPU-optimized

## ML Pipeline (Copied from Colab)

The pipeline executes in this order:
1. **Face Detection + Tracking** (InsightFace Buffalo-S)
2. **Emotion Detection** (DeepFace)
3. **Video Annotation** (OpenCV)

This is the **exact same logic** as the Colab notebook, just running locally on CPU.
