import React from 'react';
import { Compass, RotateCcw, Target, ChevronLeft, ChevronRight, ChevronUp, ChevronDown } from 'lucide-react';

export default function GimbalManualControl({
  panDeg = 0.0,
  tiltDeg = 0.0,
  onPoseChange,
  onResetPose,
  onAutoCenter,
  disabled = false,
}) {
  // Nudge helper
  const handleNudgePan = (delta) => {
    const newPan = Math.max(-180, Math.min(180, (panDeg || 0) + delta));
    onPoseChange(newPan, tiltDeg);
  };

  const handleNudgeTilt = (delta) => {
    const newTilt = Math.max(-90, Math.min(90, (tiltDeg || 0) + delta));
    onPoseChange(panDeg, newTilt);
  };

  return (
    <div className="hud-card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Compass size={18} style={{ color: 'var(--color-primary)' }} />
          <h2 style={{ fontSize: '1rem', margin: 0 }}>GIMBAL PAN-TILT MANUAL STEERING</h2>
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          {onAutoCenter && (
            <button
              type="button"
              className="btn btn-outline"
              onClick={onAutoCenter}
              disabled={disabled}
              style={{ fontSize: '0.72rem', padding: '4px 8px', color: '#22c55e', borderColor: 'rgba(34, 197, 94, 0.4)' }}
              title="Auto-calculate line-of-sight bearing and center boresight onto beacon"
            >
              <Target size={12} style={{ marginRight: '4px' }} />
              AUTO-CENTER
            </button>
          )}
          <button
            type="button"
            className="btn btn-outline"
            onClick={onResetPose}
            disabled={disabled}
            style={{ fontSize: '0.72rem', padding: '4px 8px' }}
            title="Reset gimbal to initial scenario orientation"
          >
            <RotateCcw size={12} style={{ marginRight: '4px' }} />
            RESET
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '12px' }}>
        {/* Pan Axis Control */}
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 'bold', color: 'var(--color-text-main)' }}>
              PAN (AZIMUTH)
            </span>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.9rem',
              color: 'var(--color-primary)',
              background: 'rgba(0, 229, 255, 0.1)',
              padding: '2px 6px',
              borderRadius: '4px',
            }}>
              {(panDeg || 0).toFixed(2)}°
            </span>
          </div>

          <input
            type="range"
            min="-180"
            max="180"
            step="0.1"
            value={panDeg || 0}
            onChange={(e) => onPoseChange(parseFloat(e.target.value), tiltDeg)}
            disabled={disabled}
            style={{ width: '100%', accentColor: 'var(--color-primary)' }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--color-text-muted)', marginTop: '2px', fontFamily: 'var(--font-mono)' }}>
            <span>-180° (Left)</span>
            <span>0° (Center)</span>
            <span>+180° (Right)</span>
          </div>

          {/* Pan Nudge Buttons */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '4px', marginTop: '10px' }}>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgePan(-5.0)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              -5°
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgePan(-1.0)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              -1°
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgePan(-0.2)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              -0.2°
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgePan(0.2)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              +0.2°
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgePan(1.0)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              +1°
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgePan(5.0)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              +5°
            </button>
          </div>
        </div>

        {/* Tilt Axis Control */}
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 'bold', color: 'var(--color-text-main)' }}>
              TILT (ELEVATION)
            </span>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.9rem',
              color: 'var(--color-primary)',
              background: 'rgba(0, 229, 255, 0.1)',
              padding: '2px 6px',
              borderRadius: '4px',
            }}>
              {(tiltDeg || 0).toFixed(2)}°
            </span>
          </div>

          <input
            type="range"
            min="-90"
            max="90"
            step="0.1"
            value={tiltDeg || 0}
            onChange={(e) => onPoseChange(panDeg, parseFloat(e.target.value))}
            disabled={disabled}
            style={{ width: '100%', accentColor: 'var(--color-primary)' }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--color-text-muted)', marginTop: '2px', fontFamily: 'var(--font-mono)' }}>
            <span>-90° (Down)</span>
            <span>0° (Horizon)</span>
            <span>+90° (Up)</span>
          </div>

          {/* Tilt Nudge Buttons */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '4px', marginTop: '10px' }}>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgeTilt(-5.0)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              -5°
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgeTilt(-1.0)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              -1°
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgeTilt(-0.2)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              -0.2°
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgeTilt(0.2)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              +0.2°
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgeTilt(1.0)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              +1°
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => handleNudgeTilt(5.0)}
              disabled={disabled}
              style={{ fontSize: '0.68rem', padding: '3px 6px' }}
            >
              +5°
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
