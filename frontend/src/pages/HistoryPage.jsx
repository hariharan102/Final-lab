/**
 * History Page Component
 * 
 * Displays the history of all processed jobs for both Colab and Local modes.
 * Allows users to view past results or check status of pending jobs.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllJobs } from '../services/api';
import { useExecutionMode } from '../context/ExecutionModeContext';
import './HistoryPage.css';

function HistoryPage() {
  const navigate = useNavigate();
  const { mode } = useExecutionMode();
  
  const [activeTab, setActiveTab] = useState(mode); // 'colab' or 'local'
  const [colabJobs, setColabJobs] = useState([]);
  const [localJobs, setLocalJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAllJobs();
  }, []);

  const fetchAllJobs = async () => {
    setLoading(true);
    setError('');

    // Fetch jobs from both backends in parallel
    const results = await Promise.allSettled([
      getAllJobs('colab'),
      getAllJobs('local')
    ]);

    // Process Colab jobs
    if (results[0].status === 'fulfilled') {
      const data = results[0].value;
      // Handle both array and object with jobs property
      const jobs = Array.isArray(data) ? data : (data.jobs || []);
      setColabJobs(jobs);
    } else {
      console.log('Colab backend not available:', results[0].reason?.message);
      setColabJobs([]);
    }

    // Process Local jobs
    if (results[1].status === 'fulfilled') {
      const data = results[1].value;
      const jobs = Array.isArray(data) ? data : (data.jobs || []);
      setLocalJobs(jobs);
    } else {
      console.log('Local backend not available:', results[1].reason?.message);
      setLocalJobs([]);
    }

    setLoading(false);
  };

  const getStatusBadgeClass = (status) => {
    switch (status?.toUpperCase()) {
      case 'DONE':
        return 'status-done';
      case 'PROCESSING':
        return 'status-processing';
      case 'PENDING':
        return 'status-pending';
      case 'FAILED':
        return 'status-failed';
      case 'CANCELLED':
        return 'status-cancelled';
      default:
        return 'status-unknown';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleJobClick = (job, mode) => {
    const jobId = job.job_id || job.id;
    const status = job.status?.toUpperCase();
    
    if (status === 'DONE') {
      navigate(`/results/${jobId}`, { state: { executionMode: mode } });
    } else if (status === 'PROCESSING' || status === 'PENDING') {
      navigate(`/processing/${jobId}`, { state: { executionMode: mode } });
    }
  };

  const currentJobs = activeTab === 'local' ? localJobs : colabJobs;

  return (
    <div className="history-page">
      <div className="history-header">
        <h2>📜 Processing History</h2>
        <p>View all your past and ongoing emotion detection jobs</p>
        
        <button className="back-button" onClick={() => navigate('/')}>
          ← Back to Upload
        </button>
      </div>

      {/* Tab Selector */}
      <div className="tab-selector">
        <button 
          className={`tab-button ${activeTab === 'colab' ? 'active' : ''}`}
          onClick={() => setActiveTab('colab')}
        >
          ☁️ Colab GPU Jobs ({colabJobs.length})
        </button>
        <button 
          className={`tab-button ${activeTab === 'local' ? 'active' : ''}`}
          onClick={() => setActiveTab('local')}
        >
          💻 Local CPU Jobs ({localJobs.length})
        </button>
      </div>

      {/* Refresh Button */}
      <div className="refresh-section">
        <button className="refresh-button" onClick={fetchAllJobs} disabled={loading}>
          {loading ? '⏳ Loading...' : '🔄 Refresh'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {/* Jobs List */}
      <div className="jobs-container">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading jobs...</p>
          </div>
        ) : currentJobs.length === 0 ? (
          <div className="empty-state">
            <p>No jobs found for {activeTab === 'local' ? 'Local CPU' : 'Colab GPU'} mode.</p>
            <button onClick={() => navigate('/')}>Upload a Video</button>
          </div>
        ) : (
          <div className="jobs-list">
            {currentJobs.map((job, index) => {
              const jobId = job.job_id || job.id;
              const status = job.status?.toUpperCase() || 'UNKNOWN';
              const isDone = status === 'DONE';
              const isInProgress = ['PROCESSING', 'PENDING'].includes(status);
              
              // Generate download URLs
              const baseUrl = activeTab === 'local' ? 'http://localhost:8001' : 'http://localhost:8000/api';
              const videoUrl = activeTab === 'local' 
                ? `${baseUrl}/local/jobs/${jobId}/stream`
                : `${baseUrl}/jobs/${jobId}/stream/`;
              const jsonUrl = activeTab === 'local' 
                ? `${baseUrl}/local/jobs/${jobId}/json`
                : `${baseUrl}/jobs/${jobId}/json/`;
              
              return (
                <div 
                  key={jobId || index}
                  className="job-card"
                >
                  <div className="job-info">
                    <div className="job-id-row">
                      <span className="job-id-label">Job ID:</span>
                      <span className="job-id-value">{jobId || 'N/A'}</span>
                    </div>
                    
                    {job.original_filename && (
                      <div className="job-filename">
                        📁 {job.original_filename}
                      </div>
                    )}
                    
                    <div className="job-dates">
                      <span>Created: {formatDate(job.created_at)}</span>
                      {job.updated_at && (
                        <span>Updated: {formatDate(job.updated_at)}</span>
                      )}
                    </div>
                    
                    {job.status_message && (
                      <div className="job-message">
                        {job.status_message}
                      </div>
                    )}
                    
                    {/* Download buttons for completed jobs */}
                    {isDone && (
                      <div className="job-downloads">
                        <a 
                          href={videoUrl} 
                          download={`emotion_video_${jobId}.mp4`}
                          className="download-link-small video"
                          onClick={(e) => e.stopPropagation()}
                        >
                          🎬 Video
                        </a>
                        <a 
                          href={jsonUrl} 
                          download={`emotion_data_${jobId}.json`}
                          className="download-link-small json"
                          onClick={(e) => e.stopPropagation()}
                        >
                          📊 JSON
                        </a>
                        <button 
                          className="view-results-btn"
                          onClick={() => handleJobClick(job, activeTab)}
                        >
                          📈 View Results
                        </button>
                      </div>
                    )}
                    
                    {/* Progress button for in-progress jobs */}
                    {isInProgress && (
                      <div className="job-actions">
                        <button 
                          className="view-progress-btn"
                          onClick={() => handleJobClick(job, activeTab)}
                        >
                          👁️ View Progress
                        </button>
                      </div>
                    )}
                  </div>
                  
                  <div className="job-status">
                    <span className={`status-badge ${getStatusBadgeClass(status)}`}>
                      {status}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default HistoryPage;
