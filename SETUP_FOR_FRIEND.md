# 🚀 Complete Setup Guide - Emotion Detection System

## 📦 What You'll Get

A full-stack web application that:
- ✅ Uploads meeting videos
- ✅ Uses GPU-powered AI (Google Colab) to detect emotions in faces
- ✅ Shows live progress
- ✅ Displays emotion statistics and annotated videos

---

## 📋 Prerequisites - Install These First

### 1. **Python 3.8+**
   - Download from: https://www.python.org/downloads/
   - **IMPORTANT**: During installation, check ✅ "Add Python to PATH"

### 2. **Node.js 16+**
   - Download from: https://nodejs.org/
   - **IMPORTANT**: During installation, check ✅ "Add to PATH"

### 3. **Git (Optional but recommended)**
   - Download from: https://git-scm.com/download/win

### 4. **Google Account**
   - Gmail account (free)
   - Will use for Google Drive API and Colab

---

## 🔑 Step 1: Google Cloud Setup (15 minutes)

### 1.1 Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click **Create Project**
3. Project name: `Emotion Detection System`
4. Click **Create**
5. Wait for project to be created (1-2 minutes)

### 1.2 Enable Google Drive API

1. In Google Cloud Console, search for **"Drive API"**
2. Click on **Google Drive API**
3. Click **ENABLE**
4. Wait 1-2 minutes for API to be enabled

### 1.3 Create OAuth 2.0 Credentials

1. Go to: **APIs & Services > Credentials** (left sidebar)
2. Click **Create Credentials > OAuth client ID**
3. If you see a warning about "OAuth consent screen", click **Configure Consent Screen**:
   - Choose: **External**
   - Click **Create**
   - Fill in:
     - App name: `Emotion Detection`
     - User support email: Your Gmail
     - Developer email: Your Gmail
   - Click **Save & Continue**
   - Skip scopes (click **Save & Continue**)
   - Skip test users (click **Save & Continue**)
   - Click **Back to Dashboard**

4. Go back to **Credentials > Create Credentials > OAuth client ID**
5. Application type: Select **Desktop app**
6. Name: `Emotion Detection Client`
7. Click **Create**
8. Click **Download JSON** button (⬇️ icon)
9. Save as **`credentials.json`**

### 1.4 Place Credentials File

1. Extract the project zip
2. Place `credentials.json` in the `backend/` folder
   ```
   your_project/
   └── backend/
       └── credentials.json  ← Put it here
   ```

---

## 🛠️ Step 2: Backend Setup (5 minutes)

Open **PowerShell** or **Command Prompt** in the project folder:

```powershell
# Navigate to project folder
cd C:\path\to\project

# Run setup script (Windows)
.\setup.bat
```

**What this does:**
- ✅ Creates Python virtual environment
- ✅ Installs all Python packages
- ✅ Sets up database
- ✅ Installs Node.js packages

**If setup.bat doesn't work, do it manually:**

```powershell
# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

# Frontend setup (in new PowerShell window)
cd frontend
npm install
```

---

## 🔐 Step 3: First-Time Google Drive Authentication (2 minutes)

This only needs to be done ONCE:

```powershell
# Make sure you're in backend directory with venv activated
cd backend
venv\Scripts\activate

# Enter Django shell
python manage.py shell

# In the shell, type:
from jobs.google_drive_service import GoogleDriveService
service = GoogleDriveService()
exit()
```

**What happens:**
1. Browser opens automatically
2. Click **Allow** to grant Google Drive access
3. Browser shows "Authorization successful"
4. Come back to PowerShell - you'll see `token.json` created in `backend/`

---

## 📝 Step 4: Update Colab Notebook URL (2 minutes)

The system needs to know where your Colab notebook is:

1. Open: `backend/emotion_backend/settings.py`
2. Find line with: `COLAB_NOTEBOOK_URL = '...'`
3. **Keep it as is for now** (you'll update after uploading to Colab)

---

## ☁️ Step 5: Upload Colab Notebook (3 minutes)

This is the GPU processing notebook:

1. Go to: https://colab.research.google.com/
2. Click **File > Open Notebook**
3. Click **Upload** tab
4. Select: `colab_template.ipynb` from your project
5. Google Colab opens it
6. **Don't run it yet!** Just upload and save

### Get Colab Notebook URL

1. In Google Colab, look at the URL bar
2. Copy the notebook ID from the URL:
   ```
   https://colab.research.google.com/drive/YOUR_NOTEBOOK_ID/edit
                                      ↑ Copy this part ↑
   ```
3. Update `backend/emotion_backend/settings.py`:
   ```python
   COLAB_NOTEBOOK_URL = 'https://colab.research.google.com/drive/YOUR_NOTEBOOK_ID/edit'
   ```

---

## ▶️ Step 6: Start the Application

### Terminal 1 - Start Backend

```powershell
cd backend
venv\Scripts\activate
python manage.py runserver
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Terminal 2 - Start Frontend

```powershell
cd frontend
npm run dev
```

**Expected output:**
```
  Local:   http://localhost:3000/
```

### 3. Open in Browser

- Go to: http://localhost:3000/
- You should see the upload page ✅

---

## 🎥 Step 7: Upload and Process a Video

### 7.1 Upload Video

1. On Upload Page, select a video file (MP4 recommended)
2. Click **Upload**
3. You'll see:
   - Job ID (copy this)
   - Link to Colab notebook

### 7.2 Process in Colab

1. Click the **Colab link** from step 7.1
2. Google Colab opens with your notebook
3. At the top, find the cell with `JOB_ID = "..."`
4. Replace with your Job ID from 7.1
5. Click **Runtime > Run All** (or press Ctrl+F9)
6. Wait for processing (5-10 minutes depending on video length)

### 7.3 Monitor Progress

1. Go back to http://localhost:3000/
2. You should see "Processing" page with live status
3. Status updates every 2-3 seconds from Colab

### 7.4 View Results

1. When Colab finishes, results appear automatically
2. Download processed video and view emotion statistics

---

## 🖥️ Alternative: Local Processing (No GPU needed)

If you don't want to use Colab, use the **Local Backend**:

```powershell
cd local_backend
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
```

Then on the frontend, select **"Local Mode"** instead of Colab Mode.

**Trade-off:** Slower (CPU only) but no Google Drive/Colab needed.

---

## 🆘 Troubleshooting

### "Python is not installed"
- Install Python from https://www.python.org/
- Check "Add Python to PATH" during installation
- Restart PowerShell after installing

### "Node.js is not installed"
- Install Node.js from https://nodejs.org/
- Check "Add to PATH" during installation
- Restart PowerShell after installing

### "credentials.json not found"
- Make sure you downloaded it from Google Cloud Console
- Place it in `backend/` folder
- Filename must be exactly `credentials.json`

### "Browser doesn't open for Google authentication"
- Run `python manage.py shell` and try again
- If browser still doesn't open, manually visit the URL shown in terminal

### Backend shows "Permission denied" errors
- Make sure `token.json` was created in `backend/`
- If not, redo Step 3 (authentication)
- Delete `token.json` and re-authenticate if issues persist

### "Cannot connect to http://localhost:3000"
- Make sure frontend is running (`npm run dev`)
- Check that backend is running (`python manage.py runserver`)
- Try refreshing the page

### Colab notebook says "Job not found"
- Make sure you updated the `JOB_ID` variable in Colab
- Job ID must match exactly (copy-paste recommended)

### Video processing hangs or shows "Processing..." forever
- Check Colab notebook for errors (Runtime > Show all logs)
- Make sure video file is not too large (try < 5 minutes first)
- Restart Colab and try again

---

## 📊 Project Structure

```
your_project/
├── backend/              ← Django backend (port 8000)
│   ├── credentials.json  ← Your Google credentials
│   ├── token.json        ← Auto-generated auth token
│   └── jobs/             ← API endpoints
│
├── frontend/             ← React app (port 3000)
│   └── src/
│       ├── pages/        ← Upload, Processing, Results pages
│       └── services/     ← API calls to backend
│
├── local_backend/        ← Alternative CPU backend (port 8001)
│   └── pipeline/         ← Face detection + emotion detection
│
└── colab_template.ipynb  ← GPU processing notebook
```

---

## 🔄 Quick Reference - Running the System

**Every time you want to use the system:**

```powershell
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm run dev

# Then open: http://localhost:3000/
```

---

## 📚 Architecture Overview

```
Your Computer:
  ┌─────────────────────────────────────────────────────┐
  │  Browser (http://localhost:3000)                    │
  │  React Frontend - Upload videos, view results       │
  └──────────────┬──────────────────────────────────────┘
                 │
                 ├─→ Backend (http://localhost:8000)
                 │   Django - Manages uploads & status
                 │
                 ├─→ Google Drive (Cloud Storage)
                 │   Videos uploaded here
                 │
                 └─→ Google Colab (GPU Processing)
                     ML models detect emotions
                     Writes results back to Drive
```

---

## 🎓 What Each Component Does

| Component | Purpose | Requires |
|-----------|---------|----------|
| **React Frontend** | User interface, upload, view results | Browser only |
| **Django Backend** | Coordinate uploads/results, API | Python, Google credentials |
| **Google Drive** | Cloud storage for videos | Google account |
| **Google Colab** | GPU processing, emotion detection | Manual run button click |
| **Local Backend** | Alternative CPU-only processing | Python only |

---

## ✅ Checklist Before First Run

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Google Cloud Project created
- [ ] Google Drive API enabled
- [ ] OAuth credentials downloaded (`credentials.json`)
- [ ] `credentials.json` placed in `backend/`
- [ ] `setup.bat` run successfully (or manual setup done)
- [ ] Google authentication completed (token.json created)
- [ ] Colab notebook URL updated in settings.py
- [ ] Both backend and frontend started
- [ ] Can access http://localhost:3000/

---

## 🚀 You're Ready!

Once all steps are complete, you can:

1. Upload videos from the web interface
2. Process them in Colab with GPU
3. View emotion statistics instantly
4. Download annotated videos

**Enjoy!** 🎉

---

## 📞 Need Help?

1. Check Troubleshooting section above
2. Look at detailed READMEs in each folder:
   - `backend/README.md` - Backend details
   - `frontend/README.md` - Frontend details
   - `local_backend/README.md` - Local processing
3. Check logs in browser console (F12)
4. Check Django server output

