import React from 'react';
import { Sun, Disc, Route } from 'lucide-react';

export default function BeaconConfig({ beacon, onChange, errors = [] }) {
  const handleChange = (field, value) => {
    onChange({
      ...beacon,
      [field]: field === 'trajectory' ? value : Number(value),
    });
  };

  const hasError = (field) => errors.some((e) => e.includes(`beacon.${field}`));

  return (
    <div className="hud-card">
      <div className="card-header">
        <div className="card-title-group">
          <Sun size={18} />
          <h2>Optical Transmitter Beacon</h2>
        </div>
        <span className="card-badge">LASER BEAM EMISSION</span>
      </div>
      <div className="card-body">
        <div className="form-grid-2" style={{ marginBottom: '16px' }}>
          {/* Beacon Brightness */}
          <div className="form-group">
            <label className="form-label">
              <span>Normalized Optical Power</span>
              <span className="unit-badge">Intensity</span>
            </label>
            <div className="slider-group">
              <input
                type="range"
                className="hud-slider"
                min={0.1}
                max={5.0}
                step={0.1}
                value={beacon.brightness}
                onChange={(e) => handleChange('brightness', e.target.value)}
              />
              <span className="slider-val-box">{beacon.brightness}x</span>
            </div>
          </div>

          {/* Beacon Spot Size */}
          <div className="form-group">
            <label className="form-label">
              <span>Effective Spot Diameter</span>
              <span className="unit-badge">pixels</span>
            </label>
            <div className="slider-group">
              <input
                type="range"
                className="hud-slider"
                min={1}
                max={25}
                step={0.5}
                value={beacon.size}
                onChange={(e) => handleChange('size', e.target.value)}
              />
              <span className="slider-val-box">{beacon.size} px</span>
            </div>
          </div>
        </div>

        {/* Trajectory Selector */}
        <div className="form-group">
          <label className="form-label">
            <span>Beacon Beam Trajectory</span>
            <span className="unit-badge">TRAJECTORY TYPE</span>
          </label>
          <select
            className={`form-select ${hasError('trajectory') ? 'error-input' : ''}`}
            value={beacon.trajectory}
            onChange={(e) => handleChange('trajectory', e.target.value)}
          >
            <option value="static">Static (Stationary Optical Axis)</option>
            <option value="linear">Linear (Constant Heading Translation)</option>
            <option value="circular">Circular (Conical Optical Scan)</option>
            <option value="custom">Custom (User-Defined Parameterization)</option>
          </select>
        </div>
      </div>
    </div>
  );
}
