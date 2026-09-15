import React, { useRef, useEffect, useState } from 'react';
import { Eye, Maximize2, Layers } from 'lucide-react';

export default function WorldPreview({ cameraPlatform, beaconPlatform, geometry }) {
  const [viewMode, setViewMode] = useState('topdown'); // 'topdown' (X-Z) or 'side' (Z-Y)
  const [history, setHistory] = useState([]);

  const camPos = cameraPlatform?.position || { x: 0, y: 0, z: 0 };
  const beaconPos = beaconPlatform?.position || { x: 0, y: 0, z: 50 };

  // Append history trail
  useEffect(() => {
    if (cameraPlatform && beaconPlatform) {
      setHistory((prev) => {
        const next = [...prev, { cam: { ...camPos }, beacon: { ...beaconPos } }];
        if (next.length > 60) next.shift(); // retain last 60 frames of trail
        return next;
      });
    }
  }, [camPos.x, camPos.y, camPos.z, beaconPos.x, beaconPos.y, beaconPos.z]);

  // Compute adaptive view scale
  const maxSpan = Math.max(
    Math.abs(beaconPos.x - camPos.x) * 2,
    Math.abs(beaconPos.z - camPos.z) * 1.3,
    Math.abs(beaconPos.y - camPos.y) * 2,
    30
  );

  const canvasWidth = 520;
  const canvasHeight = 300;
  const centerX = canvasWidth / 2;
  const centerY = canvasHeight / 2 + 60; // offset slightly downwards for forward Z view
  const scale = (canvasHeight * 0.7) / maxSpan;

  // Convert (X, Z) to screen (u, v) for top-down
  const toScreenTopDown = (x, z) => ({
    u: centerX + (x - camPos.x) * scale,
    v: centerY - (z - camPos.z) * scale,
  });

  // Convert (Z, Y) to screen (u, v) for side-view
  const toScreenSide = (y, z) => ({
    u: centerX + (z - camPos.z) * scale * 0.8 - 100,
    v: centerY - (y - camPos.y) * scale,
  });

  const camScreen = viewMode === 'topdown' ? toScreenTopDown(camPos.x, camPos.z) : toScreenSide(camPos.y, camPos.z);
  const beaconScreen = viewMode === 'topdown' ? toScreenTopDown(beaconPos.x, beaconPos.z) : toScreenSide(beaconPos.y, beaconPos.z);

  return (
    <div className="hud-card">
      <div className="card-header">
        <div className="card-title-group">
          <Eye size={18} color="#06b6d4" />
          <h2>2D Tactical Spatial Radar Preview</h2>
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            type="button"
            className={`btn btn-outline ${viewMode === 'topdown' ? 'active-tab' : ''}`}
            style={{
              padding: '3px 8px',
              fontSize: '0.7rem',
              borderColor: viewMode === 'topdown' ? '#22d3ee' : undefined,
              color: viewMode === 'topdown' ? '#22d3ee' : undefined,
            }}
            onClick={() => setViewMode('topdown')}
          >
            TOP-DOWN (X-Z)
          </button>
          <button
            type="button"
            className={`btn btn-outline ${viewMode === 'side' ? 'active-tab' : ''}`}
            style={{
              padding: '3px 8px',
              fontSize: '0.7rem',
              borderColor: viewMode === 'side' ? '#22d3ee' : undefined,
              color: viewMode === 'side' ? '#22d3ee' : undefined,
            }}
            onClick={() => setViewMode('side')}
          >
            SIDE-ELEVATION (Z-Y)
          </button>
        </div>
      </div>
      <div className="card-body" style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {/* SVG Tactical Radar Canvas */}
        <div style={{
          width: '100%',
          height: `${canvasHeight}px`,
          background: 'radial-gradient(circle at center, #0b1528 0%, #020617 100%)',
          borderRadius: '8px',
          border: '1px solid rgba(6, 182, 212, 0.25)',
          position: 'relative',
          overflow: 'hidden',
        }}>
          <svg width="100%" height="100%" viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}>
            {/* Grid Lines & Concentric Distance Rings */}
            <defs>
              <pattern id="radarGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#radarGrid)" />

            {/* Distance Circles from Camera */}
            {[0.25, 0.5, 0.75, 1.0].map((frac, idx) => (
              <circle
                key={idx}
                cx={camScreen.u}
                cy={camScreen.v}
                r={maxSpan * scale * frac}
                fill="none"
                stroke="rgba(6, 182, 212, 0.12)"
                strokeDasharray="3 3"
              />
            ))}

            {/* Center Reference Crosshairs */}
            <line x1={camScreen.u - 18} y1={camScreen.v} x2={camScreen.u + 18} y2={camScreen.v} stroke="rgba(34, 211, 238, 0.4)" strokeWidth="1.5" />
            <line x1={camScreen.u} y1={camScreen.v - 18} x2={camScreen.u} y2={camScreen.v + 18} stroke="rgba(34, 211, 238, 0.4)" strokeWidth="1.5" />

            {/* Past Trajectory Trail */}
            {history.length > 1 && (
              <polyline
                points={history
                  .map((h) => {
                    const pt = viewMode === 'topdown'
                      ? toScreenTopDown(h.beacon.x, h.beacon.z)
                      : toScreenSide(h.beacon.y, h.beacon.z);
                    return `${pt.u},${pt.v}`;
                  })
                  .join(' ')}
                fill="none"
                stroke="rgba(16, 185, 129, 0.35)"
                strokeWidth="2"
                strokeDasharray="2 2"
              />
            )}

            {/* Line of Sight (LOS) Laser Ray */}
            <line
              x1={camScreen.u}
              y1={camScreen.v}
              x2={beaconScreen.u}
              y2={beaconScreen.v}
              stroke="#06b6d4"
              strokeWidth="2"
              strokeDasharray="4 2"
            />

            {/* Camera Platform Point */}
            <g transform={`translate(${camScreen.u}, ${camScreen.v})`}>
              <circle r="8" fill="rgba(6, 182, 212, 0.3)" stroke="#22d3ee" strokeWidth="2" />
              <circle r="3" fill="#22d3ee" />
              <text x="12" y="4" fill="#22d3ee" fontSize="10" fontFamily="var(--font-mono)" fontWeight="700">
                CAMERA (RX)
              </text>
            </g>

            {/* Beacon Platform Point */}
            <g transform={`translate(${beaconScreen.u}, ${beaconScreen.v})`}>
              <circle r="10" fill="rgba(16, 185, 129, 0.25)" stroke="#34d399" strokeWidth="2" />
              <circle r="4" fill="#34d399" />
              <text x="14" y="4" fill="#34d399" fontSize="10" fontFamily="var(--font-mono)" fontWeight="700">
                BEACON (TX)
              </text>
            </g>
          </svg>

          {/* Scale Overlay Badge */}
          <div style={{
            position: 'absolute',
            bottom: '10px',
            left: '12px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.72rem',
            color: '#64748b',
            background: 'rgba(2, 6, 23, 0.7)',
            padding: '2px 8px',
            borderRadius: '4px',
            border: '1px solid rgba(255,255,255,0.06)',
          }}>
            VIEW: {viewMode === 'topdown' ? 'HORIZONTAL (X-Z)' : 'VERTICAL (Z-Y)'} | RANGE: {geometry?.range?.toFixed(1) || 0} m
          </div>
        </div>
      </div>
    </div>
  );
}
