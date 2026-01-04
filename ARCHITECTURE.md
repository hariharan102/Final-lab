# Dual Backend Architecture Documentation

## Overview

This project supports **TWO separate execution modes** for emotion detection:

1. **Colab Mode** (existing) - Manual GPU processing via Google Colab
2. **Local Mode** (new) - Automatic CPU processing on local machine

Each mode uses its **OWN backend** - they are completely separate services.

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React)                              │
│                          http://localhost:5173                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Execution Mode Toggle                          │  │
│  │              [ ☁️ Colab GPU ]  [ 💻 Local CPU ]                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┴──────────────────┐
           │                                     │
           ▼                                     ▼
┌──────────────────────────┐      ┌─────────────────────────────────────┐
│    COLAB BACKEND         │      │       LOCAL BACKEND                 │
│    Django + DRF          │      │       FastAPI                       │
│    Port 8000             │      │       Port 8001                     │
├──────────────────────────┤      ├─────────────────────────────────────┤
│ • Google Drive storage   │      │ • Local filesystem storage          │
│ • OAuth authentication   │      │ • No authentication required        │
│ • Manual Colab execution │      │ • Automatic background execution    │
│ • GPU (T4) processing    │      │ • CPU-only processing               │
└──────────────────────────┘      └─────────────────────────────────────┘
           │                                     │
           ▼                                     ▼
┌──────────────────────────┐      ┌─────────────────────────────────────┐
│  GOOGLE COLAB NOTEBOOK   │      │     LOCAL PYTHON PIPELINE           │
│  (User runs manually)    │      │     (Runs automatically)            │
│                          │      │                                     │
│  • InsightFace (GPU)     │      │  • InsightFace (CPU)                │
│  • DeepFace (GPU)        │      │  • DeepFace (CPU)                   │
│  • T4 GPU acceleration   │      │  • No GPU required                  │
└──────────────────────────┘      └─────────────────────────────────────┘
```

## Backend Comparison

| Feature                | Colab Backend (Django)      | Local Backend (FastAPI)     |
|------------------------|-----------------------------|-----------------------------|
| **Port**               | 8000                        | 8001                        |
| **Framework**          | Django + Django REST        | FastAPI                     |
| **Database**           | SQLite (db.sqlite3)         | SQLite (local_backend.db)   |
| **Storage**            | Google Drive                | Local filesystem            |
| **Authentication**     | OAuth (Google)              | None                        |
| **Processing**         | Manual (user runs Colab)    | Automatic (background)      |
| **Hardware**           | GPU (Colab T4)              | CPU only                    |
| **Speed**              | Fast (GPU)                  | Slower (CPU)                |
| **Setup Complexity**   | High (OAuth, Drive)         | Low (just run it)           |

## API Endpoints

### Colab Backend (Port 8000)

| Method | Endpoint                    | Description                     |
|--------|-----------------------------|---------------------------------|
| POST   | `/api/jobs/upload/`         | Upload video to Google Drive    |
| GET    | `/api/jobs/{id}/status/`    | Get job status (from Drive)     |
| GET    | `/api/jobs/{id}/results/`   | Get results (from Drive)        |
| GET    | `/api/jobs/{id}/stream/`    | Stream video (from Drive)       |

### Local Backend (Port 8001)

| Method | Endpoint                      | Description                     |
|--------|-------------------------------|---------------------------------|
| POST   | `/local/jobs/upload`          | Upload video, start auto-process|
| GET    | `/local/jobs/{id}/status`     | Get job status (local file)     |
| GET    | `/local/jobs/{id}/results`    | Get results (local file)        |
| GET    | `/local/jobs/{id}/stream`     | Stream video (local file)       |

## File Structure

```
Final lab/
├── backend/                    # EXISTING Colab backend (DO NOT MODIFY)
│   ├── manage.py
│   ├── emotion_backend/
│   └── jobs/
│
├── local_backend/              # NEW Local backend
│   ├── main.py                 # FastAPI entry point
│   ├── models.py               # Database models
│   ├── routes.py               # API routes
│   ├── requirements.txt        # Dependencies
│   ├── pipeline/               # ML pipeline (COPY of Colab logic)
│   │   ├── face_detection.py   # InsightFace face tracking
│   │   └── emotion_detection.py # DeepFace emotion analysis
│   └── storage/                # Local file storage
│       ├── input_videos/
│       ├── output_videos/
│       ├── output_json/
│       └── status/
│
├── frontend/                   # React frontend (UPDATED)
│   └── src/
│       ├── context/
│       │   └── ExecutionModeContext.jsx  # Mode state management
│       ├── components/
│       │   └── ExecutionModeSelector.jsx # Mode toggle UI
│       ├── services/
│       │   └── api.js                    # Dual-backend API calls
│       └── pages/
│           ├── UploadPage.jsx            # Updated for dual-mode
│           ├── ProcessingPage.jsx        # Updated for dual-mode
│           └── ResultsPage.jsx           # Updated for dual-mode
│
├── start_dual_backends.bat     # Start both backends
└── ARCHITECTURE.md             # This file
```

## How Frontend Handles Dual Mode

### ExecutionModeContext

The `ExecutionModeContext` provides global state for the execution mode:

```javascript
const { mode, setMode, isColab, isLocal, modeInfo } = useExecutionMode();
```

- `mode`: Current mode ('colab' or 'local')
- `setMode`: Function to change mode
- `isColab`: Boolean shortcut
- `isLocal`: Boolean shortcut
- `modeInfo`: UI info (name, icon, features)

### API Service

The `api.js` service routes requests to the correct backend:

```javascript
// Upload to appropriate backend based on mode
const response = await uploadVideo(videoFile, mode);

// Get status from appropriate backend
const status = await getJobStatus(jobId, mode);
```

### Mode Persistence

The selected mode is:
1. Stored in `localStorage` for persistence
2. Passed via React Router `location.state` during navigation
3. Used by all API calls automatically

## Running the System

### Option 1: Dual Mode (Both Backends)

```bash
# Run the startup script
start_dual_backends.bat

# Start frontend separately
cd frontend
npm run dev
```

### Option 2: Local Only

```bash
# Start local backend
cd local_backend
start_local_backend.bat

# Start frontend
cd frontend
npm run dev
```

### Option 3: Colab Only (Original)

```bash
# Start Django backend
cd backend
python manage.py runserver 8000

# Start frontend
cd frontend
npm run dev
```

## Important Notes

### What NOT to Do

1. **DO NOT** merge the two backends into one service
2. **DO NOT** add GPU logic to the local backend
3. **DO NOT** add Google Drive/OAuth to local backend
4. **DO NOT** modify the original Colab backend
5. **DO NOT** change the ML pipeline logic (only infrastructure)

### ML Pipeline Integrity

The local backend's ML pipeline is a **DIRECT COPY** of the Colab notebook:

- `face_detection.py` - Copied from notebook Cell 1
- `emotion_detection.py` - Copied from notebook Cell 4

The only changes are:
- GPU → CPU execution provider
- File paths (Google Drive → local filesystem)
- Status updates (Drive files → local JSON files)

### Performance Expectations

| Mode  | Video Length | Expected Time |
|-------|--------------|---------------|
| Colab | 1 minute     | ~30 seconds   |
| Local | 1 minute     | ~5-10 minutes |

Local mode is significantly slower because it uses CPU instead of GPU.

## Troubleshooting

### Local Backend Issues

1. **"Cannot connect to backend on port 8001"**
   - Make sure local backend is running: `cd local_backend && python main.py`
   - Check if port 8001 is available

2. **"InsightFace model download failed"**
   - First run downloads models (~100MB)
   - Ensure internet connection
   - Models are cached after first download

3. **"Processing is very slow"**
   - This is expected for CPU execution
   - Consider shorter videos for testing
   - Use Colab mode for faster processing

### Frontend Issues

1. **Mode doesn't persist after refresh**
   - Check browser localStorage
   - Clear localStorage if corrupted

2. **Wrong backend called**
   - Verify mode in browser console
   - Check network tab for request URL

## Academic Context

This dual-backend architecture is designed for:
- **Flexibility**: Choose GPU (fast) or CPU (accessible) based on resources
- **Separation of Concerns**: Each backend handles one execution mode
- **Maintainability**: Changes to one backend don't affect the other
- **Academic Clarity**: Clear architecture for understanding and presentation
