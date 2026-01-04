/**
 * API Service for Emotion Detection - Dual Backend Support
 * 
 * This service handles all HTTP requests to BOTH backends:
 * 
 * 1. COLAB BACKEND (existing - Django @ port 8000)
 *    - Manual GPU processing via Google Colab
 *    - Files stored in Google Drive
 *    - User must open Colab and click "Run All"
 * 
 * 2. LOCAL BACKEND (new - FastAPI @ port 8001)
 *    - Automatic CPU processing
 *    - Files stored locally
 *    - No manual steps required
 * 
 * The `mode` parameter determines which backend to use.
 */

import axios from 'axios';

// Backend URLs - TWO SEPARATE BACKENDS
const COLAB_API_URL = 'http://localhost:8000/api';  // Existing Django backend
const LOCAL_API_URL = 'http://localhost:8001';      // New FastAPI backend

// Create axios instances for each backend
const colabClient = axios.create({
  baseURL: COLAB_API_URL,
  headers: { 'Content-Type': 'application/json' },
});

const localClient = axios.create({
  baseURL: LOCAL_API_URL,
  headers: { 'Content-Type': 'application/json' },
});

/**
 * Get the appropriate API client based on execution mode.
 * @param {string} mode - 'colab' or 'local'
 */
const getClient = (mode) => mode === 'local' ? localClient : colabClient;

/**
 * Upload a video file for processing.
 * 
 * COLAB MODE: Uploads to Google Drive, returns Colab URL for manual processing
 * LOCAL MODE: Uploads locally, processing starts automatically
 * 
 * @param {File} videoFile - Video file from file input
 * @param {string} mode - 'colab' or 'local'
 * @returns {Promise} Response with job_id and status
 */
export const uploadVideo = async (videoFile, mode = 'colab') => {
  console.log(`[API] uploadVideo (mode: ${mode}):`, {
    name: videoFile.name,
    size: videoFile.size,
    type: videoFile.type
  });
  
  const formData = new FormData();
  formData.append('video', videoFile);
  
  const client = getClient(mode);
  const endpoint = mode === 'local' ? '/local/jobs/upload' : '/jobs/upload/';
  
  console.log(`[API] POST ${endpoint}`);

  try {
    const response = await client.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    console.log('[API] Upload response:', response.data);
    return {
      ...response.data,
      execution_mode: mode
    };
  } catch (error) {
    console.error('[API] Upload error:', error);
    throw error;
  }
};

/**
 * Get current status of a processing job.
 * 
 * Frontend should poll this every 1-2 seconds during processing.
 * 
 * @param {string} jobId - UUID of the job
 * @param {string} mode - 'colab' or 'local'
 * @returns {Promise} Current status information
 */
export const getJobStatus = async (jobId, mode = 'colab') => {
  const client = getClient(mode);
  const endpoint = mode === 'local' 
    ? `/local/jobs/${jobId}/status` 
    : `/jobs/${jobId}/status/`;
  
  const response = await client.get(endpoint);
  return {
    ...response.data,
    execution_mode: mode
  };
};

/**
 * Get processing results (only available when status=DONE).
 * 
 * @param {string} jobId - UUID of the job
 * @param {string} mode - 'colab' or 'local'
 * @returns {Promise} Results including video URL and emotion data
 */
export const getJobResults = async (jobId, mode = 'colab') => {
  const client = getClient(mode);
  const endpoint = mode === 'local' 
    ? `/local/jobs/${jobId}/results` 
    : `/jobs/${jobId}/results/`;
  
  const response = await client.get(endpoint);
  return {
    ...response.data,
    execution_mode: mode
  };
};

/**
 * Get the video stream URL based on execution mode.
 * 
 * @param {string} jobId - UUID of the job
 * @param {string} mode - 'colab' or 'local'
 * @returns {string} Full URL to stream the video
 */
export const getVideoStreamUrl = (jobId, mode = 'colab') => {
  const baseUrl = mode === 'local' ? LOCAL_API_URL : COLAB_API_URL;
  const endpoint = mode === 'local' 
    ? `/local/jobs/${jobId}/stream` 
    : `/jobs/${jobId}/stream/`;
  return `${baseUrl}${endpoint}`;
};

/**
 * Get list of all jobs (optional - for debugging).
 * 
 * @param {string} mode - 'colab' or 'local'
 * @returns {Promise} Array of all video jobs
 */
export const getAllJobs = async (mode = 'colab') => {
  const client = getClient(mode);
  const endpoint = mode === 'local' ? '/local/jobs-list' : '/jobs/';
  const response = await client.get(endpoint);
  return response.data;
};

/**
 * Get detailed info about a specific job.
 * 
 * @param {string} jobId - UUID of the job
 * @param {string} mode - 'colab' or 'local'
 * @returns {Promise} Detailed job information
 */
export const getJobDetail = async (jobId, mode = 'colab') => {
  const client = getClient(mode);
  const endpoint = mode === 'local' 
    ? `/local/jobs/${jobId}/status` 
    : `/jobs/${jobId}/`;
  const response = await client.get(endpoint);
  return response.data;
};

/**
 * Terminate/cancel a running or pending job.
 * 
 * @param {string} jobId - UUID of the job to terminate
 * @param {string} mode - 'colab' or 'local'
 * @returns {Promise} Response with updated job status
 */
export const terminateJob = async (jobId, mode = 'colab') => {
  const client = getClient(mode);
  const endpoint = mode === 'local' 
    ? `/local/jobs/${jobId}/terminate` 
    : `/jobs/${jobId}/terminate/`;
  const response = await client.post(endpoint);
  return response.data;
};

/**
 * Check if a backend is available/healthy.
 * 
 * @param {string} mode - 'colab' or 'local'
 * @returns {Promise<boolean>} True if backend is available
 */
export const checkBackendHealth = async (mode = 'colab') => {
  try {
    const client = getClient(mode);
    const endpoint = mode === 'local' ? '/health' : '/';
    await client.get(endpoint, { timeout: 3000 });
    return true;
  } catch {
    return false;
  }
};

export default {
  uploadVideo,
  getJobStatus,
  getJobResults,
  getVideoStreamUrl,
  getAllJobs,
  getJobDetail,
  terminateJob,
  checkBackendHealth,
};
