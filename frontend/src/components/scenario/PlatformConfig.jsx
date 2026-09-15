import React from 'react';
import { Navigation, Compass, Activity } from 'lucide-react';

export default function PlatformConfig({ title, badge, platform, onChange, errors = [], fieldPrefix }) {
  const handleChange = (field, value) => {
    onChange({
      ...platform,
      [field]: typeof value === 'string' && field === 'motion_profile' ? value : Number(value),
    });
  };

  const hasError = (field) => errors.some((e) => e.includes(`${fieldPrefix}.${field}`));

  return (
    <div className="hud-card">
      <div className="card-header">
        <div className="card-title-group">
          <Navigation size={18} />
          <h2>{title}</h2>
        </div>
        <span className="card-badge">{badge}</span>
      </div>
      <div className="card-body">
        {/* Motion Profile Selector */}
        <div className="form-group" style={{ marginBottom: '16px' }}>
          <label className="form-label">
            <span>Motion Kinematics Profile</span>
            <span className="unit-badge">PROFILE TYPE</span>
          </label>
          <select
            className={`form-select ${hasError('motion_profile') ? 'error-input' : ''}`}
            value={platform.motion_profile}
            onChange={(e) => handleChange('motion_profile', e.target.value)}
          >
            <option value="static">Static (Stationary Terminal)</option>
            <option value="drift">Drift (Constant Linear Velocity)</option>
            <option value="sway">Sway (Sinusoidal Platform Oscillation)</option>
            <option value="orbit">Orbit (Circular Trajectory)</option>
          </select>
        </div>

        {/* Initial Position Coordinates (X, Y, Z) */}
        <div style={{ marginBottom: '16px' }}>
          <label className="form-label" style={{ marginBottom: '6px' }}>
            <span>Initial Position (World Frame)</span>
            <span className="unit-badge">meters (X, Y, Z)</span>
          </label>
          <div className="form-grid-3">
            <div className="form-group">
              <input
                type="number"
                step="1"
                placeholder="X (m)"
                className="form-input"
                value={platform.initial_position_x}
                onChange={(e) => handleChange('initial_position_x', e.target.value)}
              />
            </div>
            <div className="form-group">
              <input
                type="number"
                step="1"
                placeholder="Y (m)"
                className="form-input"
                value={platform.initial_position_y}
                onChange={(e) => handleChange('initial_position_y', e.target.value)}
              />
            </div>
            <div className="form-group">
              <input
                type="number"
                step="1"
                placeholder="Z (m)"
                className="form-input"
                value={platform.initial_position_z}
                onChange={(e) => handleChange('initial_position_z', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Dynamic Velocity or Oscillation Parameters */}
        {platform.motion_profile === 'drift' && (
          <div style={{ marginBottom: '16px' }}>
            <label className="form-label" style={{ marginBottom: '6px' }}>
              <span>Linear Velocity Vector</span>
              <span className="unit-badge">m/s (Vx, Vy, Vz)</span>
            </label>
            <div className="form-grid-3">
              <input
                type="number"
                step="0.1"
                placeholder="Vx (m/s)"
                className="form-input"
                value={platform.velocity_x}
                onChange={(e) => handleChange('velocity_x', e.target.value)}
              />
              <input
                type="number"
                step="0.1"
                placeholder="Vy (m/s)"
                className="form-input"
                value={platform.velocity_y}
                onChange={(e) => handleChange('velocity_y', e.target.value)}
              />
              <input
                type="number"
                step="0.1"
                placeholder="Vz (m/s)"
                className="form-input"
                value={platform.velocity_z}
                onChange={(e) => handleChange('velocity_z', e.target.value)}
              />
            </div>
          </div>
        )}

        {(platform.motion_profile === 'sway' || platform.motion_profile === 'orbit') && (
          <div className="form-grid-2">
            <div className="form-group">
              <label className="form-label">
                <span>Oscillation Amplitude</span>
                <span className="unit-badge">meters</span>
              </label>
              <div className="slider-group">
                <input
                  type="range"
                  className="hud-slider"
                  min={0}
                  max={50}
                  step={0.5}
                  value={platform.amplitude}
                  onChange={(e) => handleChange('amplitude', e.target.value)}
                />
                <span className="slider-val-box">{platform.amplitude} m</span>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">
                <span>Motion Frequency</span>
                <span className="unit-badge">Hz</span>
              </label>
              <div className="slider-group">
                <input
                  type="range"
                  className="hud-slider"
                  min={0}
                  max={5}
                  step={0.05}
                  value={platform.frequency}
                  onChange={(e) => handleChange('frequency', e.target.value)}
                />
                <span className="slider-val-box">{platform.frequency} Hz</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
