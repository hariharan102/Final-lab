/**
 * Execution Mode Context
 * 
 * This context manages the global execution mode toggle:
 * - "colab": Use existing Colab backend (manual GPU processing)
 * - "local": Use new local backend (automatic CPU processing)
 * 
 * The mode selection affects which API endpoints are called throughout the app.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

// Execution modes
export const EXECUTION_MODES = {
  LOCAL: 'local',
  COLAB: 'colab'
};

// Mode descriptions for UI
export const MODE_INFO = {
  [EXECUTION_MODES.COLAB]: {
    name: 'Google Colab (GPU)',
    description: 'Manual processing with T4 GPU in Colab',
    icon: '☁️',
    features: [
      'Requires Google account',
      'Manual Colab notebook execution',
      'Fast GPU processing (T4)',
      'Files stored in Google Drive'
    ]
  },
  [EXECUTION_MODES.LOCAL]: {
    name: 'Local Machine (CPU)',
    description: 'Automatic processing on your computer',
    icon: '💻',
    features: [
      'No Google account needed',
      'Fully automatic processing',
      'CPU-based (slower but simpler)',
      'Files stored locally'
    ]
  }
};

// Create context
const ExecutionModeContext = createContext();

/**
 * Provider component that wraps the app and provides execution mode state.
 */
export function ExecutionModeProvider({ children }) {
  // Load saved mode from localStorage, default to 'local' (Local Machine first)
  const [mode, setMode] = useState(() => {
    const saved = localStorage.getItem('executionMode');
    const initialMode = saved || EXECUTION_MODES.LOCAL;
    console.log('[ExecutionModeProvider] Initializing with mode:', initialMode);
    return initialMode;
  });

  // Persist mode changes to localStorage
  useEffect(() => {
    localStorage.setItem('executionMode', mode);
    console.log(`[ExecutionModeProvider] Mode updated to: ${mode}`);
    console.log(`[ExecutionModeProvider] isColab: ${mode === EXECUTION_MODES.COLAB}, isLocal: ${mode === EXECUTION_MODES.LOCAL}`);
  }, [mode]);

  const value = {
    mode,
    setMode,
    isColab: mode === EXECUTION_MODES.COLAB,
    isLocal: mode === EXECUTION_MODES.LOCAL,
    modeInfo: MODE_INFO[mode]
  };

  return (
    <ExecutionModeContext.Provider value={value}>
      {children}
    </ExecutionModeContext.Provider>
  );
}

/**
 * Hook to access execution mode from any component.
 */
export function useExecutionMode() {
  const context = useContext(ExecutionModeContext);
  if (!context) {
    throw new Error('useExecutionMode must be used within ExecutionModeProvider');
  }
  return context;
}

export default ExecutionModeContext;
