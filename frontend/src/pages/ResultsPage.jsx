/**
 * Results Page Component - Simplified
 * 
 * Displays:
 * 1. Download buttons for video and JSON
 * 2. Emotion distribution per person detected
 * 3. Summary statistics
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { getJobResults, getVideoStreamUrl } from '../services/api';
import { useExecutionMode } from '../context/ExecutionModeContext';
import EmotionChart from '../components/EmotionChart';
import SummaryChart from '../components/SummaryChart';
import './ResultsPage.css';

// API base URLs
const COLAB_API_URL = 'http://localhost:8000/api';
const LOCAL_API_URL = 'http://localhost:8001';

function ResultsPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  const { mode: contextMode } = useExecutionMode();
  const executionMode = location.state?.executionMode || contextMode;
  const isLocalMode = executionMode === 'local';

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await getJobResults(jobId, executionMode);
        setResults(response);
        setLoading(false);
      } catch (err) {
        if (err.response?.status === 400) {
          setError('Results not available yet. Processing may still be in progress.');
          setTimeout(() => {
            navigate(`/processing/${jobId}`, { state: { executionMode } });
          }, 3000);
        } else {
          setError(err.response?.data?.error || err.response?.data?.detail || 'Failed to load results');
        }
        setLoading(false);
      }
    };
    fetchResults();
  }, [jobId, navigate, executionMode]);

  const handleDownloadVideo = async () => {
    const url = getVideoStreamUrl(jobId, executionMode);
    
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `emotion_detection_${jobId}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error('Download failed:', err);
      // Fallback: open in new tab
      window.open(url, '_blank');
    }
  };

  const handleDownloadJSON = async () => {
    const baseUrl = isLocalMode ? LOCAL_API_URL : COLAB_API_URL;
    const endpoint = isLocalMode 
      ? `/local/jobs/${jobId}/json`
      : `/jobs/${jobId}/json/`;
    const url = `${baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `emotion_data_${jobId}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error('Download failed:', err);
      window.open(url, '_blank');
    }
  };

  const getEmotionColor = (emotion) => {
    const colors = {
      happy: '#4CAF50',
      sad: '#2196F3',
      angry: '#F44336',
      neutral: '#9E9E9E',
      surprise: '#FF9800',
      fear: '#9C27B0',
      disgust: '#795548',
    };
    return colors[emotion?.toLowerCase()] || '#607D8B';
  };

  if (loading) {
    return (
      <div className="results-page">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-page">
        <div className="error-card">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')}>Back to Upload</button>
        </div>
      </div>
    );
  }

  // Video URL for local mode playback
  const videoStreamUrl = getVideoStreamUrl(jobId, executionMode);

  return (
    <div className="results-page">
      <div className="results-header">
        <h2>✅ Emotion Detection Results</h2>
        <p className="job-id">Job ID: {jobId}</p>
        <span className={`mode-badge mode-${executionMode}`}>
          {isLocalMode ? '💻 Local CPU Mode' : '☁️ Colab GPU Mode'}
        </span>
      </div>

      {/* Video Player for Local Mode */}
      {isLocalMode && (
        <div className="video-section">
          <h3>🎬 Processed Video</h3>
          <video 
            controls 
            className="result-video"
            src={videoStreamUrl}
          >
            Your browser does not support the video tag.
          </video>
        </div>
      )}

      {/* Download Section */}
      <div className="download-section">
        <h3>📥 Download Results</h3>
        <div className="download-buttons">
          <button onClick={handleDownloadVideo} className="download-btn video-btn">
            🎬 Download Processed Video
          </button>
          <button onClick={handleDownloadJSON} className="download-btn json-btn">
            📊 Download Emotion JSON
          </button>
        </div>
        <p className="download-note">
          💡 Tip: Use VLC or any video player to view the processed video with emotion annotations.
        </p>
      </div>

      {/* Summary Stats */}
      <div className="stats-section">
        <h3>📈 Processing Summary</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-value">{results?.total_frames || 0}</span>
            <span className="stat-label">Frames Processed</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">
              {results?.emotion_data ? Object.keys(results.emotion_data).length : 0}
            </span>
            <span className="stat-label">People Detected</span>
          </div>
        </div>
      </div>

      {/* Emotion Color Palette Legend */}
      <div className="color-palette-section">
        <h3>🎨 Emotion Color Palette</h3>
        <div className="color-palette">
          <div className="color-item">
            <div className="color-box" style={{ backgroundColor: '#4CAF50' }}></div>
            <span>Happy</span>
          </div>
          <div className="color-item">
            <div className="color-box" style={{ backgroundColor: '#2196F3' }}></div>
            <span>Sad</span>
          </div>
          <div className="color-item">
            <div className="color-box" style={{ backgroundColor: '#F44336' }}></div>
            <span>Angry</span>
          </div>
          <div className="color-item">
            <div className="color-box" style={{ backgroundColor: '#9E9E9E' }}></div>
            <span>Neutral</span>
          </div>
          <div className="color-item">
            <div className="color-box" style={{ backgroundColor: '#FF9800' }}></div>
            <span>Surprise</span>
          </div>
          <div className="color-item">
            <div className="color-box" style={{ backgroundColor: '#9C27B0' }}></div>
            <span>Fear</span>
          </div>
          <div className="color-item">
            <div className="color-box" style={{ backgroundColor: '#795548' }}></div>
            <span>Disgust</span>
          </div>
        </div>
      </div>

      {/* Summary Chart - All People */}
      <div className="emotion-section">
        <h3>📊 Emotion Summary - All People</h3>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: '1rem' }}>
          Dominant emotion for each person across all frames
        </p>
        {results?.emotion_data && typeof results.emotion_data === 'object' && Object.keys(results.emotion_data).length > 0 ? (
          <SummaryChart emotionData={results.emotion_data} />
        ) : (
          <p className="no-data">No emotion data available</p>
        )}
      </div>

      {/* Emotion Analysis */}
      <div className="emotion-section">
        <h3>😊 Emotion Analysis by Person</h3>
        
        {results?.emotion_data && typeof results.emotion_data === 'object' && Object.keys(results.emotion_data).length > 0 ? (
          <div className="emotion-cards">
            {Object.entries(results.emotion_data).map(([personId, data]) => (
              <div key={personId} className="person-card">
                <h4>{personId.replace('_', ' ').toUpperCase()}</h4>
                
                {data && data.emotions && Object.keys(data.emotions).length > 0 ? (
                  <>
                    <div className="emotion-stats">
                      <p><strong>Total Frames:</strong> {data.frame_count || 'N/A'}</p>
                    </div>

                    <EmotionChart emotions={data.emotions} frames={data.frames} />

                    <div className="emotion-list">
                      {Object.entries(data.emotions)
                        .sort(([, a], [, b]) => b - a)
                        .map(([emotion, count]) => (
                          <div key={emotion} className="emotion-item">
                            <span className="emotion-name">{emotion}</span>
                            <span className="emotion-count">{count} frames</span>
                            <div className="emotion-bar">
                              <div
                                className="emotion-bar-fill"
                                style={{
                                  width: `${(count / (data.frame_count || 1)) * 100}%`,
                                  backgroundColor: getEmotionColor(emotion)
                                }}
                              />
                            </div>
                          </div>
                        ))}
                    </div>
                  </>
                ) : (
                  <p className="no-data">No emotion data available for this person</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="no-results">
            <p>No faces were detected in the video, or emotion data is not available.</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="navigation-section">
        <button onClick={() => navigate('/')} className="nav-btn">
          ← Upload Another Video
        </button>
        <button onClick={() => navigate('/history')} className="nav-btn secondary">
          📜 View History
        </button>
      </div>
    </div>
  );
}

export default ResultsPage;
