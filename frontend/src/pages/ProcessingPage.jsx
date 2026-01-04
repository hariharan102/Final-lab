/**
 * Processing Page Component
 * 
 * Shows live processing status by polling the appropriate backend.
 * 
 * DUAL BACKEND SUPPORT:
 * - Colab mode: Polls Django backend (port 8000), shows Colab link
 * - Local mode: Polls FastAPI backend (port 8001), fully automatic
 * 
 * Status Flow:
 * PENDING → (Colab: User runs notebook / Local: Auto-starts) → PROCESSING → DONE
 * 
 * When status becomes DONE, automatically navigate to Results page.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { getJobStatus, terminateJob } from '../services/api';
import { useExecutionMode } from '../context/ExecutionModeContext';
import './ProcessingPage.css';

function ProcessingPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get execution mode from context or location state
  const { mode: contextMode, isLocal, modeInfo } = useExecutionMode();
  const executionMode = location.state?.executionMode || contextMode;
  const isLocalMode = executionMode === 'local';
  const colabUrl = location.state?.colabUrl;

  const [status, setStatus] = useState('PENDING');
  const [message, setMessage] = useState('Waiting for processing to start...');
  const [progress, setProgress] = useState(0);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState('');
  const [isTerminating, setIsTerminating] = useState(false);

  useEffect(() => {
    // Poll status every 1 second for real-time updates
    const pollInterval = setInterval(async () => {
      try {
        const response = await getJobStatus(jobId, executionMode);
        
        setStatus(response.status);
        setMessage(response.status_message || getDefaultMessage(response.status));
        setProgress(response.progress || 0);
        setLastUpdated(response.updated_at ? new Date(response.updated_at) : new Date());
        setError('');

        // Auto-navigate to results when done
        if (response.status === 'DONE') {
          clearInterval(pollInterval);
          setTimeout(() => {
            navigate(`/results/${jobId}`, {
              state: { executionMode }
            });
          }, 1500);
        }

        // Stop polling if failed or cancelled
        if (response.status === 'FAILED' || response.status === 'CANCELLED') {
          clearInterval(pollInterval);
        }

      } catch (err) {
        setError('Failed to fetch status. Will retry...');
        console.error('Status polling error:', err);
      }
    }, 1000);

    // Initial fetch
    getJobStatus(jobId, executionMode)
      .then(response => {
        setStatus(response.status);
        setMessage(response.status_message || getDefaultMessage(response.status));
        setProgress(response.progress || 0);
        setLastUpdated(response.updated_at ? new Date(response.updated_at) : new Date());
      })
      .catch(err => {
        setError('Failed to load job status');
        console.error('Initial status fetch error:', err);
      });

    // Cleanup interval on unmount
    return () => clearInterval(pollInterval);
  }, [jobId, navigate, executionMode]);

  const getDefaultMessage = (currentStatus) => {
    if (isLocalMode) {
      const messages = {
        'PENDING': 'Video uploaded. Starting automatic processing...',
        'PROCESSING': 'Processing video locally with CPU...',
        'DONE': 'Processing complete! Redirecting to results...',
        'FAILED': 'Processing failed. Check console for errors.',
        'CANCELLED': 'Job cancelled by user.',
      };
      return messages[currentStatus] || 'Unknown status';
    } else {
      const messages = {
        'PENDING': 'Video uploaded to Google Drive. Please run the Colab notebook to start processing.',
        'PROCESSING': 'Processing video with GPU in Google Colab...',
        'DONE': 'Processing complete! Redirecting to results...',
        'FAILED': 'Processing failed. Please check Colab notebook for errors.',
        'CANCELLED': 'Job cancelled by user.',
      };
      return messages[currentStatus] || 'Unknown status';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'PENDING':
        return '⏳';
      case 'PROCESSING':
        return '⚙️';
      case 'DONE':
        return '✅';
      case 'FAILED':
        return '❌';
      case 'CANCELLED':
        return '🛑';
      default:
        return '❓';
    }
  };

  const openColabNotebook = () => {
    if (colabUrl) {
      window.open(colabUrl, '_blank');
    }
  };

  const handleTerminateJob = async () => {
    if (!window.confirm('Are you sure you want to terminate this job?')) {
      return;
    }

    setIsTerminating(true);
    try {
      await terminateJob(jobId, executionMode);
      setStatus('CANCELLED');
      setMessage('Job cancelled by user');
      setError('');
    } catch (err) {
      setError('Failed to terminate job: ' + (err.response?.data?.message || err.message));
      console.error('Terminate job error:', err);
    } finally {
      setIsTerminating(false);
    }
  };

  return (
    <div className="processing-page">
      <div className="processing-card">
        <h2>Processing Status</h2>
        <p className="job-id">Job ID: {jobId}</p>
        
        {/* Execution Mode Badge */}
        <div className="mode-indicator">
          <span className={`mode-badge mode-${executionMode}`}>
            {isLocalMode ? '💻 Local CPU Mode' : '☁️ Colab GPU Mode'}
          </span>
        </div>

        <div className={`status-indicator status-${status.toLowerCase()}`}>
          <span className="status-icon">{getStatusIcon()}</span>
          <span className="status-text">{status}</span>
        </div>

        <div className="status-message">
          {message}
        </div>

        {/* Progress Bar (more useful in local mode) */}
        {status === 'PROCESSING' && (
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <span className="progress-text">{progress}%</span>
          </div>
        )}

        {lastUpdated && (
          <p className="last-updated">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </p>
        )}

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {/* Colab-specific: Show button to open Colab notebook */}
        {!isLocalMode && status === 'PENDING' && (
          <div className="action-section">
            <p className="instruction">
              👉 To start GPU processing, open the Colab notebook and click "Run All":
            </p>
            <button onClick={openColabNotebook} className="colab-button">
              🚀 Open Colab Notebook (GPU Processing)
            </button>
          </div>
        )}

        {/* Local-specific: Show auto-processing message */}
        {isLocalMode && status === 'PENDING' && (
          <div className="action-section local-action">
            <div className="spinner"></div>
            <p className="instruction">
              🔄 Processing will start automatically...
            </p>
            <p className="local-note">
              No manual steps required. The pipeline runs on your local CPU.
            </p>
          </div>
        )}

        {status === 'PROCESSING' && (
          <div className="processing-animation">
            <div className="spinner"></div>
            <p>Analyzing emotions with InsightFace + DeepFace...</p>
            <p className="processing-note">
              {isLocalMode 
                ? '(Running on local CPU - this may take a while)'
                : '(Running on Colab T4 GPU)'
              }
            </p>
            <button 
              onClick={handleTerminateJob} 
              className="terminate-button"
              disabled={isTerminating}
            >
              {isTerminating ? '⏳ Terminating...' : '🛑 Terminate Job'}
            </button>
          </div>
        )}

        {status === 'DONE' && (
          <div className="success-section">
            <p className="success-message">
              🎉 Processing complete! Redirecting to results...
            </p>
          </div>
        )}

        {(status === 'FAILED' || status === 'CANCELLED') && (
          <div className="error-section">
            {status === 'FAILED' && (
              <>
                <p>Processing failed. Please check:</p>
                <ul>
                  {isLocalMode ? (
                    <>
                      <li>Local backend console for error messages</li>
                      <li>Python dependencies installed correctly</li>
                      <li>Input video format and quality</li>
                    </>
                  ) : (
                    <>
                      <li>Colab notebook for error messages</li>
                      <li>Google Drive permissions</li>
                      <li>Input video format and quality</li>
                    </>
                  )}
                </ul>
              </>
            )}
            {status === 'CANCELLED' && (
              <p>The job was cancelled and will not be processed.</p>
            )}
            <button onClick={() => navigate('/')} className="retry-button">
              Upload New Video
            </button>
          </div>
        )}

        <div className={`info-box ${isLocalMode ? 'local-info' : ''}`}>
          <h3>Live Monitoring:</h3>
          <p>
            {isLocalMode 
              ? 'This page polls the local FastAPI backend every second. Processing runs automatically on your CPU.'
              : 'This page polls the Django backend every second. The backend reads status updates from Google Drive that are continuously written by your Colab notebook during processing.'
            }
          </p>
        </div>
      </div>
    </div>
  );
}

export default ProcessingPage;