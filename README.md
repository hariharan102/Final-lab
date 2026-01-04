# Offline Meeting Emotion Detection System

## 🎯 Project Overview

A full-stack web application for detecting and analyzing emotions in meeting videos using GPU-accelerated AI models. The system leverages **Google Colab for GPU processing** while maintaining a clean separation between the web application and AI inference.

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   React     │────▶│   Django    │────▶│ Google Drive │────▶│ Google Colab │
│  Frontend   │     │   Backend   │     │  (Storage)   │     │   (GPU AI)   │
│             │◀────│             │◀────│              │◀────│              │
└─────────────┘     └─────────────┘     └──────────────┘     └──────────────┘
```

### Data Flow

1. **Upload Phase:**
   - User uploads video via React frontend
   - Django backend saves to Google Drive
   - Backend returns job_id and Colab notebook URL

2. **Processing Phase (Manual):**
   - User opens Colab notebook
   - User clicks "Run All" to start GPU processing
   - Colab reads video from Google Drive
   - Colab writes live status updates to Google Drive

3. **Monitoring Phase:**
   - Frontend polls backend every 2-3 seconds
   - Backend reads status from Google Drive
   - Frontend displays live progress

4. **Results Phase:**
   - Colab writes processed video + JSON to Google Drive
   - Backend fetches results from Google Drive
   - Frontend displays annotated video and emotion statistics

## 🚀 Technology Stack

### Frontend
- **React 18** - UI framework
- **React Router v6** - Client-side routing
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Vite** - Build tool

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API layer
- **Google Drive API** - Cloud storage integration
- **SQLite** - Database

### AI/ML (Google Colab)
- **InsightFace (Buffalo-S)** - Face detection & tracking
- **DeepFace** - Emotion detection
- **OpenCV** - Video processing & annotation

## 📋 Prerequisites

- **Python 3.8+** for Django backend
- **Node.js 16+** for React frontend
- **Google Account** for Drive API and Colab
- **Google Cloud Project** with Drive API enabled

## 🛠️ Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up Google Drive API (see backend/README.md)
# Place credentials.json in backend/

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Backend will run at: `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at: `http://localhost:3000`

### 3. Google Drive API Setup

See detailed instructions in [backend/README.md](backend/README.md#google-drive-api-setup)

**Summary:**
1. Create Google Cloud project
2. Enable Google Drive API
3. Create OAuth 2.0 credentials
4. Download `credentials.json`
5. Place in `backend/` directory
6. Run first-time authentication

### 4. Google Colab Setup

See [colab_template.ipynb](colab_template.ipynb) for the processing notebook.

**Key Steps:**
1. Mount Google Drive
2. Install dependencies (InsightFace, DeepFace)
3. Read video from `/ai_emotion_project/input_videos/`
4. Run emotion detection
5. Write outputs to Google Drive

## 📁 Project Structure

```
Final lab/
├── backend/                      # Django REST API
│   ├── emotion_backend/          # Project settings
│   │   ├── settings.py           # Configuration
│   │   └── urls.py               # URL routing
│   ├── jobs/                     # Jobs app
│   │   ├── models.py             # VideoJob model
│   │   ├── serializers.py        # DRF serializers
│   │   ├── views.py              # API endpoints
│   │   ├── urls.py               # App URLs
│   │   ├── admin.py              # Django admin
│   │   └── google_drive_service.py  # Drive integration
│   ├── manage.py                 # Django CLI
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Backend docs
│
├── frontend/                     # React application
│   ├── src/
│   │   ├── components/
│   │   │   └── EmotionChart.jsx  # Chart component
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx    # Video upload
│   │   │   ├── ProcessingPage.jsx # Live monitoring
│   │   │   └── ResultsPage.jsx   # Results display
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   ├── App.jsx               # Main component
│   │   └── main.jsx              # Entry point
│   ├── package.json              # Dependencies
│   ├── vite.config.js            # Build config
│   └── README.md                 # Frontend docs
│
├── colab_template.ipynb          # Google Colab notebook
└── README.md                     # This file
```

## 🔑 Key Features

### ✅ What This System Does

- Upload videos through web interface
- Store videos in Google Drive
- Provide Colab notebook for manual GPU processing
- Monitor processing status in real-time
- Display processed videos with emotion annotations
- Show emotion distribution per detected person
- Download processed results

### ❌ What This System Does NOT Do

- Run AI inference in the backend
- Automatically trigger Colab processing
- Use Celery, Redis, or background workers
- Modify or optimize the AI/ML code

## 🎭 AI Models (Colab Only)

The emotion detection pipeline (runs **ONLY** in Google Colab):

1. **InsightFace Buffalo-S**
   - Face detection
   - Face tracking across frames
   - Person ID assignment

2. **DeepFace**
   - Emotion classification
   - 7 emotion categories: happy, sad, angry, neutral, surprise, fear, disgust

3. **OpenCV**
   - Video reading/writing
   - Frame annotation
   - Bounding box drawing

## 📊 API Endpoints

### Upload Video
```http
POST /api/jobs/upload/
Content-Type: multipart/form-data

Response: {
  "job_id": "uuid",
  "status": "PENDING",
  "colab_url": "https://colab.research.google.com/...",
  "message": "Video uploaded successfully"
}
```

### Get Status
```http
GET /api/jobs/<job_id>/status/

Response: {
  "id": "uuid",
  "status": "PROCESSING",
  "status_message": "Processing frame 45/120",
  "updated_at": "2026-01-02T10:30:00Z"
}
```

### Get Results
```http
GET /api/jobs/<job_id>/results/

Response: {
  "job_id": "uuid",
  "output_video_url": "https://drive.google.com/...",
  "emotion_data": {
    "person_1": {
      "frame_count": 120,
      "emotions": {"happy": 45, "sad": 12, ...}
    }
  }
}
```

## 🗂️ Google Drive Structure

```
/ai_emotion_project/
  /input_videos/      # Backend uploads videos here
    /<job_id>.mp4
  
  /output_videos/     # Colab writes processed videos here
    /<job_id>.mp4
  
  /output_json/       # Colab writes emotion results here
    /<job_id>.json
  
  /status/            # Colab writes live status updates here
    /<job_id>.json
```

Folders are **created automatically** on first run.

## 🔄 Complete Workflow

### Step-by-Step Process

1. **User uploads video**
   - Navigate to `http://localhost:3000`
   - Select video file (MP4, AVI, MOV)
   - Click "Upload Video"

2. **Backend processes upload**
   - Creates VideoJob record (status: PENDING)
   - Uploads video to Google Drive
   - Returns job_id and Colab URL

3. **User starts GPU processing**
   - Click "Open Colab Notebook"
   - In Colab, click "Run All"
   - Colab mounts Drive and starts processing

4. **Frontend monitors progress**
   - Auto-redirects to Processing page
   - Polls backend every 2.5 seconds
   - Displays live status from Colab

5. **Colab processing**
   - Detects faces with InsightFace
   - Classifies emotions with DeepFace
   - Annotates video frames
   - Writes status updates
   - Saves output video and JSON

6. **Results display**
   - Frontend auto-detects completion
   - Redirects to Results page
   - Shows annotated video
   - Displays emotion charts

## 🛡️ Security Considerations

- Never commit `credentials.json` or `token.json`
- Change Django `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS in production
- Implement user authentication (future enhancement)

## 🐛 Troubleshooting

### Backend Issues

**Problem:** `credentials.json not found`
- **Solution:** Download OAuth credentials from Google Cloud Console

**Problem:** `Google Drive API not enabled`
- **Solution:** Enable Drive API in Google Cloud Console

**Problem:** `CORS errors`
- **Solution:** Check `CORS_ALLOWED_ORIGINS` in Django settings

### Frontend Issues

**Problem:** `API connection failed`
- **Solution:** Ensure backend is running on `localhost:8000`

**Problem:** `Status not updating`
- **Solution:** Check Colab has written status file to Drive

### Colab Issues

**Problem:** `ModuleNotFoundError: insightface`
- **Solution:** Run installation cells in Colab notebook

**Problem:** `Drive not mounted`
- **Solution:** Authorize Google Drive access in Colab

## 📈 Future Enhancements

- [ ] User authentication and authorization
- [ ] Job history and dashboard
- [ ] Email notifications on completion
- [ ] Support for multiple video formats
- [ ] Real-time streaming (WebSocket)
- [ ] Export emotion data as CSV/Excel
- [ ] Sentiment trend analysis over time
- [ ] Multi-language support

## 📝 License

Academic project - Free to use for educational purposes.

## 👥 Contributors

- Hariharan A

## 📞 Support

For issues or questions:
1. Check README files in `backend/` and `frontend/`
2. Review Colab notebook comments
3. Inspect browser DevTools console
4. Check Django backend logs

## 🎓 Academic Context

This system demonstrates:
- Full-stack web development
- REST API design
- Cloud storage integration
- Asynchronous processing patterns
- Real-time status monitoring
- GPU-accelerated ML deployment
- Clean architecture principles

**Key Learning Points:**
- Separation of concerns (web app vs. ML inference)
- Stateless backend design
- Polling-based status updates
- Manual workflow orchestration
- Academic ML pipeline integration
