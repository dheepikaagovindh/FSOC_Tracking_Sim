import React, { useState, useRef } from 'react';
import { Crosshair, Eye, EyeOff, AlertTriangle, Maximize2 } from 'lucide-react';
import { getCameraImageUrl } from '../../services/cameraApi';

export default function CameraFocalPlane({ frame, intrinsics, timestamp, imageTimestamp }) {
  const [hoverPos, setHoverPos] = useState(null);
  const containerRef = useRef(null);

  const width = intrinsics?.width || 640;
  const height = intrinsics?.height || 480;
  const cx = intrinsics?.cx ?? width / 2;
  const cy = intrinsics?.cy ?? height / 2;
  const hfov = intrinsics?.hfov_deg || 30.0;
  const vfov = intrinsics?.vfov_deg || 22.5;

  const isVisible = frame?.visible ?? false;
  const projU = frame?.projection?.u ?? cx;
  const projV = frame?.projection?.v ?? cy;
  const visReason = frame?.visibility?.reason || (isVisible ? 'VISIBLE' : 'OUT_OF_FOV');

  // Handle hover on viewport
  const handleMouseMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const scaleX = width / rect.width;
    const scaleY = height / rect.height;
    const x = Math.max(0, Math.min(width, (e.clientX - rect.left) * scaleX));
    const y = Math.max(0, Math.min(height, (e.clientY - rect.top) * scaleY));
    setHoverPos({ u: x.toFixed(1), v: y.toFixed(1) });
  };

  const handleMouseLeave = () => {
    setHoverPos(null);
  };

  return (
    <div className="hud-card" style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Header */}
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Crosshair size={18} style={{ color: 'var(--color-primary)' }} />
          <h2 style={{ fontSize: '1rem', margin: 0 }}>SYNTHETIC OPTICAL FOCAL PLANE</h2>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className={`status-pill ${isVisible ? 'status-pill-success' : 'status-pill-warning'}`} style={{ fontSize: '0.72rem', padding: '3px 8px' }}>
            {isVisible ? <Eye size={12} style={{ marginRight: '4px', verticalAlign: '-1px' }} /> : <EyeOff size={12} style={{ marginRight: '4px', verticalAlign: '-1px' }} />}
            {visReason}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
            {width}x{height} | HFOV: {hfov}° VFOV: {vfov}°
          </span>
        </div>
      </div>

      {/* Optical Sensor Viewport */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{
          position: 'relative',
          width: '100%',
          aspectRatio: `${width} / ${height}`,
          backgroundColor: '#05070a',
          border: '1px solid var(--color-border)',
          borderRadius: '6px',
          overflow: 'hidden',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          cursor: 'crosshair',
          marginTop: '10px',
        }}
      >
        {/* Synthetic Frame Image from Backend */}
        <img
          src={getCameraImageUrl(imageTimestamp || timestamp)}
          alt="Synthetic Optical Sensor View"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            imageRendering: 'pixelated',
          }}
          onError={(e) => {
            // Fallback to dark background if offline
            e.target.style.opacity = 0;
          }}
          onLoad={(e) => {
            e.target.style.opacity = 1;
          }}
        />

        {/* SVG HUD Reticle & Target Crosshairs Overlay */}
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none',
          }}
        >
          <defs>
            {/* Grid Pattern */}
            <pattern id="cam-grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(0, 229, 255, 0.05)" strokeWidth="0.5" />
            </pattern>
          </defs>

          {/* Background Grid */}
          <rect width={width} height={height} fill="url(#cam-grid)" />

          {/* Corner Framing Brackets */}
          <path d="M 10 30 L 10 10 L 30 10" fill="none" stroke="rgba(0, 229, 255, 0.5)" strokeWidth="1.5" />
          <path d={`M ${width - 30} 10 L ${width - 10} 10 L ${width - 10} 30`} fill="none" stroke="rgba(0, 229, 255, 0.5)" strokeWidth="1.5" />
          <path d={`M 10 ${height - 30} L 10 ${height - 10} L 30 ${height - 10}`} fill="none" stroke="rgba(0, 229, 255, 0.5)" strokeWidth="1.5" />
          <path d={`M ${width - 30} ${height - 10} L ${width - 10} ${height - 10} L ${width - 10} ${height - 30}`} fill="none" stroke="rgba(0, 229, 255, 0.5)" strokeWidth="1.5" />

          {/* Optical Boresight Center Crosshairs (cx, cy) */}
          <line x1={cx - 30} y1={cy} x2={cx + 30} y2={cy} stroke="rgba(0, 229, 255, 0.6)" strokeWidth="1" strokeDasharray="3,3" />
          <line x1={cx} y1={cy - 30} x2={cx} y2={cy + 30} stroke="rgba(0, 229, 255, 0.6)" strokeWidth="1" strokeDasharray="3,3" />
          <circle cx={cx} cy={cy} r="4" fill="none" stroke="rgba(0, 229, 255, 0.8)" strokeWidth="1" />
          <circle cx={cx} cy={cy} r="1" fill="rgba(0, 229, 255, 1)" />

          {/* Angular Reticle Rings (Concentric circles around boresight) */}
          <circle cx={cx} cy={cy} r={width * 0.15} fill="none" stroke="rgba(0, 229, 255, 0.12)" strokeWidth="1" strokeDasharray="2,4" />
          <circle cx={cx} cy={cy} r={width * 0.30} fill="none" stroke="rgba(0, 229, 255, 0.12)" strokeWidth="1" strokeDasharray="2,4" />

          {/* Reticle Az/El Axis Indicators */}
          <text x={cx + 35} y={cy + 3} fill="rgba(0, 229, 255, 0.4)" fontSize="8" fontFamily="monospace">+AZ</text>
          <text x={cx - 50} y={cy + 3} fill="rgba(0, 229, 255, 0.4)" fontSize="8" fontFamily="monospace">-AZ</text>
          <text x={cx - 10} y={cy - 35} fill="rgba(0, 229, 255, 0.4)" fontSize="8" fontFamily="monospace">+EL</text>
          <text x={cx - 10} y={cy + 45} fill="rgba(0, 229, 255, 0.4)" fontSize="8" fontFamily="monospace">-EL</text>

          {/* Detected / Projected Beacon Marker */}
          {isVisible && (
            <g>
              {/* Dynamic Target Box around beacon */}
              <rect
                x={projU - 12}
                y={projV - 12}
                width="24"
                height="24"
                fill="rgba(34, 197, 94, 0.08)"
                stroke="#22c55e"
                strokeWidth="1.2"
                strokeDasharray="4,2"
              />
              {/* Target Diamond Marker */}
              <polygon
                points={`${projU},${projV - 6} ${projU + 6},${projV} ${projU},${projV + 6} ${projU - 6},${projV}`}
                fill="none"
                stroke="#22c55e"
                strokeWidth="1"
              />
              {/* Line from Boresight Center to Target (Displacement Vector) */}
              <line
                x1={cx}
                y1={cy}
                x2={projU}
                y2={projV}
                stroke="rgba(34, 197, 94, 0.45)"
                strokeWidth="1"
                strokeDasharray="2,2"
              />
              {/* Coordinate label next to target */}
              <text
                x={Math.min(width - 90, projU + 16)}
                y={Math.max(20, projV - 8)}
                fill="#22c55e"
                fontSize="10"
                fontFamily="monospace"
                fontWeight="bold"
              >
                [{projU.toFixed(1)}, {projV.toFixed(1)}]
              </text>
            </g>
          )}

          {/* Out of FOV or Behind Camera Indicator */}
          {!isVisible && (
            <g>
              <rect
                x={width / 2 - 120}
                y={height / 2 - 25}
                width="240"
                height="50"
                rx="4"
                fill="rgba(239, 68, 68, 0.15)"
                stroke="#ef4444"
                strokeWidth="1"
              />
              <text
                x={width / 2}
                y={height / 2 - 5}
                textAnchor="middle"
                fill="#fca5a5"
                fontSize="12"
                fontFamily="monospace"
                fontWeight="bold"
              >
                BEACON {visReason}
              </text>
              <text
                x={width / 2}
                y={height / 2 + 12}
                textAnchor="middle"
                fill="rgba(252, 165, 165, 0.8)"
                fontSize="9"
                fontFamily="monospace"
              >
                Adjust Gimbal Pan/Tilt to Reacquire
              </text>
            </g>
          )}
        </svg>

        {/* HUD Overlay Labels */}
        <div style={{
          position: 'absolute',
          top: '8px',
          left: '12px',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.72rem',
          color: 'var(--color-primary)',
          textShadow: '0 0 4px rgba(0, 229, 255, 0.5)',
          pointerEvents: 'none',
        }}>
          <div>OPTICAL RECEIVER CAM // SENSOR_01</div>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem' }}>
            t = {(timestamp || 0).toFixed(2)}s
          </div>
        </div>

        {/* Cursor Coordinate Inspection Box */}
        {hoverPos && (
          <div style={{
            position: 'absolute',
            bottom: '8px',
            right: '12px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.72rem',
            background: 'rgba(5, 7, 10, 0.85)',
            border: '1px solid var(--color-border)',
            padding: '2px 8px',
            borderRadius: '4px',
            color: 'var(--color-primary)',
            pointerEvents: 'none',
          }}>
            CURSOR: u={hoverPos.u}, v={hoverPos.v}
          </div>
        )}

        {/* Boresight Center Pill */}
        <div style={{
          position: 'absolute',
          bottom: '8px',
          left: '12px',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.7rem',
          color: 'var(--color-text-muted)',
          pointerEvents: 'none',
        }}>
          BORESIGHT (cx, cy): [{cx.toFixed(1)}, {cy.toFixed(1)}]
        </div>
      </div>
    </div>
  );
}
