# React Frontend for Emotion Detection System

## Overview

This React application provides a user-friendly interface for uploading videos, monitoring GPU processing in Google Colab, and viewing emotion detection results.

## Architecture

```
User → Upload Video → Backend → Google Drive → Colab (GPU)
                                      ↓
User ← Results Page ← Backend ← Google Drive ← Colab
```

## Features

### 1. Upload Page
- Video file selection and validation
- Upload to backend (which saves to Google Drive)
- Receive Google Colab notebook link

### 2. Processing Page (Live Monitoring)
- **Live status polling** (every 2.5 seconds)
- Real-time updates from Colab via Google Drive
- "Open Colab" button for manual GPU processing
- Auto-redirect to results when complete

### 3. Results Page
- Processed video with emotion annotations
- Emotion distribution charts per person
- Download processed video
- Emotion statistics and metadata

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API Endpoint

The app is pre-configured to connect to Django backend at `http://localhost:8000`.

If your backend runs on a different port, edit [vite.config.js](vite.config.js):

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:YOUR_PORT',  // Change this
      changeOrigin: true,
    },
  },
}
```

### 3. Run Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── EmotionChart.jsx        # Emotion visualization component
│   ├── pages/
│   │   ├── UploadPage.jsx          # Video upload interface
│   │   ├── ProcessingPage.jsx      # Live status monitoring
│   │   └── ResultsPage.jsx         # Results display
│   ├── services/
│   │   └── api.js                  # Backend API calls (Axios)
│   ├── App.jsx                     # Main app component & routing
│   ├── App.css                     # Global styles
│   └── main.jsx                    # App entry point
├── package.json                    # Dependencies
└── vite.config.js                  # Vite configuration
```

## API Integration

### API Service (`src/services/api.js`)

All backend communication is centralized in the API service:

```javascript
import { uploadVideo, getJobStatus, getJobResults } from './services/api';

// Upload video
const response = await uploadVideo(videoFile);
// Returns: { job_id, status, colab_url }

// Poll status
const status = await getJobStatus(jobId);
// Returns: { status, status_message, updated_at }

// Get results
const results = await getJobResults(jobId);
// Returns: { output_video_url, emotion_data }
```

## Component Details

### UploadPage

**Workflow:**
1. User selects video file
2. Client-side validation (size, format)
3. Upload to backend via `POST /api/jobs/upload/`
4. Navigate to ProcessingPage with job_id

**Key Features:**
- File size validation (max 500MB)
- Supported formats: MP4, AVI, MOV, MKV
- Upload progress indicator

### ProcessingPage

**Workflow:**
1. Poll backend every 2.5 seconds
2. Backend reads status from Google Drive
3. Display current status and message
4. Auto-navigate to ResultsPage when status = DONE

**Status Flow:**
- `PENDING` → Show "Open Colab" button
- `PROCESSING` → Show spinner and live updates
- `DONE` → Redirect to results
- `FAILED` → Show error and retry option

**Implementation:**
```javascript
useEffect(() => {
  const pollInterval = setInterval(async () => {
    const response = await getJobStatus(jobId);
    setStatus(response.status);
    
    if (response.status === 'DONE') {
      navigate(`/results/${jobId}`);
    }
  }, 2500);
  
  return () => clearInterval(pollInterval);
}, [jobId]);
```

### ResultsPage

**Features:**
- Embedded video player for processed video
- Emotion distribution per person (bar charts)
- Downloadable processed video
- Processing metadata (timestamps, status)

**Data Structure:**
```javascript
{
  output_video_url: "https://drive.google.com/...",
  emotion_data: {
    person_1: {
      frame_count: 120,
      emotions: {
        happy: 45,
        sad: 12,
        neutral: 63
      }
    }
  }
}
```

## Styling

The app uses custom CSS with:
- Gradient backgrounds
- Card-based layout
- Responsive design
- Smooth animations
- Status-based color coding

Color scheme:
- Primary: Purple gradient (`#667eea` to `#764ba2`)
- Success: Green (`#4CAF50`)
- Warning: Orange (`#FF9800`)
- Error: Red (`#F44336`)

## Dependencies

### Core
- **React 18** - UI library
- **React Router v6** - Client-side routing
- **Axios** - HTTP client for API calls

### Visualization
- **Recharts** - Emotion distribution charts

### Build Tools
- **Vite** - Fast build tool and dev server

## Build for Production

```bash
npm run build
```

Output will be in `dist/` folder.

## Important Notes

### What This Frontend Does

✅ Upload videos to backend  
✅ Poll for live status updates  
✅ Display processed results  
✅ Provide Colab notebook access  

### What This Frontend Does NOT Do

❌ Run AI inference  
❌ Process videos locally  
❌ Automatically trigger Colab  
❌ Access Google Drive directly  

## Testing

### Manual Testing Steps

1. **Upload Test:**
   - Select video file
   - Verify upload success
   - Check job_id received

2. **Processing Test:**
   - Verify Colab button works
   - Check status polling (DevTools Network tab)
   - Confirm auto-redirect on completion

3. **Results Test:**
   - Verify video playback
   - Check emotion data display
   - Test video download

## Troubleshooting

### CORS Errors

If you see CORS errors in console:
1. Ensure Django backend has `django-cors-headers` installed
2. Check `CORS_ALLOWED_ORIGINS` in Django settings
3. Backend should include `http://localhost:3000`

### API Connection Issues

1. Verify backend is running: `http://localhost:8000`
2. Check Vite proxy configuration
3. Inspect Network tab in DevTools

### Status Not Updating

1. Check backend logs for Google Drive API errors
2. Verify Colab has written status file
3. Confirm polling interval is active (check Network tab)

## Next Steps

1. ✅ Frontend setup complete
2. ⏭️ Start Django backend
3. ⏭️ Test video upload flow
4. ⏭️ Configure Google Colab notebook
5. ⏭️ Test end-to-end workflow
