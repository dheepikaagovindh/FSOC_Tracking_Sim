import React, { useState } from 'react';
import { Target, Crosshair, Eye, ShieldCheck, AlertTriangle, Layers, Maximize2 } from 'lucide-react';
import { getAnnotatedImageUrl } from '../../services/detectionApi';
import { getDisturbedImageUrl } from '../../services/disturbanceApi';

export default function DetectionViewfinder({
  detectionResult,
  detectionTelemetry,
  disturbanceFrame,
  imageTimestamp,
  intrinsics,
}) {
  const [showOverlays, setShowOverlays] = useState(true);
  const [showGroundTruth, setShowGroundTruth] = useState(true);
  const [showRawSensor, setShowRawSensor] = useState(false);
  const [isZoomed, setIsZoomed] = useState(false);

  const detected = detectionResult?.detected || false;
  const metrics = detectionResult?.metrics;
  const error = detectionResult?.error;
  const bbox = detectionResult?.bbox;

  const width = disturbanceFrame?.width || 640;
  const height = disturbanceFrame?.height || 480;

  const imageUrl = showRawSensor
    ? getDisturbedImageUrl(imageTimestamp)
    : getAnnotatedImageUrl(imageTimestamp);

  return (
    <div className="hud-card" style={{ padding: '16px', position: 'relative' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Target size={18} color="var(--color-primary)" />
          <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, letterSpacing: '0.05em' }}>
            OPTICAL BEACON ACQUISITION VIEWFINDER
          </h3>
        </div>

        {/* Status Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {detected ? (
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '4px 10px',
              borderRadius: '20px',
              background: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.5)',
              color: '#34d399',
              fontSize: '0.75rem',
              fontWeight: 600,
              fontFamily: 'var(--font-mono)',
            }}>
              <ShieldCheck size={13} />
              BEACON ACQUIRED
            </span>
          ) : (
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '4px 10px',
              borderRadius: '20px',
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.5)',
              color: '#f87171',
              fontSize: '0.75rem',
              fontWeight: 600,
              fontFamily: 'var(--font-mono)',
            }}>
              <AlertTriangle size={13} />
              TARGET LOST / OCCLUDED
            </span>
          )}
        </div>
      </div>

      {/* Main Viewfinder Frame */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          aspectRatio: `${width} / ${height}`,
          background: '#040711',
          borderRadius: '8px',
          overflow: 'hidden',
          border: detected ? '1px solid rgba(0, 229, 255, 0.4)' : '1px solid rgba(239, 68, 68, 0.4)',
          boxShadow: detected ? '0 0 20px rgba(0, 229, 255, 0.1)' : '0 0 20px rgba(239, 68, 68, 0.1)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          transform: isZoomed ? 'scale(1.3)' : 'scale(1)',
          transformOrigin: detectionResult?.u && detectionResult?.v
            ? `${(detectionResult.u / width) * 100}% ${(detectionResult.v / height) * 100}%`
            : 'center center',
          transition: 'transform 0.3s ease-in-out',
        }}
      >
        {/* Optical Sensor Image */}
        <img
          src={imageUrl}
          alt="Beacon Centroid Viewfinder"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            display: 'block',
            imageRendering: 'pixelated',
          }}
          onError={(e) => {
            e.target.style.display = 'none';
          }}
        />

        {/* Dynamic SVG Reticle Overlay (if showOverlays is enabled) */}
        {showOverlays && (
          <svg
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              pointerEvents: 'none',
            }}
            viewBox={`0 0 ${width} ${height}`}
          >
            {/* Corner Tech Brackets */}
            <path
              d={`M 15 30 L 15 15 L 30 15  M ${width - 30} 15 L ${width - 15} 15 L ${width - 15} 30  M 15 ${height - 30} L 15 ${height - 15} L 30 ${height - 15}  M ${width - 30} ${height - 15} L ${width - 15} ${height - 15} L ${width - 15} ${height - 30}`}
              stroke="rgba(0, 229, 255, 0.3)"
              strokeWidth="2"
              fill="none"
            />

            {/* Boresight Crosshair at optical center */}
            <circle cx={width / 2} cy={height / 2} r="4" stroke="rgba(255,255,255,0.25)" fill="none" strokeWidth="1" />
            <line x1={width / 2 - 12} y1={height / 2} x2={width / 2 + 12} y2={height / 2} stroke="rgba(255,255,255,0.25)" strokeWidth="1" />
            <line x1={width / 2} y1={height / 2 - 12} x2={width / 2} y2={height / 2 + 12} stroke="rgba(255,255,255,0.25)" strokeWidth="1" />

            {/* If beacon is detected, draw dynamic animated HUD ring */}
            {detected && detectionResult?.u != null && detectionResult?.v != null && (
              <g>
                {/* Bounding Box */}
                {bbox && (
                  <rect
                    x={bbox.x_min}
                    y={bbox.y_min}
                    width={bbox.width}
                    height={bbox.height}
                    fill="none"
                    stroke="#00e5ff"
                    strokeWidth="1"
                    strokeDasharray="3 2"
                  />
                )}

                {/* Sub-Pixel Target Reticle */}
                <circle
                  cx={detectionResult.u}
                  cy={detectionResult.v}
                  r="12"
                  stroke="#10b981"
                  strokeWidth="2"
                  fill="none"
                />
                <circle
                  cx={detectionResult.u}
                  cy={detectionResult.v}
                  r="3"
                  fill="#00e5ff"
                />

                {/* Ground Truth Diamond & Displacement Vector */}
                {showGroundTruth && error?.has_ground_truth && error.true_u != null && error.true_v != null && (
                  <g>
                    {/* Error vector line */}
                    <line
                      x1={detectionResult.u}
                      y1={detectionResult.v}
                      x2={error.true_u}
                      y2={error.true_v}
                      stroke="#fbbf24"
                      strokeWidth="1.5"
                      strokeDasharray="2 2"
                    />
                    {/* Ground truth diamond */}
                    <polygon
                      points={`${error.true_u},${error.true_v - 5} ${error.true_u + 5},${error.true_v} ${error.true_u},${error.true_v + 5} ${error.true_u - 5},${error.true_v}`}
                      stroke="#fbbf24"
                      strokeWidth="1.5"
                      fill="rgba(251, 191, 36, 0.2)"
                    />
                  </g>
                )}
              </g>
            )}
          </svg>
        )}

        {/* Viewfinder Top-Left Telemetry Overlay */}
        <div
          style={{
            position: 'absolute',
            top: '8px',
            left: '10px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.72rem',
            color: detected ? '#34d399' : '#f87171',
            background: 'rgba(0, 0, 0, 0.75)',
            padding: '4px 8px',
            borderRadius: '4px',
            backdropFilter: 'blur(4px)',
            border: '1px solid rgba(255,255,255,0.1)',
            lineHeight: 1.4,
          }}
        >
          <div>EST: {detected ? `(${detectionResult.u?.toFixed(2)}, ${detectionResult.v?.toFixed(2)}) px` : '---'}</div>
          {error?.has_ground_truth && error.true_u != null && (
            <div style={{ color: '#fbbf24' }}>
              TRUE: ({error.true_u?.toFixed(2)}, {error.true_v?.toFixed(2)}) px | Err: {error.radial_error?.toFixed(2)} px
            </div>
          )}
        </div>

        {/* Viewfinder Bottom-Right Quality Overlay */}
        <div
          style={{
            position: 'absolute',
            bottom: '8px',
            right: '10px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.70rem',
            color: 'var(--color-text-muted)',
            background: 'rgba(0, 0, 0, 0.75)',
            padding: '4px 8px',
            borderRadius: '4px',
            backdropFilter: 'blur(4px)',
            border: '1px solid rgba(255,255,255,0.1)',
            textAlign: 'right',
            lineHeight: 1.4,
          }}
        >
          <div>PNR: <span style={{ color: '#00e5ff' }}>{metrics?.pnr?.toFixed(1) || '0.0'}</span> | SNR: <span style={{ color: '#00e5ff' }}>{metrics?.snr_db?.toFixed(1) || '0.0'} dB</span></div>
          <div>CONF: <span style={{ color: detected ? '#34d399' : '#f87171' }}>{((metrics?.confidence || 0) * 100).toFixed(0)}%</span> | LAT: {detectionResult?.execution_time_ms?.toFixed(1) || '0.0'} ms</div>
        </div>
      </div>

      {/* Viewfinder Controls Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            type="button"
            className={`btn btn-outline ${showOverlays ? 'btn-active' : ''}`}
            onClick={() => setShowOverlays(!showOverlays)}
            style={{ fontSize: '0.72rem', padding: '3px 8px' }}
          >
            <Crosshair size={12} style={{ marginRight: '4px' }} />
            HUD Reticle
          </button>

          <button
            type="button"
            className={`btn btn-outline ${showGroundTruth ? 'btn-active' : ''}`}
            onClick={() => setShowGroundTruth(!showGroundTruth)}
            style={{ fontSize: '0.72rem', padding: '3px 8px' }}
          >
            <Eye size={12} style={{ marginRight: '4px' }} />
            Ground Truth
          </button>

          <button
            type="button"
            className={`btn btn-outline ${showRawSensor ? 'btn-active' : ''}`}
            onClick={() => setShowRawSensor(!showRawSensor)}
            style={{ fontSize: '0.72rem', padding: '3px 8px' }}
          >
            <Layers size={12} style={{ marginRight: '4px' }} />
            {showRawSensor ? 'Raw Disturbed' : 'Server Annotated'}
          </button>
        </div>

        <button
          type="button"
          className="btn btn-outline"
          onClick={() => setIsZoomed(!isZoomed)}
          style={{ fontSize: '0.72rem', padding: '3px 8px' }}
          title="Toggle Target ROI Inspection Zoom"
        >
          <Maximize2 size={12} style={{ marginRight: '4px' }} />
          {isZoomed ? 'Reset Zoom' : 'Target Zoom'}
        </button>
      </div>
    </div>
  );
}
