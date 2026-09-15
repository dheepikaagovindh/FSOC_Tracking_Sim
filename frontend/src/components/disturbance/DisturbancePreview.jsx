import React from 'react';
import { Eye, EyeOff, ShieldCheck, Zap, AlertTriangle, Radio } from 'lucide-react';
import { getCameraImageUrl } from '../../services/cameraApi';
import { getDisturbedImageUrl } from '../../services/disturbanceApi';

export default function DisturbancePreview({
  cameraFrame,
  disturbanceFrame,
  imageTimestamp,
  intrinsics,
}) {
  const width = intrinsics?.width || 640;
  const height = intrinsics?.height || 480;
  const cx = intrinsics?.cx ?? width / 2;
  const cy = intrinsics?.cy ?? height / 2;

  const meta = disturbanceFrame?.metadata;
  const isDisturbed = disturbanceFrame?.is_disturbed ?? false;
  const isDropoutActive = meta?.dropout?.active ?? false;
  const isBeaconVisibleInClean = cameraFrame?.visible ?? false;
  const projU = cameraFrame?.projection?.u ?? cx;
  const projV = cameraFrame?.projection?.v ?? cy;

  const vibDx = meta?.vibration?.offset_x ?? 0.0;
  const vibDy = meta?.vibration?.offset_y ?? 0.0;

  return (
    <div className="hud-card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Radio size={18} style={{ color: 'var(--color-primary)' }} />
          <h2 style={{ fontSize: '1rem', margin: 0 }}>OPTICAL OBSERVATION COMPARATIVE VIEWFINDER</h2>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span
            className={`status-pill ${isDropoutActive ? 'status-pill-danger' : isDisturbed ? 'status-pill-warning' : 'status-pill-success'}`}
            style={{ fontSize: '0.72rem', padding: '3px 8px' }}
          >
            {isDropoutActive ? (
              <>
                <AlertTriangle size={12} style={{ marginRight: '4px', verticalAlign: '-1px' }} />
                DROPOUT ACTIVE
              </>
            ) : isDisturbed ? (
              <>
                <Zap size={12} style={{ marginRight: '4px', verticalAlign: '-1px' }} />
                DISTURBANCES ACTIVE ({meta?.applied_effects_count || 0})
              </>
            ) : (
              <>
                <ShieldCheck size={12} style={{ marginRight: '4px', verticalAlign: '-1px' }} />
                CLEAN OBSERVATION
              </>
            )}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
            {width}x{height} | {meta?.severity?.toUpperCase() || 'OFF'}
          </span>
        </div>
      </div>

      {/* Side-by-side Viewports Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
        padding: '16px',
        background: 'rgba(5, 7, 10, 0.6)',
      }}>
        {/* Left Viewport: Clean Synthetic Frame */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 'bold', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
              1. CLEAN SYNTHETIC CAMERA FRAME
            </span>
            <span style={{ fontSize: '0.68rem', color: '#22c55e', background: 'rgba(34, 197, 94, 0.1)', padding: '2px 6px', borderRadius: '4px' }}>
              GROUND TRUTH
            </span>
          </div>

          <div style={{
            position: 'relative',
            width: '100%',
            aspectRatio: `${width} / ${height}`,
            backgroundColor: '#05070a',
            border: '1px solid rgba(0, 229, 255, 0.25)',
            borderRadius: '6px',
            overflow: 'hidden',
          }}>
            <img
              src={getCameraImageUrl(imageTimestamp)}
              alt="Clean Camera Frame"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'contain',
                imageRendering: 'pixelated',
              }}
            />

            {/* HUD Overlay for Clean View */}
            <svg
              viewBox={`0 0 ${width} ${height}`}
              style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}
            >
              {/* Center Crosshairs */}
              <line x1={cx - 15} y1={cy} x2={cx + 15} y2={cy} stroke="rgba(0, 229, 255, 0.5)" strokeWidth="0.8" />
              <line x1={cx} y1={cy - 15} x2={cx} y2={cy + 15} stroke="rgba(0, 229, 255, 0.5)" strokeWidth="0.8" />

              {/* Target Marker in Clean View */}
              {isBeaconVisibleInClean && (
                <g>
                  <circle cx={projU} cy={projV} r="8" fill="none" stroke="#22c55e" strokeWidth="1" strokeDasharray="2,2" />
                  <text x={projU + 12} y={projV - 4} fill="#22c55e" fontSize="9" fontFamily="monospace">
                    [{projU.toFixed(1)}, {projV.toFixed(1)}]
                  </text>
                </g>
              )}
            </svg>

            <div style={{ position: 'absolute', bottom: '6px', left: '8px', fontSize: '0.65rem', color: 'rgba(255,255,255,0.6)', fontFamily: 'var(--font-mono)' }}>
              CLEAN VIEW (t={(cameraFrame?.timestamp || 0).toFixed(2)}s)
            </div>
          </div>
        </div>

        {/* Right Viewport: Disturbed Sensor Observation */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 'bold', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
              2. DISTURBED SENSOR OBSERVATION
            </span>
            <span style={{ fontSize: '0.68rem', color: isDisturbed ? '#f59e0b' : '#38bdf8', background: 'rgba(245, 158, 11, 0.1)', padding: '2px 6px', borderRadius: '4px' }}>
              DETECTOR INPUT
            </span>
          </div>

          <div style={{
            position: 'relative',
            width: '100%',
            aspectRatio: `${width} / ${height}`,
            backgroundColor: '#05070a',
            border: isDropoutActive ? '1px solid #ef4444' : isDisturbed ? '1px solid rgba(245, 158, 11, 0.5)' : '1px solid rgba(0, 229, 255, 0.25)',
            borderRadius: '6px',
            overflow: 'hidden',
          }}>
            <img
              src={getDisturbedImageUrl(imageTimestamp)}
              alt="Disturbed Sensor Observation"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'contain',
                imageRendering: 'pixelated',
              }}
            />

            {/* HUD Overlay for Disturbed View */}
            <svg
              viewBox={`0 0 ${width} ${height}`}
              style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}
            >
              {/* Center Crosshairs */}
              <line x1={cx - 15} y1={cy} x2={cx + 15} y2={cy} stroke="rgba(245, 158, 11, 0.5)" strokeWidth="0.8" />
              <line x1={cx} y1={cy - 15} x2={cx} y2={cy + 15} stroke="rgba(245, 158, 11, 0.5)" strokeWidth="0.8" />

              {/* Vibration Vector Offset Arrow */}
              {meta?.vibration?.applied && (
                <g>
                  <line
                    x1={cx}
                    y1={cy}
                    x2={cx + vibDx * 5}
                    y2={cy + vibDy * 5}
                    stroke="#f59e0b"
                    strokeWidth="1.5"
                  />
                  <circle cx={cx + vibDx * 5} cy={cy + vibDy * 5} r="2" fill="#f59e0b" />
                </g>
              )}

              {/* Dropout Alert Overlay */}
              {isDropoutActive && (
                <g>
                  <rect
                    x={width / 2 - 110}
                    y={height / 2 - 20}
                    width="220"
                    height="40"
                    rx="4"
                    fill="rgba(239, 68, 68, 0.3)"
                    stroke="#ef4444"
                    strokeWidth="1.2"
                  />
                  <text
                    x={width / 2}
                    y={height / 2 + 5}
                    textAnchor="middle"
                    fill="#fca5a5"
                    fontSize="11"
                    fontFamily="monospace"
                    fontWeight="bold"
                  >
                    SIGNAL DEEP FADE / DROPOUT
                  </text>
                </g>
              )}
            </svg>

            <div style={{ position: 'absolute', bottom: '6px', left: '8px', fontSize: '0.65rem', color: isDisturbed ? '#f59e0b' : '#38bdf8', fontFamily: 'var(--font-mono)' }}>
              DISTURBED (N: σ={meta?.noise?.sigma?.toFixed(1) || 0}, B: {meta?.blur?.strength?.toFixed(1) || 0}, V: {meta?.vibration?.magnitude?.toFixed(1) || 0}px)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
