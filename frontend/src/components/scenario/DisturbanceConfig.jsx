import React from 'react';
import { Zap, Wind, EyeOff, RadioTower } from 'lucide-react';

export default function DisturbanceConfig({ disturbances, onChange, errors = [] }) {
  const handleToggle = (field) => {
    onChange({
      ...disturbances,
      [field]: !disturbances[field],
    });
  };

  const handleValueChange = (field, value) => {
    onChange({
      ...disturbances,
      [field]: Number(value),
    });
  };

  const setSeverity = (severity) => {
    let updates = { severity };
    if (severity === 'off') {
      updates = {
        severity: 'off',
        vibration_enabled: false,
        vibration_magnitude: 0.0,
        noise_enabled: false,
        noise_magnitude: 0.0,
        blur_enabled: false,
        blur_strength: 0.0,
        dropout_enabled: false,
        dropout_probability: 0.0,
        dropout_duration: 0.0,
      };
    } else if (severity === 'low') {
      updates = {
        severity: 'low',
        vibration_enabled: true,
        vibration_magnitude: 1.0,
        noise_enabled: true,
        noise_magnitude: 0.05,
        blur_enabled: false,
        blur_strength: 0.0,
        dropout_enabled: false,
        dropout_probability: 0.0,
        dropout_duration: 0.0,
      };
    } else if (severity === 'medium') {
      updates = {
        severity: 'medium',
        vibration_enabled: true,
        vibration_magnitude: 2.5,
        noise_enabled: true,
        noise_magnitude: 0.12,
        blur_enabled: true,
        blur_strength: 1.5,
        dropout_enabled: true,
        dropout_probability: 0.25,
        dropout_duration: 0.4,
      };
    } else if (severity === 'high') {
      updates = {
        severity: 'high',
        vibration_enabled: true,
        vibration_magnitude: 4.8,
        noise_enabled: true,
        noise_magnitude: 0.22,
        blur_enabled: true,
        blur_strength: 3.0,
        dropout_enabled: true,
        dropout_probability: 0.45,
        dropout_duration: 0.8,
      };
    }
    onChange({
      ...disturbances,
      ...updates,
    });
  };

  return (
    <div className="hud-card">
      <div className="card-header">
        <div className="card-title-group">
          <Zap size={18} />
          <h2>Environmental & Sensor Disturbances</h2>
        </div>
        <span className="card-badge">NOISE & JITTER INJECTION</span>
      </div>
      <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
        {/* Master Severity Segmented Buttons */}
        <div className="form-group">
          <label className="form-label">
            <span>Master Disturbance Severity</span>
            <span className="unit-badge">LEVEL</span>
          </label>
          <div className="severity-selector">
            {['off', 'low', 'medium', 'high'].map((sev) => (
              <button
                key={sev}
                type="button"
                className={`severity-btn ${disturbances.severity === sev ? `active ${sev}` : ''}`}
                onClick={() => setSeverity(sev)}
              >
                {sev.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Platform Micro-Vibration */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div className="toggle-row">
            <div className="toggle-label-group">
              <span className="toggle-title">Platform Micro-Vibration</span>
              <span className="toggle-subtitle">Aerospace motor / rotor jitter dynamics</span>
            </div>
            <label className="switch">
              <input
                type="checkbox"
                checked={disturbances.vibration_enabled}
                onChange={() => handleToggle('vibration_enabled')}
              />
              <span className="slider-round" />
            </label>
          </div>
          {disturbances.vibration_enabled && (
            <div className="slider-group" style={{ padding: '4px 10px' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8', minWidth: '70px' }}>Magnitude:</span>
              <input
                type="range"
                className="hud-slider"
                min={0.1}
                max={10.0}
                step={0.1}
                value={disturbances.vibration_magnitude}
                onChange={(e) => handleValueChange('vibration_magnitude', e.target.value)}
              />
              <span className="slider-val-box">{disturbances.vibration_magnitude} px</span>
            </div>
          )}
        </div>

        {/* Sensor Noise */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div className="toggle-row">
            <div className="toggle-label-group">
              <span className="toggle-title">Sensor Gaussian Noise</span>
              <span className="toggle-subtitle">Thermal read noise and background clutter</span>
            </div>
            <label className="switch">
              <input
                type="checkbox"
                checked={disturbances.noise_enabled}
                onChange={() => handleToggle('noise_enabled')}
              />
              <span className="slider-round" />
            </label>
          </div>
          {disturbances.noise_enabled && (
            <div className="slider-group" style={{ padding: '4px 10px' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8', minWidth: '70px' }}>Std Dev (σ):</span>
              <input
                type="range"
                className="hud-slider"
                min={0.01}
                max={0.50}
                step={0.01}
                value={disturbances.noise_magnitude}
                onChange={(e) => handleValueChange('noise_magnitude', e.target.value)}
              />
              <span className="slider-val-box">{disturbances.noise_magnitude}</span>
            </div>
          )}
        </div>

        {/* Optical Blur */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div className="toggle-row">
            <div className="toggle-label-group">
              <span className="toggle-title">Atmospheric Optical Blur</span>
              <span className="toggle-subtitle">PSF point-spread broadening and motion smear</span>
            </div>
            <label className="switch">
              <input
                type="checkbox"
                checked={disturbances.blur_enabled}
                onChange={() => handleToggle('blur_enabled')}
              />
              <span className="slider-round" />
            </label>
          </div>
          {disturbances.blur_enabled && (
            <div className="slider-group" style={{ padding: '4px 10px' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8', minWidth: '70px' }}>Strength:</span>
              <input
                type="range"
                className="hud-slider"
                min={0.5}
                max={5.0}
                step={0.1}
                value={disturbances.blur_strength}
                onChange={(e) => handleValueChange('blur_strength', e.target.value)}
              />
              <span className="slider-val-box">{disturbances.blur_strength} σ</span>
            </div>
          )}
        </div>

        {/* Beacon Dropout / Deep Fades */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div className="toggle-row">
            <div className="toggle-label-group">
              <span className="toggle-title">Beacon Scintillation & Dropouts</span>
              <span className="toggle-subtitle">Intermittent signal fading and line-of-sight blockage</span>
            </div>
            <label className="switch">
              <input
                type="checkbox"
                checked={disturbances.dropout_enabled}
                onChange={() => handleToggle('dropout_enabled')}
              />
              <span className="slider-round" />
            </label>
          </div>
          {disturbances.dropout_enabled && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', padding: '4px 10px' }}>
              <div className="slider-group">
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', minWidth: '70px' }}>Probability:</span>
                <input
                  type="range"
                  className="hud-slider"
                  min={0.0}
                  max={1.0}
                  step={0.05}
                  value={disturbances.dropout_probability}
                  onChange={(e) => handleValueChange('dropout_probability', e.target.value)}
                />
                <span className="slider-val-box">{(disturbances.dropout_probability * 100).toFixed(0)}%</span>
              </div>
              <div className="form-group">
                <label className="form-label">
                  <span>Mean Burst Duration</span>
                  <span className="unit-badge">seconds</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.0"
                  max="10.0"
                  className="form-input"
                  value={disturbances.dropout_duration}
                  onChange={(e) => handleValueChange('dropout_duration', e.target.value)}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
