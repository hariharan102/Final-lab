# Django Backend for Emotion Detection System

## Architecture Overview

This backend serves as a **coordination layer** between the React frontend and Google Colab GPU processing. It does **NOT** run any AI/ML inference.

**Data Flow:**
```
Frontend → Django → Google Drive → Colab (GPU) → Google Drive → Django → Frontend
```

## Key Responsibilities

1. **Video Upload**: Receive videos from frontend, upload to Google Drive
2. **Status Polling**: Read status updates written by Colab
3. **Results Delivery**: Fetch processed videos and emotion JSON from Google Drive

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. Google Drive API Setup

#### A. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Emotion Detection System"
3. Enable **Google Drive API**

#### B. Create OAuth 2.0 Credentials

1. Navigate to: **APIs & Services > Credentials**
2. Click: **Create Credentials > OAuth 2.0 Client ID**
3. Application type: **Desktop app**
4. Download `credentials.json`
5. Place `credentials.json` in `backend/` directory

#### C. First-Time Authentication

```bash
python manage.py shell
>>> from jobs.google_drive_service import GoogleDriveService
>>> service = GoogleDriveService()
# Browser will open for Google authentication
# Click "Allow" to grant Drive access
# token.json will be created automatically
```

### 3. Configure Settings

Edit `emotion_backend/settings.py`:

```python
# Update your Colab notebook URL
COLAB_NOTEBOOK_URL = 'https://colab.research.google.com/drive/YOUR_ACTUAL_NOTEBOOK_ID'
```

### 4. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

## API Endpoints

### 1. Upload Video

```http
POST /api/jobs/upload/
Content-Type: multipart/form-data

{
  "video": <file>
}

Response:
{
  "job_id": "uuid",
  "status": "PENDING",
  "colab_url": "https://colab.research.google.com/...",
  "message": "Video uploaded successfully. Please open Colab to start GPU processing."
}
```

### 2. Get Job Status

```http
GET /api/jobs/<job_id>/status/

Response:
{
  "id": "uuid",
  "status": "PROCESSING",
  "status_message": "Processing frame 45/120",
  "updated_at": "2026-01-02T10:30:00Z"
}
```

**Status Values:**
- `PENDING`: Waiting for Colab processing
- `PROCESSING`: Currently running in Colab
- `DONE`: Processing complete, results available
- `FAILED`: Error occurred

### 3. Get Results

```http
GET /api/jobs/<job_id>/results/

Response:
{
  "job_id": "uuid",
  "status": "DONE",
  "output_video_url": "https://drive.google.com/...",
  "emotion_data": {
    "person_1": {
      "frame_count": 120,
      "emotions": {
        "happy": 45,
        "sad": 12,
        "angry": 3,
        "neutral": 60
      }
    }
  }
}
```

## Google Drive Folder Structure

The backend expects this structure in your Google Drive:

```
/ai_emotion_project/
  /input_videos/      ← Backend uploads videos here
    /<job_id>.mp4
  
  /output_videos/     ← Colab writes processed videos here
    /<job_id>.mp4
  
  /output_json/       ← Colab writes emotion results here
    /<job_id>.json
  
  /status/            ← Colab writes live status updates here
    /<job_id>.json
```

**Folders are created automatically** on first run.

## Database Schema

### VideoJob Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key, used for file naming |
| `status` | CharField | PENDING, PROCESSING, DONE, FAILED |
| `status_message` | TextField | Detailed status from Colab |
| `input_video_path` | CharField | Google Drive path to input video |
| `output_video_path` | CharField | Google Drive path to output video |
| `output_json_path` | CharField | Google Drive path to emotion JSON |
| `colab_notebook_url` | CharField | Link to Colab notebook |
| `created_at` | DateTime | Job creation timestamp |
| `updated_at` | DateTime | Last status update |

## Important Notes

### What This Backend Does NOT Do

❌ Run AI inference  
❌ Detect faces or emotions  
❌ Process videos with GPU  
❌ Automatically trigger Colab  

### What This Backend DOES Do

✅ Upload videos to Google Drive  
✅ Read status updates from Colab  
✅ Fetch results from Google Drive  
✅ Provide REST API for frontend  

## Development Tips

### Testing Without Google Drive

To test locally without Google Drive API setup, the code includes a `MockGoogleDriveService` that stores files locally in `media/mock_drive/`.

### Admin Interface

Access Django admin at: `http://localhost:8000/admin`

View and manage all VideoJob records.

### Debugging

Check logs for Google Drive operations:
```python
# In views.py or google_drive_service.py
import logging
logger = logging.getLogger(__name__)
logger.info(f"Processing job {job_id}")
```

## Security Considerations

1. **Never commit `credentials.json` or `token.json`** (already in .gitignore)
2. Change `SECRET_KEY` in production
3. Set `DEBUG = False` in production
4. Configure proper `ALLOWED_HOSTS`
5. Use environment variables for sensitive settings

## Next Steps

1. ✅ Backend setup complete
2. ⏭️ Set up React frontend
3. ⏭️ Configure Google Colab notebook
4. ⏭️ Test end-to-end workflow
