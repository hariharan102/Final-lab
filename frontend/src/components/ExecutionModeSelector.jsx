/**
 * Execution Mode Selector Component
 * 
 * Toggle switch/selector that allows users to choose between:
 * - Google Colab (GPU, manual) - existing workflow
 * - Local Machine (CPU, automatic) - new workflow
 * 
 * This component can be placed in the header or upload page.
 */

import React from 'react';
import { useExecutionMode, EXECUTION_MODES, MODE_INFO } from '../context/ExecutionModeContext';
import './ExecutionModeSelector.css';

function ExecutionModeSelector({ showDetails = true }) {
  const { mode, setMode, modeInfo } = useExecutionMode();

  const handleModeChange = (newMode) => {
    console.log(`[ExecutionModeSelector] Changing mode from ${mode} to ${newMode}`);
    setMode(newMode);
  };

  // Debug: Log current mode
  React.useEffect(() => {
    console.log('[ExecutionModeSelector] Current mode:', mode);
  }, [mode]);

  return (
    <div className="execution-mode-selector">
      <h3 className="selector-title">Execution Mode</h3>
      
      <div className="mode-toggle">
        {Object.values(EXECUTION_MODES).map((modeOption) => {
          const info = MODE_INFO[modeOption];
          const isActive = mode === modeOption;
          
          return (
            <button
              key={modeOption}
              className={`mode-button ${isActive ? 'active' : ''}`}
              onClick={() => handleModeChange(modeOption)}
              aria-pressed={isActive}
            >
              <span className="mode-icon">{info.icon}</span>
              <span className="mode-name">{info.name}</span>
            </button>
          );
        })}
      </div>

      {showDetails && (
        <div className="mode-details">
          <p className="mode-description">{modeInfo.description}</p>
          <ul className="mode-features">
            {modeInfo.features.map((feature, index) => (
              <li key={index}>{feature}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ExecutionModeSelector;
