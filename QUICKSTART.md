# Quick Start Guide

## Automated Setup (Windows)

Run the setup script:

```bash
setup.bat
```

This will:
- Create Python virtual environment
- Install all Python dependencies
- Run Django migrations
- Install Node.js dependencies

## Manual Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Google Drive API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` to `backend/`

## First Run

1. Start backend: `python manage.py runserver`
2. Start frontend: `npm run dev`
3. Open browser: `http://localhost:3000`
4. Upload a video
5. Copy job_id from response
6. Open `colab_template.ipynb` in Google Colab
7. Update `JOB_ID` variable
8. Click "Run All" in Colab
9. Monitor progress in web app

## Troubleshooting

See main [README.md](README.md) for detailed troubleshooting steps.
