import React, { useState, useEffect } from 'react';
import { Sliders, RotateCcw, Play, Pause, FastForward, Check, RefreshCw } from 'lucide-react';

export default function ErrorControls({
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
    pixel_tolerance: 5.0,
    angular_tolerance_deg: 0.25,
    use_angular_alignment: true,
    use_radial_alignment: true,
    use_prediction_when_tracking_missing: true,
  });

  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (config) {
      setLocalConfig({
        enabled: config.enabled ?? true,
        pixel_tolerance: config.pixel_tolerance ?? 5.0,
        angular_tolerance_deg: config.angular_tolerance_deg ?? 0.25,
        use_angular_alignment: config.use_angular_alignment ?? true,
        use_radial_alignment: config.use_radial_alignment ?? true,
        use_prediction_when_tracking_missing: config.use_prediction_when_tracking_missing ?? true,
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
      console.error('Failed to update alignment config:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card error-controls-card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sliders size={18} className="text-cyan-400" />
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>ALIGNMENT TOLERANCES & PARAMETERS</h3>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '5px 10px', display: 'flex', alignItems: 'center', gap: '4px' }}
            onClick={onReset}
            disabled={disabled}
            title="Reset Error state and rate history"
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
            title="Execute single calculation step"
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
            <span>{isRunning ? 'Pause Loop' : 'Live Align'}</span>
          </button>
        </div>
      </div>

      <div className="card-body" style={{ marginTop: '0.75rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
          {/* Angular Lock Tolerance Slider */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
              <label htmlFor="align-ang-tol" style={{ color: '#cbd5e1', fontWeight: 500 }}>Angular Lock Tolerance (&theta;tol):</label>
              <span style={{ color: '#34d399', fontWeight: 600 }}>&plusmn;{localConfig.angular_tolerance_deg.toFixed(2)}&deg;</span>
            </div>
            <input
              id="align-ang-tol"
              type="range"
              min="0.05"
              max="2.00"
              step="0.05"
              value={localConfig.angular_tolerance_deg}
              onChange={(e) => handleChange('angular_tolerance_deg', parseFloat(e.target.value))}
              disabled={disabled}
              className="range-slider"
            />
            <span style={{ fontSize: '0.68rem', color: '#64748b' }}>Tight = Precision Tracking / Wide = Fast Lock</span>
          </div>

          {/* Pixel Lock Tolerance Slider */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
              <label htmlFor="align-px-tol" style={{ color: '#cbd5e1', fontWeight: 500 }}>Pixel Lock Radius (pxtol):</label>
              <span style={{ color: '#38bdf8', fontWeight: 600 }}>&le; {localConfig.pixel_tolerance.toFixed(1)} px</span>
            </div>
            <input
              id="align-px-tol"
              type="range"
              min="1.0"
              max="30.0"
              step="0.5"
              value={localConfig.pixel_tolerance}
              onChange={(e) => handleChange('pixel_tolerance', parseFloat(e.target.value))}
              disabled={disabled}
              className="range-slider"
            />
            <span style={{ fontSize: '0.68rem', color: '#64748b' }}>Focal plane radius for pixel-mode lock</span>
          </div>
        </div>

        {/* Toggles & Apply Button */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.05)', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: '#cbd5e1', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={localConfig.use_angular_alignment}
                onChange={(e) => handleChange('use_angular_alignment', e.target.checked)}
                disabled={disabled}
              />
              <span>Use Angular Metric (Degrees)</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: '#cbd5e1', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={localConfig.use_radial_alignment}
                onChange={(e) => handleChange('use_radial_alignment', e.target.checked)}
                disabled={disabled}
              />
              <span>Radial Lock Circle (vs Box)</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: '#cbd5e1', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={localConfig.use_prediction_when_tracking_missing}
                onChange={(e) => handleChange('use_prediction_when_tracking_missing', e.target.checked)}
                disabled={disabled}
              />
              <span>Use Motion Prediction on Dropout</span>
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
            <span>{savedSuccess ? 'Applied!' : saving ? 'Updating...' : 'Apply Tolerances'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
