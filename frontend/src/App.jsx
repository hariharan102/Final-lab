import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { ExecutionModeProvider, useExecutionMode } from './context/ExecutionModeContext';
import ExecutionModeSelector from './components/ExecutionModeSelector';
import UploadPage from './pages/UploadPage';
import ProcessingPage from './pages/ProcessingPage';
import ResultsPage from './pages/ResultsPage';
import HistoryPage from './pages/HistoryPage';
import './App.css';

/**
 * Header Component with Execution Mode Display
 * 
 * Shows current execution mode in the header for visibility.
 */
function AppHeader() {
  const { mode, modeInfo } = useExecutionMode();
  const navigate = useNavigate();
  
  // Debug logging
  React.useEffect(() => {
    console.log('[AppHeader] Current mode:', mode);
    console.log('[AppHeader] Mode info:', modeInfo);
  }, [mode, modeInfo]);
  
  return (
    <header className="App-header">
      <h1>🎭 Online and Offline Meeting Emotion Detection</h1>
      <p className="subtitle">
        {modeInfo?.icon || '🎯'} {mode === 'local' ? 'Local CPU Processing' : 'GPU Processing via Google Colab'}
      </p>
      {/* Debug Mode Display - Shows exact mode value */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{
          position: 'fixed',
          top: '10px',
          right: '10px',
          background: mode === 'local' ? '#6c5ce7' : '#4285f4',
          color: 'white',
          padding: '8px 16px',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 'bold',
          zIndex: 9999,
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
        }}>
          MODE: {mode.toUpperCase()}
        </div>
      )}
      <div className="header-controls">
        <div className="header-mode-indicator">
          <span className={`mode-badge mode-${mode}`}>
            {mode === 'local' ? '💻 Local Mode' : '☁️ Colab Mode'}
          </span>
        </div>
        <button className="history-button" onClick={() => navigate('/history')}>
          📜 History
        </button>
      </div>
    </header>
  );
}

/**
 * Footer Component with Architecture Info
 */
function AppFooter() {
  const { mode } = useExecutionMode();
  
  return (
    <footer className="App-footer">
      <p>
        {mode === 'local' 
          ? 'Architecture: React → FastAPI → Local CPU Processing → Results'
          : 'Architecture: React → Django → Google Drive → Colab (GPU) → Results'
        }
      </p>
    </footer>
  );
}

/**
 * Main App Component
 * 
 * Architecture Overview:
 * =====================
 * This app supports TWO execution modes:
 * 
 * 1. COLAB MODE (existing):
 *    React → Django (port 8000) → Google Drive → Manual Colab → Results
 * 
 * 2. LOCAL MODE (new):
 *    React → FastAPI (port 8001) → Local Storage → Automatic CPU → Results
 * 
 * The execution mode is selected on the Upload page and persists throughout
 * the processing flow. Each mode uses its OWN backend - they are separate.
 * 
 * Routing:
 * / → Upload video page (with mode selector)
 * /processing/:jobId → Live status monitoring
 * /results/:jobId → Display processed video and emotion data
 */
function App() {
  return (
    <ExecutionModeProvider>
      <Router>
        <div className="App">
          <AppHeader />

          <main className="App-main">
            <Routes>
              <Route path="/" element={<UploadPage />} />
              <Route path="/processing/:jobId" element={<ProcessingPage />} />
              <Route path="/results/:jobId" element={<ResultsPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          <AppFooter />
        </div>
      </Router>
    </ExecutionModeProvider>
  );
}

export default App;