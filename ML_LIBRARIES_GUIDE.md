# ML Libraries Not Available - User Guide

## What You're Seeing

When you click "Upload & Process Locally" in the web application, you see:
- Purple screen (no content)
- Console error: 503 Service Unavailable
- Error message about ML libraries not being installed

## Why This Happens

The Local Backend (port 8001) is running successfully, but the **ML libraries** required for emotion detection are not compatible with Python 3.14:

- ❌ **InsightFace** - Face detection (not available for Python 3.14)
- ❌ **DeepFace** - Emotion recognition (not available for Python 3.14)
- ❌ **ONNX Runtime** - ML inference engine (not available for Python 3.14)

## What's Fixed

✅ **Frontend now shows a helpful error message** instead of a purple screen
✅ **Error message includes:**
- Clear explanation of the problem
- Solution instructions
- Alternative option (use Google Colab mode)

After refreshing the page, you'll see a yellow warning box with:
```
⚠️ ML Libraries Not Available

Video processing requires ML libraries that are not installed 
or incompatible with Python 3.14.

Solution: Install Python 3.9-3.12 and run: 
pip install insightface deepface onnxruntime

Alternative: Switch to "Google Colab (GPU)" mode above to use 
GPU processing instead.
```

## Solutions

### Option 1: Use Google Colab Mode (Easiest - No Setup Required)

1. **Switch Mode**: Click "Google Colab (GPU)" button at the top of the upload page
2. **Upload Video**: Select and upload your video
3. **Open Colab**: Click the provided Colab notebook link
4. **Run Processing**: Click "Run All" in Colab
5. **View Results**: Return to the web app to see results

**Advantages:**
- ✅ No Python version changes needed
- ✅ Uses GPU (faster processing)
- ✅ Works with your current Python 3.14 setup

### Option 2: Install Python 3.11 for Local Backend (Full Local Processing)

If you want the Local Machine mode to work with emotion detection:

#### Step 1: Install Python 3.11

**Using Homebrew (macOS):**
```bash
brew install python@3.11
```

**Using pyenv:**
```bash
pyenv install 3.11.7
```

**Or download from:** https://www.python.org/downloads/

#### Step 2: Recreate Local Backend Virtual Environment

```bash
cd /Users/shyamali/Documents/CIDM/Final-lab/local_backend

# Remove old venv
rm -rf venv

# Create new venv with Python 3.11
python3.11 -m venv venv

# Activate it
source venv/bin/activate

# Verify Python version
python --version  # Should show Python 3.11.x

# Install all dependencies
pip install -r requirements.txt

# Install ML libraries
pip install insightface deepface onnxruntime
```

#### Step 3: Restart Servers

```bash
cd /Users/shyamali/Documents/CIDM/Final-lab
./run.sh
```

#### Step 4: Verify ML Libraries

```bash
curl http://localhost:8001/local/frame-api-status
```

Should return:
```json
{
  "status": "ready",
  "ml_libraries_available": true,
  "face_analyzer_loaded": false,
  "face_tracker_active": false
}
```

### Option 3: Keep Current Setup (Limited Functionality)

You can continue using Python 3.14 with these limitations:

**What Works:**
- ✅ Web application UI
- ✅ Django backend (Google Colab integration)
- ✅ Video upload interface
- ✅ Google Colab mode (full emotion detection)

**What Doesn't Work:**
- ❌ Local Machine mode emotion detection
- ❌ Browser extension emotion detection
- ❌ Frame-by-frame API

## Current System Status

After running `./run.sh`:

```
✅ Django Backend:       http://localhost:8000  (Fully functional)
✅ Local Backend:        http://localhost:8001  (Running, ML unavailable)
✅ React Frontend:       http://localhost:3000  (Fully functional)
```

## Testing Your Setup

### 1. Check All Servers Running
```bash
curl http://localhost:8000/health  # Django
curl http://localhost:8001/health  # Local Backend
curl http://localhost:3000         # Frontend
```

### 2. Check ML Status
```bash
curl http://localhost:8001/local/frame-api-status
```

**With Python 3.14 (current):**
```json
{
  "status": "unavailable",
  "ml_libraries_available": false
}
```

**With Python 3.11 (after setup):**
```json
{
  "status": "ready",
  "ml_libraries_available": true
}
```

### 3. Test Web Application

1. Open: http://localhost:3000
2. Try **Google Colab mode** first (should work)
3. Then try **Local Machine mode** (will show error if ML unavailable)

## Recommended Approach

**For immediate use:**
1. Keep your current Python 3.14 setup
2. Use **Google Colab (GPU)** mode for video processing
3. Everything works perfectly this way

**For full local processing:**
1. Install Python 3.11 specifically for `local_backend` directory
2. Follow Option 2 steps above
3. Both modes will work

## Browser Extension

The browser extension also requires ML libraries. If you want to use it:

1. Follow **Option 2** to install Python 3.11 and ML libraries
2. Restart the Local Backend
3. Install the extension from `emotion/` folder
4. Extension will work with real-time emotion detection

Without ML libraries, the extension will show the same error.

## Summary

🎯 **Quick Fix**: Use Google Colab mode (switch the button at the top)

🔧 **Full Fix**: Install Python 3.11 for the local_backend directory

📚 **More Info**: See `PYTHON_314_COMPATIBILITY.md` for technical details

## Files Modified

To improve the user experience:

1. **`frontend/src/pages/UploadPage.jsx`** - Better error handling
2. **`frontend/src/pages/UploadPage.css`** - Error message styling
3. **`local_backend/frame_api.py`** - Graceful ML unavailability handling
4. **`local_backend/routes.py`** - Helpful error messages

Now when you try to use Local Machine mode without ML libraries, you'll see a clear, helpful error message instead of a purple screen.
