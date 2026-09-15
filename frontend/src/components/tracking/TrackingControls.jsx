import React, { useState, useEffect } from 'react';
import { Sliders, RotateCcw, Play, Pause, FastForward, Check, RefreshCw } from 'lucide-react';

export default function TrackingControls({
  config,
  onUpdateConfig,
  onReset,
  onStep,
  isRunning,
  onToggleRunning,
  disabled = false,
}) {
  const [localConfig, setLocalConfig] = useState({
    enabled: true,
    process_noise: 10.0,
    measurement_noise: 4.0,
    max_missed_frames: 10,
    min_detection_confidence: 0.20,
    prediction_enabled: true,
    prediction_lead_time: 0.0,
    adaptive_measurement_noise: true,
  });

  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (config) {
      setLocalConfig({
        enabled: config.enabled ?? true,
        process_noise: config.process_noise ?? 10.0,
        measurement_noise: config.measurement_noise ?? 4.0,
        max_missed_frames: config.max_missed_frames ?? 10,
        min_detection_confidence: config.min_detection_confidence ?? 0.20,
        prediction_enabled: config.prediction_enabled ?? true,
        prediction_lead_time: config.prediction_lead_time ?? 0.0,
        adaptive_measurement_noise: config.adaptive_measurement_noise ?? true,
      });
    }
  }, [config]);

  const handleChange = (key, value) => {
    setLocalConfig((prev) => ({ ...prev, [key]: value }));
  };

  const handleApply = async () => {
    setSaving(true);
    try {
      await onUpdateConfig(localConfig);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2000);
    } catch (err) {
      console.error('Failed to update config:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card tracking-controls-card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sliders size={18} className="text-cyan-400" />
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>KALMAN FILTER PARAMETERS & ACTIONS</h3>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '5px 10px', display: 'flex', alignItems: 'center', gap: '4px' }}
            onClick={onReset}
            disabled={disabled}
            title="Reset Tracker state and history"
          >
            <RotateCcw size={14} />
            <span>Reset</span>
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '5px 10px', display: 'flex', alignItems: 'center', gap: '4px' }}
            onClick={onStep}
            disabled={disabled || isRunning}
            title="Execute single tracking step"
          >
            <FastForward size={14} />
            <span>Step</span>
          </button>

          <button
            type="button"
            className={`btn ${isRunning ? 'btn-danger' : 'btn-primary'}`}
            style={{ fontSize: '0.75rem', padding: '5px 12px', display: 'flex', alignItems: 'center', gap: '4px' }}
            onClick={onToggleRunning}
            disabled={disabled}
          >
            {isRunning ? <Pause size={14} /> : <Play size={14} />}
            <span>{isRunning ? 'Pause Loop' : 'Live Track'}</span>
          </button>
        </div>
      </div>

      <div className="card-body" style={{ marginTop: '0.75rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
          {/* Process Noise Spectral Density q */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
              <label htmlFor="kf-process-noise" style={{ color: '#cbd5e1', fontWeight: 500 }}>Process Noise (q):</label>
              <span style={{ color: '#38bdf8', fontWeight: 600 }}>{localConfig.process_noise.toFixed(1)}</span>
            </div>
            <input
              id="kf-process-noise"
              type="range"
              min="0.1"
              max="50.0"
              step="0.5"
              value={localConfig.process_noise}
              onChange={(e) => handleChange('process_noise', parseFloat(e.target.value))}
              disabled={disabled}
              className="range-slider"
            />
            <span style={{ fontSize: '0.68rem', color: '#64748b' }}>Lower = Smoother / Higher = Fast Response</span>
          </div>

          {/* Measurement Noise Variance r */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
              <label htmlFor="kf-meas-noise" style={{ color: '#cbd5e1', fontWeight: 500 }}>Measurement Noise (r):</label>
              <span style={{ color: '#38bdf8', fontWeight: 600 }}>{localConfig.measurement_noise.toFixed(1)}</span>
            </div>
            <input
              id="kf-meas-noise"
              type="range"
              min="0.1"
              max="40.0"
              step="0.5"
              value={localConfig.measurement_noise}
              onChange={(e) => handleChange('measurement_noise', parseFloat(e.target.value))}
              disabled={disabled}
              className="range-slider"
            />
            <span style={{ fontSize: '0.68rem', color: '#64748b' }}>Expected detector centroid jitter (&sigma;z&sup2;)</span>
          </div>

          {/* Max Missed Frames */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
              <label htmlFor="kf-max-misses" style={{ color: '#cbd5e1', fontWeight: 500 }}>Max Coasting Frames:</label>
              <span style={{ color: '#fbbf24', fontWeight: 600 }}>{localConfig.max_missed_frames}</span>
            </div>
            <input
              id="kf-max-misses"
              type="range"
              min="1"
              max="30"
              step="1"
              value={localConfig.max_missed_frames}
              onChange={(e) => handleChange('max_missed_frames', parseInt(e.target.value, 10))}
              disabled={disabled}
              className="range-slider"
            />
            <span style={{ fontSize: '0.68rem', color: '#64748b' }}>Frames to coast in PREDICTING before LOST</span>
          </div>

          {/* Min Detection Confidence */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
              <label htmlFor="kf-min-conf" style={{ color: '#cbd5e1', fontWeight: 500 }}>Min Detector Confidence:</label>
              <span style={{ color: '#38bdf8', fontWeight: 600 }}>{(localConfig.min_detection_confidence * 100).toFixed(0)}%</span>
            </div>
            <input
              id="kf-min-conf"
              type="range"
              min="0.05"
              max="0.80"
              step="0.05"
              value={localConfig.min_detection_confidence}
              onChange={(e) => handleChange('min_detection_confidence', parseFloat(e.target.value))}
              disabled={disabled}
              className="range-slider"
            />
            <span style={{ fontSize: '0.68rem', color: '#64748b' }}>Rejects noisy false positives</span>
          </div>
        </div>

        {/* Toggles & Apply Button */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.05)', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: '#cbd5e1', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={localConfig.adaptive_measurement_noise}
                onChange={(e) => handleChange('adaptive_measurement_noise', e.target.checked)}
                disabled={disabled}
              />
              <span>Adaptive Measurement R (Scales with Det Conf)</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: '#cbd5e1', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={localConfig.prediction_enabled}
                onChange={(e) => handleChange('prediction_enabled', e.target.checked)}
                disabled={disabled}
              />
              <span>Lead Motion Extrapolation</span>
            </label>
          </div>

          <button
            type="button"
            className="btn btn-primary"
            style={{ fontSize: '0.75rem', padding: '6px 14px', display: 'flex', alignItems: 'center', gap: '6px' }}
            onClick={handleApply}
            disabled={disabled || saving}
          >
            {savedSuccess ? <Check size={14} className="text-emerald-400" /> : <RefreshCw size={14} className={saving ? 'animate-spin' : ''} />}
            <span>{savedSuccess ? 'Applied!' : saving ? 'Updating...' : 'Apply Config'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
