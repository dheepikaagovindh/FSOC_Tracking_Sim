import React, { useState, useEffect } from 'react';
import { Sliders, RotateCcw, Check, Zap, Activity, EyeOff, Wind } from 'lucide-react';

export default function DisturbanceControls({
  config,
  onUpdateConfig,
  onReset,
  disabled = false,
}) {
  const [localConfig, setLocalConfig] = useState({
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
  });

  useEffect(() => {
    if (config) {
      setLocalConfig({
        severity: config.severity || 'off',
        vibration_enabled: !!config.vibration_enabled,
        vibration_magnitude: config.vibration_magnitude ?? 0.0,
        noise_enabled: !!config.noise_enabled,
        noise_magnitude: config.noise_magnitude ?? 0.0,
        blur_enabled: !!config.blur_enabled,
        blur_strength: config.blur_strength ?? 0.0,
        dropout_enabled: !!config.dropout_enabled,
        dropout_probability: config.dropout_probability ?? 0.0,
        dropout_duration: config.dropout_duration ?? 0.0,
      });
    }
  }, [config]);

  const handleSeveritySelect = (sev) => {
    let updated = { ...localConfig, severity: sev };
    if (sev === 'off') {
      updated = {
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
    } else if (sev === 'low') {
      updated = {
        severity: 'low',
        vibration_enabled: true,
        vibration_magnitude: 1.0,
        noise_enabled: true,
        noise_magnitude: 0.05,
        blur_enabled: true,
        blur_strength: 1.0,
        dropout_enabled: true,
        dropout_probability: 0.05,
        dropout_duration: 0.2,
      };
    } else if (sev === 'medium') {
      updated = {
        severity: 'medium',
        vibration_enabled: true,
        vibration_magnitude: 3.0,
        noise_enabled: true,
        noise_magnitude: 0.12,
        blur_enabled: true,
        blur_strength: 2.0,
        dropout_enabled: true,
        dropout_probability: 0.15,
        dropout_duration: 0.4,
      };
    } else if (sev === 'high') {
      updated = {
        severity: 'high',
        vibration_enabled: true,
        vibration_magnitude: 6.0,
        noise_enabled: true,
        noise_magnitude: 0.25,
        blur_enabled: true,
        blur_strength: 3.5,
        dropout_enabled: true,
        dropout_probability: 0.30,
        dropout_duration: 0.6,
      };
    }
    setLocalConfig(updated);
    onUpdateConfig(updated);
  };

  const handleChange = (field, value) => {
    const updated = { ...localConfig, [field]: value };
    setLocalConfig(updated);
    onUpdateConfig(updated);
  };

  return (
    <div className="hud-card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sliders size={18} style={{ color: 'var(--color-primary)' }} />
          <h2 style={{ fontSize: '1rem', margin: 0 }}>DISTURBANCE PARAMETER CONFIGURATOR</h2>
        </div>
        <button
          type="button"
          className="btn btn-outline"
          onClick={onReset}
          disabled={disabled}
          style={{ fontSize: '0.72rem', padding: '4px 8px' }}
        >
          <RotateCcw size={12} style={{ marginRight: '4px' }} />
          RESET TO ZERO
        </button>
      </div>

      <div style={{ padding: '16px' }}>
        {/* Master Severity Level Buttons */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--color-text-muted)', marginBottom: '8px', fontWeight: 'bold' }}>
            MASTER SEVERITY PRESET
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
            {[
              { id: 'off', name: 'OFF', color: 'var(--text-secondary)' },
              { id: 'low', name: 'LOW', color: '#34d399' },
              { id: 'medium', name: 'MEDIUM', color: '#fbbf24' },
              { id: 'high', name: 'HIGH', color: '#f87171' },
            ].map((sev) => {
              const isSelected = localConfig.severity.toLowerCase() === sev.id;
              return (
                <button
                  key={sev.id}
                  type="button"
                  className={`btn btn-outline ${isSelected ? 'btn-active' : ''}`}
                  onClick={() => handleSeveritySelect(sev.id)}
                  disabled={disabled}
                  style={{
                    padding: '8px',
                    fontSize: '0.8rem',
                    fontWeight: 'bold',
                    borderColor: isSelected ? sev.color : 'var(--color-border)',
                    background: isSelected ? 'rgba(0, 229, 255, 0.15)' : 'rgba(15, 23, 42, 0.6)',
                    color: isSelected ? '#ffffff' : 'var(--color-text-muted)',
                  }}
                >
                  {sev.name}
                </button>
              );
            })}
          </div>
        </div>

        {/* 4 Fine Parameter Cards Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          {/* 1. Platform Vibration / Image Jitter */}
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Wind size={14} style={{ color: 'var(--color-primary)' }} />
                <span style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>PLATFORM JITTER</span>
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', fontSize: '0.72rem' }}>
                <input
                  type="checkbox"
                  checked={localConfig.vibration_enabled}
                  onChange={(e) => handleChange('vibration_enabled', e.target.checked)}
                  disabled={disabled}
                />
                <span>ENABLE</span>
              </label>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
              <span>Magnitude:</span>
              <span style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{localConfig.vibration_magnitude.toFixed(1)} px</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="15.0"
              step="0.5"
              value={localConfig.vibration_magnitude}
              onChange={(e) => handleChange('vibration_magnitude', parseFloat(e.target.value))}
              disabled={disabled || !localConfig.vibration_enabled}
              style={{ width: '100%', accentColor: 'var(--color-primary)' }}
            />
          </div>

          {/* 2. Optical & Atmospheric Blur */}
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Activity size={14} style={{ color: 'var(--color-primary)' }} />
                <span style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>OPTICAL BLUR</span>
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', fontSize: '0.72rem' }}>
                <input
                  type="checkbox"
                  checked={localConfig.blur_enabled}
                  onChange={(e) => handleChange('blur_enabled', e.target.checked)}
                  disabled={disabled}
                />
                <span>ENABLE</span>
              </label>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
              <span>Strength / Sigma:</span>
              <span style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{localConfig.blur_strength.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="10.0"
              step="0.5"
              value={localConfig.blur_strength}
              onChange={(e) => handleChange('blur_strength', parseFloat(e.target.value))}
              disabled={disabled || !localConfig.blur_enabled}
              style={{ width: '100%', accentColor: 'var(--color-primary)' }}
            />
          </div>

          {/* 3. Sensor Noise */}
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Zap size={14} style={{ color: 'var(--color-primary)' }} />
                <span style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>SENSOR NOISE</span>
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', fontSize: '0.72rem' }}>
                <input
                  type="checkbox"
                  checked={localConfig.noise_enabled}
                  onChange={(e) => handleChange('noise_enabled', e.target.checked)}
                  disabled={disabled}
                />
                <span>ENABLE</span>
              </label>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
              <span>Noise Magnitude:</span>
              <span style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{localConfig.noise_magnitude.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="0.5"
              step="0.01"
              value={localConfig.noise_magnitude}
              onChange={(e) => handleChange('noise_magnitude', parseFloat(e.target.value))}
              disabled={disabled || !localConfig.noise_enabled}
              style={{ width: '100%', accentColor: 'var(--color-primary)' }}
            />
          </div>

          {/* 4. Beacon Dropout / Fades */}
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <EyeOff size={14} style={{ color: 'var(--color-primary)' }} />
                <span style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>BEACON DROPOUT</span>
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', fontSize: '0.72rem' }}>
                <input
                  type="checkbox"
                  checked={localConfig.dropout_enabled}
                  onChange={(e) => handleChange('dropout_enabled', e.target.checked)}
                  disabled={disabled}
                />
                <span>ENABLE</span>
              </label>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
              <span>Probability:</span>
              <span style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{(localConfig.dropout_probability * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={localConfig.dropout_probability}
              onChange={(e) => handleChange('dropout_probability', parseFloat(e.target.value))}
              disabled={disabled || !localConfig.dropout_enabled}
              style={{ width: '100%', accentColor: 'var(--color-primary)' }}
            />

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '6px', fontSize: '0.72rem' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Duration:</span>
              <input
                type="number"
                min="0.0"
                max="5.0"
                step="0.1"
                value={localConfig.dropout_duration}
                onChange={(e) => handleChange('dropout_duration', parseFloat(e.target.value) || 0.0)}
                disabled={disabled || !localConfig.dropout_enabled}
                style={{
                  width: '65px',
                  background: '#020617',
                  border: '1px solid var(--color-border)',
                  color: '#ffffff',
                  fontSize: '0.75rem',
                  fontFamily: 'var(--font-mono)',
                  padding: '2px 4px',
                  borderRadius: '4px',
                  textAlign: 'right',
                }}
              />
              <span style={{ color: 'var(--color-text-muted)' }}>sec</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
