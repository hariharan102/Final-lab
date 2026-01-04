/**
 * Upload Page Component
 * 
 * Allows users to:
 * 1. Select execution mode (Colab GPU or Local CPU)
 * 2. Select and upload a video file
 * 3. Submit to appropriate backend based on mode
 * 4. Navigate to Processing page
 * 
 * DUAL BACKEND SUPPORT:
 * - Colab mode: Uploads to Django backend (port 8000), requires manual Colab run
 * - Local mode: Uploads to FastAPI backend (port 8001), automatic processing
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadVideo } from '../services/api';
import { useExecutionMode, EXECUTION_MODES } from '../context/ExecutionModeContext';
import ExecutionModeSelector from '../components/ExecutionModeSelector';
import './UploadPage.css';

function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  
  // Get execution mode from context
  const { mode, isLocal, isColab, modeInfo } = useExecutionMode();

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setError('');
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a video file');
      return;
    }

    console.log('Starting upload...', {
      fileName: selectedFile.name,
      fileSize: selectedFile.size,
      fileType: selectedFile.type,
      executionMode: mode
    });

    setUploading(true);
    setError('');

    try {
      // Upload video to appropriate backend based on execution mode
      console.log(`Calling uploadVideo API (mode: ${mode})...`);
      const response = await uploadVideo(selectedFile, mode);
      console.log('Upload successful:', response);

      // Navigate to processing page with job ID and mode info
      navigate(`/processing/${response.job_id}`, {
        state: { 
          colabUrl: response.colab_url,
          executionMode: mode
        }
      });

    } catch (err) {
      console.error('Upload error:', err);
      console.error('Error response:', err.response);
      
      // Extract error message from various possible formats
      let errorMessage = 'Upload failed. Please try again.';
      if (err.response?.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.error) {
          if (typeof err.response.data.error === 'string') {
            errorMessage = err.response.data.error;
          } else {
            errorMessage = JSON.stringify(err.response.data.error);
          }
        } else if (err.response.data.details || err.response.data.detail) {
          errorMessage = err.response.data.details || err.response.data.detail;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      // Add hint about backend availability
      if (err.code === 'ERR_NETWORK' || err.message.includes('Network Error')) {
        const port = isLocal ? '8001' : '8000';
        const backend = isLocal ? 'Local FastAPI' : 'Django';
        errorMessage = `Cannot connect to ${backend} backend on port ${port}. Make sure the backend is running.`;
      }
      
      setError(errorMessage);
      setUploading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-card">
        <h2>Upload Video for Emotion Detection</h2>
        <p className="description">
          Select a video file to analyze emotions in meetings.
          Choose your preferred processing mode below.
        </p>

        {/* Execution Mode Selector */}
        <ExecutionModeSelector showDetails={true} />

        <div className="upload-section">
          <input
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            disabled={uploading}
            id="video-input"
            className="file-input"
          />
          <label htmlFor="video-input" className="file-label">
            {selectedFile ? selectedFile.name : 'Choose Video File'}
          </label>

          {selectedFile && (
            <div className="file-info">
              <p>Size: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
              <p>Type: {selectedFile.type}</p>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
          className={`upload-button ${isLocal ? 'local-mode' : 'colab-mode'}`}
        >
          {uploading 
            ? (isLocal ? 'Uploading & Starting Processing...' : 'Uploading to Google Drive...')
            : (isLocal ? '🚀 Upload & Process Locally' : '☁️ Upload to Google Drive')
          }
        </button>

        {/* Info box changes based on execution mode */}
        <div className={`info-box ${isLocal ? 'local-info' : 'colab-info'}`}>
          <h3>How it works ({modeInfo.name}):</h3>
          {isColab ? (
            <ol>
              <li>Upload your video → Saved to Google Drive</li>
              <li>Open provided Colab link</li>
              <li>Click "Run All" in Colab (GPU processing starts)</li>
              <li>Monitor live progress in this app</li>
              <li>View results when processing completes</li>
            </ol>
          ) : (
            <ol>
              <li>Upload your video → Saved locally</li>
              <li>Processing starts automatically (no manual steps!)</li>
              <li>Monitor live progress in this app</li>
              <li>View results when processing completes</li>
            </ol>
          )}
          
          {isLocal && (
            <p className="local-note">
              💡 <strong>Note:</strong> Local processing uses CPU and may be slower than GPU.
              No Google account or Colab setup required.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default UploadPage;
