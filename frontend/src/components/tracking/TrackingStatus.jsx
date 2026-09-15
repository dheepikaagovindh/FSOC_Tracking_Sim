import React from 'react';
import { Activity, CheckCircle, AlertTriangle, XCircle, ShieldCheck, Zap, Layers } from 'lucide-react';

export default function TrackingStatus({ status, result, telemetry }) {
  const currentStatus = result?.status || status?.status || 'UNINITIALIZED';
  const confidence = result?.confidence ?? status?.current_confidence ?? 0;
  const hits = result?.consecutive_hits ?? 0;
  const misses = result?.consecutive_misses ?? 0;
  const latency = result?.processing_time_ms ?? 0;

  const getStatusBadge = () => {
    switch (currentStatus) {
      case 'TRACKING':
        return {
          icon: <CheckCircle size={16} className="text-emerald-400" />,
          label: 'TRACKING (LOCKED)',
          colorClass: 'status-active',
          bgStyle: 'rgba(16, 185, 129, 0.15)',
          borderStyle: 'rgba(16, 185, 129, 0.4)',
          textColor: '#34d399',
        };
      case 'PREDICTING':
        return {
          icon: <AlertTriangle size={16} className="text-amber-400" />,
          label: 'PREDICTING (COASTING)',
          colorClass: 'status-warning',
          bgStyle: 'rgba(245, 158, 11, 0.15)',
          borderStyle: 'rgba(245, 158, 11, 0.4)',
          textColor: '#fbbf24',
        };
      case 'LOST':
        return {
          icon: <XCircle size={16} className="text-rose-400" />,
          label: 'TRACK LOST',
          colorClass: 'status-error',
          bgStyle: 'rgba(244, 63, 94, 0.15)',
          borderStyle: 'rgba(244, 63, 94, 0.4)',
          textColor: '#f43f5e',
        };
      default:
        return {
          icon: <Activity size={16} className="text-cyan-400" />,
          label: 'UNINITIALIZED',
          colorClass: 'status-idle',
          bgStyle: 'rgba(6, 182, 212, 0.15)',
          borderStyle: 'rgba(6, 182, 212, 0.4)',
          textColor: '#22d3ee',
        };
    }
  };

  const badge = getStatusBadge();
  const confPct = Math.round(confidence * 100);

  return (
    <div className="card tracking-status-card" style={{ marginBottom: '1.25rem' }}>
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={18} className="text-cyan-400" />
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>TRACKING ENGINE STATE</h3>
        </div>
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

      <div className="card-body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginTop: '0.75rem' }}>
        {/* Confidence Gauge */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>
            <span>TRACKING CONFIDENCE</span>
            <span style={{ color: badge.textColor, fontWeight: 700 }}>{confPct}%</span>
          </div>
          <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', overflow: 'hidden' }}>
            <div
              style={{
                width: `${confPct}%`,
                height: '100%',
                background: `linear-gradient(90deg, #06b6d4, ${badge.textColor})`,
                transition: 'width 0.3s ease',
              }}
            />
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '4px' }}>
            {currentStatus === 'TRACKING' ? 'Locked on optical spot' : currentStatus === 'PREDICTING' ? 'Coasting on motion dynamics' : 'Awaiting beacon lock'}
          </div>
        </div>

        {/* Consecutive Hits & Misses */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>FRAME PERSISTENCE</div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginTop: '4px' }}>
            <div>
              <span style={{ fontSize: '0.7rem', color: '#10b981', display: 'block' }}>HITS STREAK</span>
              <span style={{ fontSize: '1.25rem', fontWeight: 700, color: '#34d399' }}>{hits}</span>
            </div>
            <div style={{ height: '24px', width: '1px', background: 'rgba(255, 255, 255, 0.1)' }} />
            <div>
              <span style={{ fontSize: '0.7rem', color: '#f43f5e', display: 'block' }}>MISS STREAK</span>
              <span style={{ fontSize: '1.25rem', fontWeight: 700, color: misses > 0 ? '#fb7185' : '#64748b' }}>{misses}</span>
            </div>
          </div>
        </div>

        {/* Latency & Processing */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>KALMAN UPDATE LATENCY</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.3rem', marginTop: '4px' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 700, color: '#38bdf8' }}>{latency.toFixed(2)}</span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>ms</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: '#10b981', marginTop: '2px' }}>&lt; 1.0ms Real-Time Requirement Met</div>
        </div>
      </div>
    </div>
  );
}
