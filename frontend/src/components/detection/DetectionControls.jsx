import React, { useState, useEffect } from 'react';
import { Sliders, Cpu, Sparkles, RefreshCw, CheckCircle2, Target } from 'lucide-react';

const ALGORITHMS = [
  {
    id: 'hybrid',
    label: 'Hybrid Multi-Stage',
    desc: 'Adaptive thresholding + localized ROI + intensity CoM + Gaussian sub-pixel peak refinement.',
    tag: 'RECOMMENDED',
  },
  {
    id: 'com',
    label: 'Intensity CoM',
    desc: 'Classic background-subtracted intensity-weighted Center of Mass.',
  },
  {
    id: 'adaptive_threshold',
    label: 'Adaptive Threshold',
    desc: 'Robust dynamic k-sigma statistical thresholding with localized centroiding.',
  },
  {
    id: 'gaussian_fit',
    label: '2D Gaussian Fit',
    desc: 'Log-parabolic Gaussian 3-point analytical sub-pixel peak estimator.',
  },
];

export default function DetectionControls({ config, onUpdateConfig, onReset, disabled }) {
  const [formData, setFormData] = useState({
    algorithm: 'hybrid',
    k_sigma: 3.5,
    min_pnr: 2.5,
    min_flux: 5.0,
    roi_radius: 15,
    subpixel_refinement: true,
  });

  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (config) {
      setFormData({
        algorithm: config.algorithm || 'hybrid',
        k_sigma: config.k_sigma ?? 3.5,
        min_pnr: config.min_pnr ?? 2.5,
        min_flux: config.min_flux ?? 5.0,
        roi_radius: config.roi_radius ?? 15,
        subpixel_refinement: config.subpixel_refinement ?? true,
      });
      setHasChanges(false);
    }
  }, [config]);

  const handleChange = (field, value) => {
    setFormData((prev) => {
      const next = { ...prev, [field]: value };
      setHasChanges(true);
      return next;
    });
  };

  const handleApply = (e) => {
    e.preventDefault();
    onUpdateConfig(formData);
    setHasChanges(false);
  };

  const handleSelectAlgo = (algoId) => {
    handleChange('algorithm', algoId);
    // Instant update
    onUpdateConfig({ ...formData, algorithm: algoId });
    setHasChanges(false);
  };

  return (
    <div className="hud-card" style={{ padding: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Cpu size={18} color="var(--color-primary)" />
          <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, letterSpacing: '0.05em' }}>
            DETECTION ALGORITHM & CENTROIDING CONFIG
          </h3>
        </div>
        <button
          type="button"
          className="btn btn-outline"
          onClick={onReset}
          disabled={disabled}
          style={{ fontSize: '0.72rem', padding: '3px 8px' }}
        >
          <RefreshCw size={12} style={{ marginRight: '4px' }} />
          Reset Defaults
        </button>
      </div>

      <form onSubmit={handleApply}>
        {/* 1. Algorithm Selection Cards */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--color-text-muted)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>
            LOCALIZATION ALGORITHM
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '8px' }}>
            {ALGORITHMS.map((algo) => {
              const active = formData.algorithm === algo.id;
              return (
                <div
                  key={algo.id}
                  onClick={() => !disabled && handleSelectAlgo(algo.id)}
                  style={{
                    padding: '10px 12px',
                    borderRadius: '6px',
                    background: active ? 'rgba(0, 229, 255, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                    border: active ? '1px solid var(--color-primary)' : '1px solid var(--color-border)',
                    cursor: disabled ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <span style={{ fontSize: '0.82rem', fontWeight: 600, color: active ? 'var(--color-primary)' : 'var(--color-text)' }}>
                      {algo.label}
                    </span>
                    {algo.tag && (
                      <span style={{
                        fontSize: '0.62rem',
                        padding: '1px 5px',
                        borderRadius: '3px',
                        background: 'rgba(16, 185, 129, 0.2)',
                        color: '#34d399',
                        fontWeight: 600,
                      }}>
                        {algo.tag}
                      </span>
                    )}
                  </div>
                  <p style={{ margin: 0, fontSize: '0.70rem', color: 'var(--color-text-muted)', lineHeight: 1.3 }}>
                    {algo.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* 2. Numerical Parameter Sliders */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
          {/* k-sigma multiplier */}
          <div className="control-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <label style={{ fontSize: '0.76rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                Adaptive Multiplier (k·σ)
              </label>
              <span style={{ fontSize: '0.76rem', color: 'var(--color-primary)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                {formData.k_sigma.toFixed(1)}σ
              </span>
            </div>
            <input
              type="range"
              min="1.0"
              max="10.0"
              step="0.1"
              value={formData.k_sigma}
              onChange={(e) => handleChange('k_sigma', parseFloat(e.target.value))}
              disabled={disabled}
              style={{ width: '100%' }}
            />
            <span style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
              Segmentation threshold: T = μ_bg + k·σ_bg
            </span>
          </div>

          {/* min PNR */}
          <div className="control-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <label style={{ fontSize: '0.76rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                Minimum PNR Floor
              </label>
              <span style={{ fontSize: '0.76rem', color: 'var(--color-primary)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                {formData.min_pnr.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="1.0"
              max="15.0"
              step="0.1"
              value={formData.min_pnr}
              onChange={(e) => handleChange('min_pnr', parseFloat(e.target.value))}
              disabled={disabled}
              style={{ width: '100%' }}
            />
            <span style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
              Peak-to-Noise Ratio: (I_max - μ_bg) / σ_bg
            </span>
          </div>

          {/* ROI Radius */}
          <div className="control-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <label style={{ fontSize: '0.76rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                Localized ROI Radius
              </label>
              <span style={{ fontSize: '0.76rem', color: 'var(--color-primary)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                {formData.roi_radius} px ({2 * formData.roi_radius + 1}×{2 * formData.roi_radius + 1})
              </span>
            </div>
            <input
              type="range"
              min="5"
              max="40"
              step="1"
              value={formData.roi_radius}
              onChange={(e) => handleChange('roi_radius', parseInt(e.target.value, 10))}
              disabled={disabled}
              style={{ width: '100%' }}
            />
            <span style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
              Sub-window footprint centered on brightest peak
            </span>
          </div>

          {/* Min Spot Flux */}
          <div className="control-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <label style={{ fontSize: '0.76rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                Minimum Spot Flux
              </label>
              <span style={{ fontSize: '0.76rem', color: 'var(--color-primary)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                {formData.min_flux.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="1.0"
              max="30.0"
              step="0.5"
              value={formData.min_flux}
              onChange={(e) => handleChange('min_flux', parseFloat(e.target.value))}
              disabled={disabled}
              style={{ width: '100%' }}
            />
            <span style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
              Integrated energy sum above threshold
            </span>
          </div>
        </div>

        {/* 3. Sub-Pixel Gaussian Refinement Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)', marginBottom: '14px' }}>
          <div>
            <div style={{ fontSize: '0.80rem', fontWeight: 600 }}>Sub-Pixel Gaussian Peak Refinement</div>
            <div style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)' }}>
              Enable 2D parabolic / log-Gaussian sub-pixel interpolation on spot peak
            </div>
          </div>
          <label className="switch" style={{ cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={formData.subpixel_refinement}
              onChange={(e) => handleChange('subpixel_refinement', e.target.checked)}
              disabled={disabled}
            />
            <span className="slider round"></span>
          </label>
        </div>

        {/* Apply Button */}
        {hasChanges && (
          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center' }}
            disabled={disabled}
          >
            <CheckCircle2 size={14} style={{ marginRight: '6px' }} />
            Apply Detection Parameters
          </button>
        )}
      </form>
    </div>
  );
}
