import React, { useState } from 'react';
import { Target, Crosshair, ShieldCheck, AlertTriangle, Layers, Maximize2 } from 'lucide-react';
import { getAnnotatedImageUrl } from '../../services/detectionApi';
import { getDisturbedImageUrl } from '../../services/disturbanceApi';

export default function DetectionOverlay({
  detectionResult,
  detectionTelemetry,
  disturbanceFrame,
  imageTimestamp,
}) {
  const [showReticle, setShowReticle] = useState(true);
  const [showRawSensor, setShowRawSensor] = useState(false);
  const [isZoomed, setIsZoomed] = useState(false);

  const detected = detectionResult?.detected || false;
  const bbox = detectionResult?.bbox;
  const confidence = detectionResult?.confidence || 0.0;
  const centerU = detectionResult?.center_x ?? detectionResult?.u;
  const centerV = detectionResult?.center_y ?? detectionResult?.v;

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
            BEACON DETECTION OVERLAY (OPENCV)
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
              BEACON DETECTED
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
              BEACON NOT DETECTED
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
          transformOrigin: centerU != null && centerV != null
            ? `${(centerU / width) * 100}% ${(centerV / height) * 100}%`
            : 'center center',
          transition: 'transform 0.3s ease-in-out',
        }}
      >
        {/* Disturbed Sensor Image */}
        <img
          src={imageUrl}
          alt="Beacon Detection Viewfinder"
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

        {/* Dynamic SVG Reticle Overlay (Strictly NO Ground Truth) */}
        {showReticle && (
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

            {/* Detected Target Reticle & Bounding Box */}
            {detected && centerU != null && centerV != null && (
              <g>
                {/* Bounding Box */}
                {bbox && (
                  <rect
                    x={bbox.x}
                    y={bbox.y}
                    width={bbox.width}
                    height={bbox.height}
                    fill="none"
                    stroke="#00e5ff"
                    strokeWidth="1.5"
                    strokeDasharray="3 2"
                  />
                )}

                {/* Sub-Pixel Target Reticle */}
                <circle
                  cx={centerU}
                  cy={centerV}
                  r="12"
                  stroke="#10b981"
                  strokeWidth="2"
                  fill="none"
                />
                <circle
                  cx={centerU}
                  cy={centerV}
                  r="3"
                  fill="#00e5ff"
                />
              </g>
            )}
          </svg>
        )}

        {/* Viewfinder Top-Left Coordinates Overlay */}
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
          <div>DETECTOR: {detectionResult?.method?.toUpperCase() || 'OPENCV'}</div>
          <div>
            CENTER: {detected ? `U = ${centerU?.toFixed(1)} px, V = ${centerV?.toFixed(1)} px` : '---'}
          </div>
        </div>

        {/* Viewfinder Bottom-Right Latency / Confidence Overlay */}
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
          <div>CONF: <span style={{ color: detected ? '#34d399' : '#f87171', fontWeight: 600 }}>{(confidence * 100).toFixed(0)}%</span></div>
          <div>LATENCY: {detectionResult?.processing_time_ms?.toFixed(1) || '0.0'} ms | CANDIDATES: {detectionResult?.candidate_count || 0}</div>
        </div>
      </div>

      {/* Viewfinder Controls Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            type="button"
            className={`btn btn-outline ${showReticle ? 'btn-active' : ''}`}
            onClick={() => setShowReticle(!showReticle)}
            style={{ fontSize: '0.72rem', padding: '3px 8px' }}
          >
            <Crosshair size={12} style={{ marginRight: '4px' }} />
            Reticle Overlay
          </button>

          <button
            type="button"
            className={`btn btn-outline ${showRawSensor ? 'btn-active' : ''}`}
            onClick={() => setShowRawSensor(!showRawSensor)}
            style={{ fontSize: '0.72rem', padding: '3px 8px' }}
          >
            <Layers size={12} style={{ marginRight: '4px' }} />
            {showRawSensor ? 'Raw Disturbed' : 'Detection Overlay'}
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
