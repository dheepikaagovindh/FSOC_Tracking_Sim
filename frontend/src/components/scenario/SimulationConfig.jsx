import React from 'react';
import { PlayCircle, Database, Film } from 'lucide-react';

export default function SimulationConfig({ simulation, onChange, errors = [] }) {
  const handleChange = (field, value) => {
    onChange({
      ...simulation,
      [field]: field.startsWith('record') ? Boolean(value) : Number(value),
    });
  };

  const handleToggle = (field) => {
    onChange({
      ...simulation,
      [field]: !simulation[field],
    });
  };

  const hasError = (field) => errors.some((e) => e.includes(`simulation.${field}`));

  return (
    <div className="hud-card">
      <div className="card-header">
        <div className="card-title-group">
          <PlayCircle size={18} />
          <h2>Simulation Timing & Data Logging</h2>
        </div>
        <span className="card-badge">EXECUTION CONTROLS</span>
      </div>
      <div className="card-body">
        <div className="form-grid-3" style={{ marginBottom: '16px' }}>
          {/* Duration */}
          <div className="form-group">
            <label className="form-label">
              <span>Duration</span>
              <span className="unit-badge">seconds</span>
            </label>
            <input
              type="number"
              min="1"
              max="3600"
              step="1"
              className={`form-input ${hasError('duration') ? 'error-input' : ''}`}
              value={simulation.duration}
              onChange={(e) => handleChange('duration', e.target.value)}
            />
          </div>

          {/* FPS */}
          <div className="form-group">
            <label className="form-label">
              <span>Frame Rate</span>
              <span className="unit-badge">FPS</span>
            </label>
            <input
              type="number"
              min="1"
              max="240"
              step="1"
              className={`form-input ${hasError('fps') ? 'error-input' : ''}`}
              value={simulation.fps}
              onChange={(e) => handleChange('fps', e.target.value)}
            />
          </div>

          {/* Random Seed */}
          <div className="form-group">
            <label className="form-label">
              <span>Random Seed</span>
              <span className="unit-badge">PRNG</span>
            </label>
            <input
              type="number"
              min="0"
              className={`form-input ${hasError('random_seed') ? 'error-input' : ''}`}
              value={simulation.random_seed}
              onChange={(e) => handleChange('random_seed', e.target.value)}
            />
          </div>
        </div>

        {/* Logging Toggles */}
        <div className="form-grid-2">
          <div className="toggle-row">
            <div className="toggle-label-group">
              <span className="toggle-title">Record Telemetry</span>
              <span className="toggle-subtitle">Log pointing error, kinematics, and state</span>
            </div>
            <label className="switch">
              <input
                type="checkbox"
                checked={simulation.record_telemetry}
                onChange={() => handleToggle('record_telemetry')}
              />
              <span className="slider-round" />
            </label>
          </div>

          <div className="toggle-row">
            <div className="toggle-label-group">
              <span className="toggle-title">Record Synthetic Frames</span>
              <span className="toggle-subtitle">Save raw focal plane video stream</span>
            </div>
            <label className="switch">
              <input
                type="checkbox"
                checked={simulation.record_frames}
                onChange={() => handleToggle('record_frames')}
              />
              <span className="slider-round" />
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
