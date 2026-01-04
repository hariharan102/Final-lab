"""
Local Emotion Detection Backend - FastAPI Application

This is a SEPARATE backend from the existing Colab/Django backend.
It runs on port 8001 and handles LOCAL CPU-based video processing.

Architecture Overview:
======================
┌────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                          │
│                     Execution Mode Toggle                       │
└────────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┴──────────────────┐
           ▼                                     ▼
┌─────────────────────────┐      ┌─────────────────────────────┐
│   COLAB BACKEND         │      │   LOCAL BACKEND (THIS)      │
│   Django @ port 8000    │      │   FastAPI @ port 8001       │
│   - Google Drive        │      │   - Local filesystem        │
│   - Manual Colab run    │      │   - Automatic execution     │
│   - GPU (T4)            │      │   - CPU only                │
└─────────────────────────┘      └─────────────────────────────┘

Key Differences:
================
- This backend runs ML pipeline AUTOMATICALLY (no manual Colab step)
- Uses CPU execution (works on any machine without GPU)
- Stores files locally (no Google Drive or OAuth required)
- Simpler setup for development and testing

Usage:
======
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload

API Documentation:
==================
    http://localhost:8001/docs (Swagger UI)
    http://localhost:8001/redoc (ReDoc)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import init_db
from routes import router as jobs_router

# Initialize FastAPI application
app = FastAPI(
    title="Local Emotion Detection Backend",
    description="""
    ## Local CPU-Based Emotion Detection API
    
    This backend processes videos **locally** using CPU, without requiring Google Colab or GPU.
    
    ### Key Features:
    - **Automatic Processing**: Upload video → Processing starts immediately
    - **CPU Execution**: Works on any machine (no GPU required)
    - **Local Storage**: All files stored locally (no Google Drive)
    
    ### API Endpoints:
    - `POST /local/jobs/upload` - Upload video and start processing
    - `GET /local/jobs/{job_id}/status` - Get processing status
    - `GET /local/jobs/{job_id}/results` - Get results (video + JSON)
    - `GET /local/jobs/{job_id}/stream` - Stream processed video
    
    ### Note:
    This is a SEPARATE backend from the Colab backend running on port 8000.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend communication
# Allows requests from React frontend (typically running on port 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite dev server
        "http://localhost:3000",    # Create React App
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(jobs_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    print("=" * 60)
    print("LOCAL EMOTION DETECTION BACKEND")
    print("=" * 60)
    print("📍 This is the LOCAL backend (CPU-based)")
    print("📍 Colab backend runs separately on port 8000")
    print("=" * 60)
    
    # Initialize SQLite database
    init_db()
    print("✅ Database initialized")
    print("✅ Ready to accept requests on port 8001")
    print()


@app.get("/")
async def root():
    """
    Root endpoint - provides API information.
    """
    return {
        "name": "Local Emotion Detection Backend",
        "version": "1.0.0",
        "execution_mode": "local",
        "description": "CPU-based automatic video processing",
        "endpoints": {
            "upload": "POST /local/jobs/upload",
            "status": "GET /local/jobs/{job_id}/status",
            "results": "GET /local/jobs/{job_id}/results",
            "stream": "GET /local/jobs/{job_id}/stream"
        },
        "colab_backend": "http://localhost:8000 (separate service)",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "backend": "local",
        "port": 8001
    }


# For running directly with Python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
