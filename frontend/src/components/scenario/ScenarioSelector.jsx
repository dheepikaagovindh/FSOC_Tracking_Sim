import React from 'react';
import { Layers, Bookmark } from 'lucide-react';

export default function ScenarioSelector({ presets, activePresetId, onSelectPreset }) {
  return (
    <div className="hud-card active-card">
      <div className="card-header">
        <div className="card-title-group">
          <Layers size={18} />
          <h2>Scenario Presets & Mission Profiles</h2>
        </div>
        <span className="card-badge">7 AVAILABLE PRESETS</span>
      </div>
      <div className="card-body preset-selector-container">
        <div className="preset-pills-grid">
          {presets.map((preset) => {
            const isActive = activePresetId === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                className={`preset-pill-button ${isActive ? 'active' : ''}`}
                onClick={() => onSelectPreset(preset.id)}
              >
                <div className="preset-pill-header">
                  <span className="preset-pill-name">{preset.name}</span>
                  <Bookmark size={14} color={isActive ? '#22d3ee' : '#64748b'} />
                </div>
                <span className="preset-pill-difficulty">{preset.difficulty}</span>
                <p className="preset-pill-desc">{preset.description}</p>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
