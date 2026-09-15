import React from 'react';
import { Target, CheckCircle2, AlertCircle, XCircle, ShieldCheck, Compass, Crosshair } from 'lucide-react';

export default function AlignmentStatus({ status, result, telemetry }) {
  const currentStatus = result?.status || status?.status || 'INVALID';
  const isAligned = result?.aligned ?? false;
  const isRadiallyAligned = result?.radially_aligned ?? false;
  const source = result?.source || 'NONE';
  const angMag = result?.angular_error_magnitude_deg ?? 0;
  const angTol = result?.angular_tolerance_deg ?? 0.25;
  const pxMag = result?.pixel_error_magnitude ?? 0;
  const pxTol = result?.pixel_tolerance ?? 5.0;
  const alignedCount = status?.aligned_frames_count ?? 0;

  const getStatusBadge = () => {
    switch (currentStatus) {
      case 'ALIGNED':
        return {
          icon: <CheckCircle2 size={16} className="text-emerald-400" />,
          label: 'ALIGNED (BORESIGHT LOCKED)',
          bgStyle: 'rgba(16, 185, 129, 0.15)',
          borderStyle: 'rgba(16, 185, 129, 0.4)',
          textColor: '#34d399',
        };
      case 'VALID':
        return {
          icon: <AlertCircle size={16} className="text-amber-400" />,
          label: 'ALIGNMENT OFFSET (VALID TRACK)',
          bgStyle: 'rgba(245, 158, 11, 0.15)',
          borderStyle: 'rgba(245, 158, 11, 0.4)',
          textColor: '#fbbf24',
        };
      default:
        return {
          icon: <XCircle size={16} className="text-rose-400" />,
          label: 'INVALID / UNALIGNED',
          bgStyle: 'rgba(244, 63, 94, 0.15)',
          borderStyle: 'rgba(244, 63, 94, 0.4)',
          textColor: '#f43f5e',
        };
    }
  };

  const getSourceBadge = () => {
    switch (source) {
      case 'FILTERED':
        return { label: 'Filtered Track', color: '#34d399', bg: 'rgba(16, 185, 129, 0.1)' };
      case 'PREDICTED':
        return { label: 'Coasting Prediction', color: '#fbbf24', bg: 'rgba(245, 158, 11, 0.1)' };
      default:
        return { label: 'No Track', color: '#94a3b8', bg: 'rgba(148, 163, 184, 0.1)' };
    }
  };

  const badge = getStatusBadge();
  const srcBadge = getSourceBadge();

  // Angular error closeness to tolerance (100% when within tolerance)
  const lockRatio = angTol > 0 ? Math.min(1.0, angTol / Math.max(angMag, 0.001)) : 0;
  const lockPct = Math.round(lockRatio * 100);

  return (
    <div className="card alignment-status-card" style={{ marginBottom: '1.25rem' }}>
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Crosshair size={18} className="text-cyan-400" />
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>BORESIGHT ALIGNMENT LOCK STATE</h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {/* Source Tag */}
          <span
            style={{
              padding: '3px 8px',
              borderRadius: '4px',
              fontSize: '0.7rem',
              fontWeight: 600,
              background: srcBadge.bg,
              color: srcBadge.color,
              border: `1px solid ${srcBadge.color}33`,
            }}
          >
            {srcBadge.label}
          </span>

          {/* Status Tag */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '4px 10px',
              borderRadius: '9999px',
              background: badge.bgStyle,
              border: `1px solid ${badge.borderStyle}`,
              color: badge.textColor,
              fontSize: '0.75rem',
              fontWeight: 700,
              letterSpacing: '0.05em',
            }}
          >
            {badge.icon}
            <span>{badge.label}</span>
          </div>
        </div>
      </div>

      <div className="card-body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginTop: '0.75rem' }}>
        {/* Angular Lock Tolerance Ratio */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>
            <span>ANGULAR LOCK QUALITY</span>
            <span style={{ color: badge.textColor, fontWeight: 700 }}>{isAligned ? '100%' : `${lockPct}%`}</span>
          </div>
          <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', overflow: 'hidden' }}>
            <div
              style={{
                width: isAligned ? '100%' : `${lockPct}%`,
                height: '100%',
                background: isAligned ? '#10b981' : '#f59e0b',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '4px' }}>
            Error: {angMag.toFixed(2)}&deg; / Tol: &plusmn;{angTol.toFixed(2)}&deg;
          </div>
        </div>

        {/* Pixel Error Closeness */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>RADIAL PIXEL OFFSET</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.4rem', marginTop: '4px' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 700, color: isAligned ? '#34d399' : '#fbbf24' }}>
              {result?.valid ? pxMag.toFixed(1) : 'N/A'}
            </span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>px</span>
            <span style={{ fontSize: '0.7rem', color: '#64748b', marginLeft: 'auto' }}>
              Tol: &le; {pxTol.toFixed(1)} px
            </span>
          </div>
          <div style={{ fontSize: '0.7rem', color: isAligned ? '#10b981' : '#fbbf24', marginTop: '2px' }}>
            {isAligned ? 'Target in lock core' : 'Exceeds boresight threshold'}
          </div>
        </div>

        {/* Lock Duration / Stats */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>CUMULATIVE ALIGNED FRAMES</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.3rem', marginTop: '4px' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 700, color: '#38bdf8' }}>{alignedCount}</span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>frames</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginTop: '2px' }}>
            Total Calcs: {status?.total_calculations ?? 0}
          </div>
        </div>
      </div>
    </div>
  );
}
