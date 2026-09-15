import React from 'react';
import { Target, Compass, Gauge, Shield, ArrowUpRight, TrendingUp } from 'lucide-react';

export default function TrackingTelemetry({ result, telemetry }) {
  const measX = telemetry?.measured_x ?? null;
  const measY = telemetry?.measured_y ?? null;
  const posX = result?.position_x ?? null;
  const posY = result?.position_y ?? null;
  const predX = result?.predicted_x ?? null;
  const predY = result?.predicted_y ?? null;
  const velX = result?.velocity_x ?? null;
  const velY = result?.velocity_y ?? null;
  const speed = telemetry?.speed ?? (velX !== null && velY !== null ? Math.hypot(velX, velY) : null);
  const uncX = result?.state_uncertainty_x ?? null;
  const uncY = result?.state_uncertainty_y ?? null;
  const uncVx = result?.velocity_uncertainty_x ?? null;
  const uncVy = result?.velocity_uncertainty_y ?? null;

  // Innovation residual
  const resX = (measX !== null && posX !== null) ? (measX - posX) : null;
  const resY = (measY !== null && posY !== null) ? (measY - posY) : null;

  return (
    <div className="card tracking-telemetry-card" style={{ marginBottom: '1.25rem' }}>
      <div className="card-header" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Compass size={18} className="text-cyan-400" />
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>KINEMATIC TELEMETRY & STATE ESTIMATES</h3>
      </div>

      <div className="card-body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginTop: '0.75rem' }}>
        {/* Measured vs Filtered vs Predicted Coordinates */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', fontWeight: 600, marginBottom: '8px' }}>
            <Target size={14} className="text-emerald-400" />
            <span>FOCAL PLANE POSITIONS (px)</span>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#06b6d4' }}>Measured (Detector):</span>
              <span style={{ fontWeight: 600, color: measX !== null ? '#22d3ee' : '#64748b' }}>
                {measX !== null ? `(${measX.toFixed(1)}, ${measY.toFixed(1)})` : 'N/A (Dropout)'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#10b981' }}>Filtered (Kalman):</span>
              <span style={{ fontWeight: 700, color: posX !== null ? '#34d399' : '#64748b' }}>
                {posX !== null ? `(${posX.toFixed(2)}, ${posY.toFixed(2)})` : 'N/A'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#f59e0b' }}>Lead Predicted (t+&tau;):</span>
              <span style={{ fontWeight: 600, color: predX !== null ? '#fbbf24' : '#64748b' }}>
                {predX !== null ? `(${predX.toFixed(2)}, ${predY.toFixed(2)})` : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Velocity & Speed */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', fontWeight: 600, marginBottom: '8px' }}>
            <TrendingUp size={14} className="text-cyan-400" />
            <span>BEACON VELOCITY DYNAMICS</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Horizontal Velocity (Vx):</span>
              <span style={{ fontWeight: 600, color: velX !== null ? '#38bdf8' : '#64748b' }}>
                {velX !== null ? `${velX.toFixed(2)} px/s` : '0.00 px/s'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Vertical Velocity (Vy):</span>
              <span style={{ fontWeight: 600, color: velY !== null ? '#38bdf8' : '#64748b' }}>
                {velY !== null ? `${velY.toFixed(2)} px/s` : '0.00 px/s'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#e2e8f0' }}>2D Motion Speed:</span>
              <span style={{ fontWeight: 700, color: speed !== null ? '#facc15' : '#64748b' }}>
                {speed !== null ? `${speed.toFixed(2)} px/s` : '0.00 px/s'}
              </span>
            </div>
          </div>
        </div>

        {/* State Covariance Uncertainty */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', fontWeight: 600, marginBottom: '8px' }}>
            <Shield size={14} className="text-purple-400" />
            <span>KALMAN COVARIANCE (1-&sigma;)</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Position StdDev (&sigma;x, &sigma;y):</span>
              <span style={{ fontWeight: 600, color: uncX !== null ? '#c084fc' : '#64748b' }}>
                {uncX !== null ? `(${uncX.toFixed(2)}, ${uncY.toFixed(2)}) px` : 'N/A'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Velocity StdDev (&sigma;vx, &sigma;vy):</span>
              <span style={{ fontWeight: 600, color: uncVx !== null ? '#c084fc' : '#64748b' }}>
                {uncVx !== null ? `(${uncVx.toFixed(2)}, ${uncVy.toFixed(2)}) px/s` : 'N/A'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Innovation Residual (y):</span>
              <span style={{ fontWeight: 600, color: resX !== null ? '#38bdf8' : '#64748b' }}>
                {resX !== null ? `(${resX.toFixed(2)}, ${resY.toFixed(2)}) px` : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
