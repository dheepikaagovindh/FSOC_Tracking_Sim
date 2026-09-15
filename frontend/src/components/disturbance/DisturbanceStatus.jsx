import React from 'react';
import { Activity, Shield, AlertTriangle, Disc, Wind, Zap } from 'lucide-react';

export default function DisturbanceStatus({ telemetry, status }) {
  const isDropoutActive = telemetry?.dropout_active ?? false;
  const sev = telemetry?.severity || status?.severity || 'off';

  return (
    <div className="hud-card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={18} style={{ color: 'var(--color-primary)' }} />
          <h2 style={{ fontSize: '1rem', margin: 0 }}>DISTURBANCE TELEMETRY & DIAGNOSTICS</h2>
        </div>
        <span
          className={`status-pill ${sev === 'off' ? 'status-pill-success' : sev === 'high' ? 'status-pill-danger' : 'status-pill-warning'}`}
          style={{ fontSize: '0.72rem', padding: '3px 8px' }}
        >
          SEVERITY: {sev.toUpperCase()}
        </span>
      </div>

      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {/* Real-time Diagnostics Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          {/* Noise Diagnostics */}
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-primary)', fontSize: '0.72rem', fontWeight: 'bold', marginBottom: '4px' }}>
              SENSOR NOISE
            </div>
            <div style={{ fontSize: '0.85rem', fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>
              σ = {(telemetry?.noise_sigma || 0.0).toFixed(1)} / 255
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', marginTop: '2px' }}>
              Additive Gaussian
            </div>
          </div>

          {/* Blur Diagnostics */}
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-primary)', fontSize: '0.72rem', fontWeight: 'bold', marginBottom: '4px' }}>
              OPTICAL BLUR
            </div>
            <div style={{ fontSize: '0.85rem', fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>
              Strength = {(telemetry?.blur_strength || 0.0).toFixed(1)}
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', marginTop: '2px' }}>
              PSF Convolution
            </div>
          </div>

          {/* Vibration Diagnostics */}
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-primary)', fontSize: '0.72rem', fontWeight: 'bold', marginBottom: '4px' }}>
              IMAGE JITTER OFFSET
            </div>
            <div style={{ fontSize: '0.82rem', fontFamily: 'var(--font-mono)', color: '#fbbf24' }}>
              dx: {(telemetry?.vibration_offset_x || 0.0).toFixed(2)} px
            </div>
            <div style={{ fontSize: '0.82rem', fontFamily: 'var(--font-mono)', color: '#fbbf24' }}>
              dy: {(telemetry?.vibration_offset_y || 0.0).toFixed(2)} px
            </div>
          </div>

          {/* Dropout Diagnostics */}
          <div style={{
            background: isDropoutActive ? 'rgba(239, 68, 68, 0.15)' : 'rgba(15, 23, 42, 0.5)',
            border: isDropoutActive ? '1px solid #ef4444' : '1px solid var(--color-border)',
            padding: '10px 12px',
            borderRadius: '6px',
          }}>
            <div style={{ color: isDropoutActive ? '#fca5a5' : 'var(--color-primary)', fontSize: '0.72rem', fontWeight: 'bold', marginBottom: '4px' }}>
              DROPOUT STATUS
            </div>
            <div style={{ fontSize: '0.82rem', fontFamily: 'var(--font-mono)', color: isDropoutActive ? '#f87171' : '#34d399', fontWeight: 'bold' }}>
              {isDropoutActive ? 'BEACON OCCLUDED' : 'SIGNAL NOMINAL'}
            </div>
            {isDropoutActive && (
              <div style={{ fontSize: '0.68rem', color: '#fca5a5', marginTop: '2px' }}>
                Remaining: {(telemetry?.dropout_remaining_duration || 0.0).toFixed(2)}s
              </div>
            )}
          </div>
        </div>

        {/* Frame & Seed Info */}
        <div style={{
          background: 'rgba(2, 6, 23, 0.6)',
          padding: '8px 12px',
          borderRadius: '4px',
          border: '1px solid var(--color-border)',
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.72rem',
          fontFamily: 'var(--font-mono)',
          color: 'var(--color-text-muted)',
        }}>
          <span>FRAME: #{telemetry?.frame_index ?? 0}</span>
          <span>TIME: {(telemetry?.timestamp ?? 0.0).toFixed(2)}s</span>
          <span>DETERMINISTIC: TRUE</span>
        </div>
      </div>
    </div>
  );
}
