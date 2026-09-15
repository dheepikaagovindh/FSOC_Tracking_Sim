import React, { useState } from 'react';
import { Eye, EyeOff, Maximize2, Minimize2, Radio, Crosshair, Target } from 'lucide-react';
import { getErrorOverlayUrl } from '../../services/errorApi';

export default function AlignmentOverlay({ telemetry, result, isRunning, cacheBust }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const overlayUrl = getErrorOverlayUrl(cacheBust);

  const valid = result?.valid ?? false;
  const isAligned = result?.aligned ?? false;
  const ex = result?.pixel_error_x ?? 0;
  const ey = result?.pixel_error_y ?? 0;
  const angMag = result?.angular_error_magnitude_deg ?? 0;

  return (
    <div className={`card alignment-viewfinder-card ${isExpanded ? 'viewfinder-fullscreen' : ''}`} style={{ marginBottom: '1.25rem' }}>
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Radio size={18} className={isRunning ? 'text-emerald-400 animate-pulse' : 'text-cyan-400'} />
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>BORESIGHT ALIGNMENT VIEWFINDER & ERROR VECTOR</h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span
            style={{
              fontSize: '0.72rem',
              padding: '3px 8px',
              borderRadius: '4px',
              background: isAligned ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)',
              color: isAligned ? '#34d399' : '#fbbf24',
              border: `1px solid ${isAligned ? '#10b981' : '#f59e0b'}44`,
              fontWeight: 600,
            }}
          >
            {isAligned ? 'LOCKED ON AXIS' : 'OFFSET VECTOR ACTIVE'}
          </span>

          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '4px 8px' }}
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? 'Minimize View' : 'Expand View'}
          >
            {isExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
      </div>

      <div
        className="card-body viewfinder-viewport-container"
        style={{
          position: 'relative',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: '#030712',
          padding: '0.5rem',
          borderRadius: '6px',
          overflow: 'hidden',
          minHeight: '360px',
        }}
      >
        <div style={{ position: 'relative', width: '100%', maxWidth: '640px', aspectRatio: '4/3', borderRadius: '4px', overflow: 'hidden', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <img
            src={overlayUrl}
            alt="Alignment HUD Stream"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              display: 'block',
            }}
          />

          {/* HUD Target Alignment Coordinate Tooltip */}
          {valid && (
            <div
              style={{
                position: 'absolute',
                top: '28px',
                left: '8px',
                background: 'rgba(3, 7, 18, 0.85)',
                border: `1px solid ${isAligned ? '#10b981' : '#f59e0b'}66`,
                borderRadius: '4px',
                padding: '4px 8px',
                fontSize: '0.72rem',
                color: isAligned ? '#34d399' : '#fbbf24',
                fontFamily: 'monospace',
                pointerEvents: 'none',
              }}
            >
              <div>BORESIGHT: (320, 240) px</div>
              <div>OFFSET: &Delta;X={ex > 0 ? '+' : ''}{ex.toFixed(1)} &Delta;Y={ey > 0 ? '+' : ''}{ey.toFixed(1)} px</div>
              <div>ANGULAR: {angMag.toFixed(2)}&deg; ({isAligned ? 'ALIGNED' : 'MISALIGNED'})</div>
            </div>
          )}

          {/* Status Indicator Pill */}
          <div
            style={{
              position: 'absolute',
              top: '28px',
              right: '8px',
              background: 'rgba(3, 7, 18, 0.85)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '4px',
              padding: '3px 8px',
              fontSize: '0.7rem',
              color: '#94a3b8',
              fontFamily: 'monospace',
              pointerEvents: 'none',
            }}
          >
            OPTICAL AXIS | 640x480
          </div>
        </div>
      </div>
    </div>
  );
}
