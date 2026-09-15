import React, { useState } from 'react';
import { Eye, EyeOff, Layers, Maximize2, Minimize2, Radio, Crosshair } from 'lucide-react';
import { getTrackingOverlayUrl } from '../../services/trackingApi';

export default function TrackingOverlay({ telemetry, result, isRunning, cacheBust }) {
  const [showMeasured, setShowMeasured] = useState(true);
  const [showFiltered, setShowFiltered] = useState(true);
  const [showPredicted, setShowPredicted] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);

  const overlayUrl = getTrackingOverlayUrl(cacheBust);

  return (
    <div className={`card tracking-viewfinder-card ${isExpanded ? 'viewfinder-fullscreen' : ''}`} style={{ marginBottom: '1.25rem' }}>
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Radio size={18} className={isRunning ? 'text-emerald-400 animate-pulse' : 'text-cyan-400'} />
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>LIVE TRACKING HUD & MOTION VIEWFINDER</h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {/* Layer toggles */}
          <div style={{ display: 'flex', gap: '0.25rem', background: 'rgba(0,0,0,0.3)', padding: '2px', borderRadius: '4px' }}>
            <button
              type="button"
              className={`btn btn-icon ${showMeasured ? 'active-layer' : ''}`}
              style={{
                fontSize: '0.7rem',
                padding: '3px 8px',
                color: showMeasured ? '#22d3ee' : '#64748b',
                border: '1px solid',
                borderColor: showMeasured ? '#06b6d4' : 'transparent',
                background: showMeasured ? 'rgba(6,182,212,0.1)' : 'transparent',
                borderRadius: '3px',
              }}
              onClick={() => setShowMeasured(!showMeasured)}
              title="Toggle Detector Measurement Layer"
            >
              Measured (Cyan)
            </button>

            <button
              type="button"
              className={`btn btn-icon ${showFiltered ? 'active-layer' : ''}`}
              style={{
                fontSize: '0.7rem',
                padding: '3px 8px',
                color: showFiltered ? '#34d399' : '#64748b',
                border: '1px solid',
                borderColor: showFiltered ? '#10b981' : 'transparent',
                background: showFiltered ? 'rgba(16,185,129,0.1)' : 'transparent',
                borderRadius: '3px',
              }}
              onClick={() => setShowFiltered(!showFiltered)}
              title="Toggle Filtered State Layer"
            >
              Filtered (Lime)
            </button>

            <button
              type="button"
              className={`btn btn-icon ${showPredicted ? 'active-layer' : ''}`}
              style={{
                fontSize: '0.7rem',
                padding: '3px 8px',
                color: showPredicted ? '#fbbf24' : '#64748b',
                border: '1px solid',
                borderColor: showPredicted ? '#f59e0b' : 'transparent',
                background: showPredicted ? 'rgba(245,158,11,0.1)' : 'transparent',
                borderRadius: '3px',
              }}
              onClick={() => setShowPredicted(!showPredicted)}
              title="Toggle Lead Predicted Layer"
            >
              Predicted (Amber)
            </button>
          </div>

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
            alt="Tracking HUD Stream"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              display: 'block',
            }}
          />

          {/* HUD Target Overlay Coordinate Tooltip */}
          {result?.tracking && result?.position_x !== null && (
            <div
              style={{
                position: 'absolute',
                top: '28px',
                left: '8px',
                background: 'rgba(3, 7, 18, 0.85)',
                border: '1px solid rgba(16, 185, 129, 0.4)',
                borderRadius: '4px',
                padding: '4px 8px',
                fontSize: '0.72rem',
                color: '#34d399',
                fontFamily: 'monospace',
                pointerEvents: 'none',
              }}
            >
              <div>KF EST: ({result.position_x.toFixed(1)}, {result.position_y.toFixed(1)}) px</div>
              <div>VEL: ({result.velocity_x?.toFixed(1) || 0}, {result.velocity_y?.toFixed(1) || 0}) px/s</div>
              <div>CONF: {Math.round((result.confidence || 0) * 100)}%</div>
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
            FOV: 30&deg; x 22.5&deg; | 640x480
          </div>
        </div>
      </div>
    </div>
  );
}
