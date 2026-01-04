# 🏗️ System Architecture Diagram

## Complete System Architecture

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                      EMOTION DETECTION SYSTEM ARCHITECTURE                     ║
║                          Dual-Backend AI Video Processing                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE LAYER                              │
│                          (React SPA - Vite Dev Server)                         │
│                                 Port: 3001                                     │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ UploadPage  │  │ Processing  │  │  Results    │  │  History    │         │
│  │             │  │    Page     │  │   Page      │  │   Page      │         │
│  │ • Mode      │  │ • Status    │  │ • Video     │  │ • Colab     │         │
│  │   Select    │  │   Polling   │  │   Player    │  │   Jobs      │         │
│  │ • File      │  │ • Progress  │  │ • Charts    │  │ • Local     │         │
│  │   Upload    │  │   Bar       │  │ • Download  │  │   Jobs      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────┐           │
│  │              Shared Context: ExecutionModeContext              │           │
│  │              (Global State: 'colab' or 'local')                │           │
│  └────────────────────────────────────────────────────────────────┘           │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────┐           │
│  │                    API Service Layer (api.js)                   │           │
│  │  • uploadVideo()  • getJobStatus()  • getJobResults()          │           │
│  │  • getAllJobs()   • terminateJob()  • getVideoStreamUrl()      │           │
│  └────────────────────────────────────────────────────────────────┘           │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
    ╔═══════════════════════════════╗   ╔═══════════════════════════════╗
    ║     COLAB BACKEND (Django)    ║   ║   LOCAL BACKEND (FastAPI)     ║
    ║         Port: 8000            ║   ║         Port: 8001            ║
    ╚═══════════════════════════════╝   ╚═══════════════════════════════╝

┌───────────────────────────────┐   ┌───────────────────────────────────┐
│    COLAB BACKEND DETAILS      │   │    LOCAL BACKEND DETAILS          │
├───────────────────────────────┤   ├───────────────────────────────────┤
│                               │   │                                   │
│ Technology Stack:             │   │ Technology Stack:                 │
│ • Django 4.x                  │   │ • FastAPI                         │
│ • Django REST Framework       │   │ • SQLAlchemy ORM                  │
│ • PostgreSQL/SQLite           │   │ • SQLite Database                 │
│ • Google Drive API            │   │ • Background Threading            │
│                               │   │ • Async/Await Support             │
│ Processing Mode:              │   │                                   │
│ • Manual (User runs Colab)    │   │ Processing Mode:                  │
│ • GPU Acceleration            │   │ • Automatic (API triggers)        │
│ • Google Colab Runtime        │   │ • CPU Processing                  │
│                               │   │ • Local Python Thread             │
│ API Endpoints:                │   │                                   │
│ POST /api/jobs/upload/        │   │ API Endpoints:                    │
│ GET  /api/jobs/<id>/status/   │   │ POST /local/jobs/upload           │
│ GET  /api/jobs/<id>/results/  │   │ GET  /local/jobs/<id>/status      │
│ GET  /api/jobs/<id>/stream/   │   │ GET  /local/jobs/<id>/results     │
│ GET  /api/jobs/<id>/json/     │   │ GET  /local/jobs/<id>/stream      │
│ GET  /api/jobs/               │   │ GET  /local/jobs/<id>/json        │
│ POST /api/jobs/<id>/terminate/│   │ POST /local/jobs/<id>/terminate   │
│                               │   │ GET  /local/jobs-list             │
│ Storage:                      │   │                                   │
│ • Google Drive                │   │ Storage:                          │
│   - input_videos/             │   │ • Local Filesystem                │
│   - output_videos/            │   │   - storage/input_videos/         │
│   - output_json/              │   │   - storage/output_videos/        │
│   - status/                   │   │   - storage/output_json/          │
│                               │   │   - storage/status/               │
│ Database Model:               │   │   - storage/temp/                 │
│ • VideoJob                    │   │                                   │
│   - id (UUID)                 │   │ Database Model:                   │
│   - status                    │   │ • LocalJob                        │
│   - original_filename         │   │   - id (UUID)                     │
│   - drive_file_id             │   │   - status                        │
│   - colab_url                 │   │   - input_video_path              │
│   - created_at                │   │   - output_video_path             │
│   - updated_at                │   │   - output_json_path              │
│                               │   │   - progress                      │
│                               │   │   - created_at                    │
│                               │   │   - updated_at                    │
└───────────────────────────────┘   └───────────────────────────────────┘
                │                                      │
                │                                      │
                ▼                                      ▼
┌───────────────────────────────┐   ┌───────────────────────────────────┐
│   GOOGLE COLAB RUNTIME        │   │   LOCAL PIPELINE RUNNER           │
│   (Manual Execution)          │   │   (Automatic Background Task)     │
├───────────────────────────────┤   ├───────────────────────────────────┤
│                               │   │                                   │
│ • User clicks "Run All"       │   │ • Triggered automatically on      │
│ • GPU T4/P100/V100            │   │   video upload                    │
│ • Mounts Google Drive         │   │ • Runs in Python thread           │
│ • Reads from Drive folders    │   │ • Updates status in DB            │
│ • Writes back to Drive        │   │                                   │
│                               │   │ File: pipeline/runner.py          │
│ File: Colab Notebook          │   │ Function: run_emotion_pipeline()  │
│       (.ipynb)                │   │                                   │
└───────────────────────────────┘   └───────────────────────────────────┘
                │                                      │
                └──────────────┬───────────────────────┘
                               │
                               ▼
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        AI/ML PROCESSING PIPELINE                               ║
║                    (Identical Logic in Both Backends)                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

                          INPUT: video.mp4 (User Upload)
                                       │
                                       ▼
        ┌─────────────────────────────────────────────────────────────┐
        │                  STAGE 1: FACE DETECTION                     │
        │                  Library: InsightFace                        │
        ├─────────────────────────────────────────────────────────────┤
        │                                                              │
        │  File: pipeline/face_detection.py                           │
        │  Function: process_video_faces()                            │
        │                                                              │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  1. Load InsightFace Model (buffalo_l)             │    │
        │  │     - Model Size: ~400MB                           │    │
        │  │     - Providers: CUDA (GPU) or CPU                 │    │
        │  │     - Input Size: 640×640                          │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  2. Open Video with OpenCV                         │    │
        │  │     - Get FPS, frame count, resolution             │    │
        │  │     - Process EVERY frame (no skipping)            │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  3. For Each Frame:                                │    │
        │  │     a. Detect faces with InsightFace               │    │
        │  │     b. Get bounding box [x, y, w, h]               │    │
        │  │     c. Extract 512-dim face embedding              │    │
        │  │     d. Track face across frames (ID assignment)    │    │
        │  │     e. Calculate confidence score                  │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  4. Face Tracking Logic:                           │    │
        │  │     - Compare embeddings with previous frames      │    │
        │  │     - If distance < 50px → Same person             │    │
        │  │     - If distance > 50px → New person (new ID)     │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  OUTPUT: face_detections.json                               │
        │  [                                                           │
        │    {                                                         │
        │      "frame_number": 0,                                      │
        │      "timestamp": 0.0,                                       │
        │      "face_id": "face_001",                                  │
        │      "bbox": [100, 150, 80, 100],                            │
        │      "confidence": 0.99,                                     │
        │      "embedding": [512 floats]                               │
        │    }                                                         │
        │  ]                                                           │
        │                                                              │
        │  Processing Speed: ~0.033 sec/frame (30 FPS video)          │
        │  Progress Updates: 5% → 40%                                 │
        └─────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
        ┌─────────────────────────────────────────────────────────────┐
        │                 STAGE 2: EMOTION DETECTION                   │
        │                   Library: DeepFace                          │
        ├─────────────────────────────────────────────────────────────┤
        │                                                              │
        │  File: pipeline/emotion_detection.py                        │
        │  Function: analyze_emotions()                               │
        │                                                              │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  1. Load DeepFace Emotion Model                    │    │
        │  │     - Model: VGG-Face based                        │    │
        │  │     - Input Size: 48×48 grayscale                  │    │
        │  │     - Model Size: ~15MB                            │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  2. Load Face Detections JSON                      │    │
        │  │     - Parse all detected faces                     │    │
        │  │     - Group by frame number                        │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  3. For Each Face Detection:                       │    │
        │  │     a. Crop face region from video frame           │    │
        │  │     b. Resize to 48×48 grayscale                   │    │
        │  │     c. Pass to DeepFace.analyze()                  │    │
        │  │     d. Get emotion probabilities (7 emotions)      │    │
        │  │     e. Apply temporal smoothing (5-sec window)     │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  4. Emotion Smoothing Algorithm:                   │    │
        │  │     Window: 5.0 seconds                            │    │
        │  │     Method: Average scores across time window      │    │
        │  │     Filter: Confidence > 30%                       │    │
        │  │     Purpose: Reduce emotion flicker                │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  5. Emotion Categories (7 total):                  │    │
        │  │     • angry      → Red (0, 0, 255)                 │    │
        │  │     • disgust    → Dark Green (0, 128, 0)          │    │
        │  │     • fear       → Purple (128, 0, 128)            │    │
        │  │     • happy      → Yellow (0, 255, 255)            │    │
        │  │     • sad        → Blue (255, 0, 0)                │    │
        │  │     • surprise   → Orange (0, 165, 255)            │    │
        │  │     • neutral    → Gray (128, 128, 128)            │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  OUTPUT: emotions.json                                      │
        │  [                                                           │
        │    {                                                         │
        │      "frame_number": 0,                                      │
        │      "timestamp": 0.0,                                       │
        │      "face_id": "face_001",                                  │
        │      "bbox": [100, 150, 80, 100],                            │
        │      "emotion": "happy",                                     │
        │      "confidence": 87.5,                                     │
        │      "all_emotions": {                                       │
        │        "happy": 87.5, "neutral": 8.2, "surprise": 3.1,      │
        │        "sad": 0.8, "angry": 0.3, "fear": 0.1, "disgust": 0.0│
        │      }                                                       │
        │    }                                                         │
        │  ]                                                           │
        │                                                              │
        │  Processing Speed: ~0.05 sec/face                           │
        │  Progress Updates: 45% → 85%                                │
        └─────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
        ┌─────────────────────────────────────────────────────────────┐
        │                 STAGE 3: VIDEO ANNOTATION                    │
        │                    Library: OpenCV                           │
        ├─────────────────────────────────────────────────────────────┤
        │                                                              │
        │  File: pipeline/emotion_detection.py (integrated)           │
        │  Function: analyze_emotions() → video writing section       │
        │                                                              │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  1. Open Original Video with cv2.VideoCapture      │    │
        │  │     - Match FPS, resolution, codec                 │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  2. Create Output Video Writer                     │    │
        │  │     - Try codec: avc1 (best browser support)       │    │
        │  │     - Fallback: H264                               │    │
        │  │     - Fallback: X264                               │    │
        │  │     - Format: .mp4                                 │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  3. For Each Frame:                                │    │
        │  │     a. Read frame from original video              │    │
        │  │     b. Lookup emotions for this frame              │    │
        │  │     c. For each detected face:                     │    │
        │  │        - Draw colored rectangle (emotion color)    │    │
        │  │        - Add emotion label text                    │    │
        │  │        - Add confidence percentage                 │    │
        │  │        - Add face ID for tracking                  │    │
        │  │     d. Write annotated frame to output             │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  4. Annotation Details:                            │    │
        │  │     - Box Thickness: 2px                           │    │
        │  │     - Font: FONT_HERSHEY_SIMPLEX                   │    │
        │  │     - Font Scale: 0.6                              │    │
        │  │     - Text Color: Emotion-based                    │    │
        │  │     - Background: Semi-transparent                 │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  OUTPUT: annotated_video.mp4                                │
        │  - Video with bounding boxes                                │
        │  - Emotion labels on each face                              │
        │  - Confidence scores displayed                              │
        │  - Face tracking IDs shown                                  │
        │                                                              │
        │  Processing Speed: ~0.01 sec/frame                          │
        │  Progress Updates: 90% → 95%                                │
        └─────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
        ┌─────────────────────────────────────────────────────────────┐
        │           STAGE 4: POST-PROCESSING & FINALIZATION            │
        ├─────────────────────────────────────────────────────────────┤
        │                                                              │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  1. Video Format Conversion (if needed)            │    │
        │  │     - Ensure H264 codec for browser playback       │    │
        │  │     - Use FFmpeg if available                      │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  2. Move Files to Final Locations                  │    │
        │  │     - output_videos/{job_id}.mp4                   │    │
        │  │     - output_json/{job_id}.json                    │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  3. Clean Up Temporary Files                       │    │
        │  │     - temp/face_detections.json                    │    │
        │  │     - temp/temp_output.mp4                         │    │
        │  │     - temp/cropped_faces/                          │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  ┌────────────────────────────────────────────────────┐    │
        │  │  4. Update Database Status                         │    │
        │  │     - Status: DONE                                 │    │
        │  │     - Message: "Processing complete!"              │    │
        │  │     - Progress: 100%                               │    │
        │  └────────────────────────────────────────────────────┘    │
        │                          ↓                                   │
        │  FINAL OUTPUTS (3 files):                                   │
        │  • output_videos/{job_id}.mp4  → Annotated video            │
        │  • output_json/{job_id}.json   → Emotion data               │
        │  • status/{job_id}.json        → Final status               │
        │                                                              │
        │  Progress Updates: 100%                                     │
        └─────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║                            DATA FLOW SUMMARY                                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   User      │      │   React     │      │  Backend    │      │  Pipeline   │
│             │      │  Frontend   │      │   API       │      │  Runner     │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
       │                     │                     │                     │
       │ Upload video.mp4    │                     │                     │
       │────────────────────>│                     │                     │
       │                     │ POST /jobs/upload   │                     │
       │                     │────────────────────>│                     │
       │                     │                     │ Create job (PENDING)│
       │                     │                     │────────────────────>│
       │                     │ Job ID + status     │                     │
       │                     │<────────────────────│                     │
       │ Job ID displayed    │                     │                     │
       │<────────────────────│                     │ Start pipeline      │
       │                     │                     │────────────────────>│
       │                     │ Poll status (1s)    │                     │
       │                     │────────────────────>│                     │
       │                     │ Status: PROCESSING  │                     │
       │                     │<────────────────────│                     │
       │ Progress: 15%       │                     │                     │
       │<────────────────────│                     │ Face detection...   │
       │                     │                     │                     │─┐
       │                     │                     │                     │ │
       │                     │ Poll status (1s)    │                     │ │
       │                     │────────────────────>│                     │ │
       │                     │ Status: PROCESSING  │                     │ │
       │                     │<────────────────────│                     │<┘
       │ Progress: 50%       │                     │                     │
       │<────────────────────│                     │ Emotion detection...│
       │                     │                     │                     │─┐
       │                     │                     │                     │ │
       │                     │ Poll status (1s)    │                     │ │
       │                     │────────────────────>│                     │ │
       │                     │ Status: PROCESSING  │                     │ │
       │                     │<────────────────────│                     │<┘
       │ Progress: 90%       │                     │                     │
       │<────────────────────│                     │ Video annotation... │
       │                     │                     │                     │─┐
       │                     │                     │                     │ │
       │                     │ Poll status (1s)    │                     │ │
       │                     │────────────────────>│                     │ │
       │                     │ Status: DONE        │                     │ │
       │                     │<────────────────────│                     │<┘
       │ Navigate to Results │                     │                     │
       │<────────────────────│                     │                     │
       │                     │ GET /jobs/id/results│                     │
       │                     │────────────────────>│                     │
       │                     │ Video URL + JSON    │                     │
       │                     │<────────────────────│                     │
       │ Play video + charts │                     │                     │
       │<────────────────────│                     │                     │
       │                     │ Stream video        │                     │
       │                     │────────────────────>│                     │
       │                     │ Video chunks        │                     │
       │                     │<────────────────────│                     │
       │ Watch annotated vid │                     │                     │
       │<────────────────────│                     │                     │

╔═══════════════════════════════════════════════════════════════════════════════╗
║                          TECHNOLOGY STACK SUMMARY                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

FRONTEND:
├── React 18.x
├── React Router 6.x (Navigation)
├── Recharts (Emotion visualization)
├── Axios (HTTP client)
└── Vite (Build tool & dev server)

COLAB BACKEND:
├── Django 4.x
├── Django REST Framework
├── PostgreSQL / SQLite
├── Google Drive API (pydrive2)
└── Python 3.10+

LOCAL BACKEND:
├── FastAPI
├── SQLAlchemy (ORM)
├── SQLite
├── Uvicorn (ASGI server)
└── Python 3.10+

AI/ML LIBRARIES:
├── InsightFace 0.7.3 (Face detection)
├── DeepFace 0.0.79 (Emotion detection)
├── OpenCV 4.8+ (Video processing)
├── NumPy 1.26.4 (Numerical computing)
├── ONNX Runtime (Model inference)
└── TensorFlow/Keras (DeepFace backend)

DEPLOYMENT:
├── Local Development: Vite Dev Server + Django/FastAPI
├── Production: Nginx + Gunicorn/Uvicorn
└── Google Colab: Jupyter Runtime with GPU

╔═══════════════════════════════════════════════════════════════════════════════╗
║                            FILE STRUCTURE                                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Final lab/
│
├── frontend/                          # React SPA
│   ├── src/
│   │   ├── components/
│   │   │   └── EmotionChart.jsx      # Recharts emotion visualization
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx        # Video upload + mode selection
│   │   │   ├── ProcessingPage.jsx    # Status polling + progress bar
│   │   │   ├── ResultsPage.jsx       # Video player + charts
│   │   │   └── HistoryPage.jsx       # Job history (Colab/Local)
│   │   ├── context/
│   │   │   └── ExecutionModeContext.jsx  # Global mode state
│   │   ├── services/
│   │   │   └── api.js                # API client for both backends
│   │   └── main.jsx
│   └── package.json
│
├── backend/                           # Django Backend (Colab mode)
│   ├── jobs/
│   │   ├── models.py                 # VideoJob model
│   │   ├── views.py                  # REST API endpoints
│   │   ├── serializers.py            # JSON serialization
│   │   └── urls.py                   # URL routing
│   ├── emotion_backend/
│   │   ├── settings.py               # Django config
│   │   └── urls.py                   # Main URL routing
│   ├── manage.py
│   └── requirements.txt
│
├── local_backend/                     # FastAPI Backend (Local mode)
│   ├── pipeline/
│   │   ├── face_detection.py         # InsightFace integration
│   │   ├── emotion_detection.py      # DeepFace integration
│   │   └── runner.py                 # Pipeline orchestration
│   ├── models.py                     # LocalJob SQLAlchemy model
│   ├── routes.py                     # FastAPI endpoints
│   ├── main.py                       # FastAPI app entry
│   ├── requirements.txt
│   └── storage/
│       ├── input_videos/             # Uploaded videos
│       ├── output_videos/            # Annotated videos
│       ├── output_json/              # Emotion data JSON
│       ├── status/                   # Real-time status updates
│       └── temp/                     # Intermediate files
│
└── Colab Notebooks/
    └── final_code_emotion_detection.ipynb  # Original ML pipeline

```

---

*Last Updated: January 3, 2026*
