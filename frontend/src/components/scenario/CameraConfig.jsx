import React from 'react';
import { Camera, Aperture } from 'lucide-react';

export default function CameraConfig({ camera, onChange, errors = [] }) {
  const handleChange = (field, value) => {
    onChange({
      ...camera,
      [field]: Number(value),
    });
  };

  const hasError = (field) => errors.some((e) => e.includes(`camera.${field}`) || e.includes(`camera.resolution`));

  return (
    <div className="hud-card">
      <div className="card-header">
        <div className="card-title-group">
          <Camera size={18} />
          <h2>Virtual Camera & Optical Sensor</h2>
        </div>
        <span className="card-badge">RECEIVER OPTICS</span>
      </div>
      <div className="card-body">
        <div className="form-grid-2" style={{ marginBottom: '16px' }}>
          {/* Resolution Width */}
          <div className="form-group">
            <label className="form-label">
              <span>Sensor Width</span>
              <span className="unit-badge">pixels</span>
            </label>
            <input
              type="number"
              className={`form-input ${hasError('width') ? 'error-input' : ''}`}
              value={camera.width}
              min={64}
              max={7680}
              step={16}
              onChange={(e) => handleChange('width', e.target.value)}
            />
          </div>

          {/* Resolution Height */}
          <div className="form-group">
            <label className="form-label">
              <span>Sensor Height</span>
              <span className="unit-badge">pixels</span>
            </label>
            <input
              type="number"
              className={`form-input ${hasError('height') ? 'error-input' : ''}`}
              value={camera.height}
              min={64}
              max={4320}
              step={16}
              onChange={(e) => handleChange('height', e.target.value)}
            />
          </div>
        </div>

        <div className="form-grid-2" style={{ marginBottom: '16px' }}>
          {/* Horizontal FOV */}
          <div className="form-group">
            <label className="form-label">
              <span>Horizontal FOV</span>
              <span className="unit-badge">{camera.horizontal_fov_deg}°</span>
            </label>
            <div className="slider-group">
              <input
                type="range"
                className="hud-slider"
                min={1}
                max={120}
                step={0.5}
                value={camera.horizontal_fov_deg}
                onChange={(e) => handleChange('horizontal_fov_deg', e.target.value)}
              />
              <span className="slider-val-box">{camera.horizontal_fov_deg}°</span>
            </div>
          </div>

          {/* Vertical FOV */}
          <div className="form-group">
            <label className="form-label">
              <span>Vertical FOV</span>
              <span className="unit-badge">{camera.vertical_fov_deg}°</span>
            </label>
            <div className="slider-group">
              <input
                type="range"
                className="hud-slider"
                min={1}
                max={90}
                step={0.5}
                value={camera.vertical_fov_deg}
                onChange={(e) => handleChange('vertical_fov_deg', e.target.value)}
              />
              <span className="slider-val-box">{camera.vertical_fov_deg}°</span>
            </div>
          </div>
        </div>

        <div className="form-grid-2">
          {/* Initial Pan */}
          <div className="form-group">
            <label className="form-label">
              <span>Initial Gimbal Pan (Azimuth)</span>
              <span className="unit-badge">deg [-180, 180]</span>
            </label>
            <div className="slider-group">
              <input
                type="range"
                className="hud-slider"
                min={-180}
                max={180}
                step={0.5}
                value={camera.initial_pan_deg}
                onChange={(e) => handleChange('initial_pan_deg', e.target.value)}
              />
              <span className="slider-val-box">{camera.initial_pan_deg}°</span>
            </div>
          </div>

          {/* Initial Tilt */}
          <div className="form-group">
            <label className="form-label">
              <span>Initial Gimbal Tilt (Elevation)</span>
              <span className="unit-badge">deg [-90, 90]</span>
            </label>
            <div className="slider-group">
              <input
                type="range"
                className="hud-slider"
                min={-90}
                max={90}
                step={0.5}
                value={camera.initial_tilt_deg}
                onChange={(e) => handleChange('initial_tilt_deg', e.target.value)}
              />
              <span className="slider-val-box">{camera.initial_tilt_deg}°</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
