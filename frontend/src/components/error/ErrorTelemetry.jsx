import React from 'react';
import { Compass, Target, TrendingUp, Navigation, Shield, Move } from 'lucide-react';

export default function ErrorTelemetry({ result, telemetry }) {
  const valid = result?.valid ?? false;
  const ex = result?.pixel_error_x ?? null;
  const ey = result?.pixel_error_y ?? null;
  const emag = result?.pixel_error_magnitude ?? null;

  const angX = result?.angular_error_x_deg ?? null;
  const angY = result?.angular_error_y_deg ?? null;
  const angMag = result?.angular_error_magnitude_deg ?? null;
  const trueSep = result?.true_angular_separation_deg ?? null;

  const normX = result?.normalized_error_x ?? null;
  const normY = result?.normalized_error_y ?? null;
  const normMag = result?.normalized_error_magnitude ?? null;

  const dirDeg = result?.error_direction_deg ?? null;
  const rateX = result?.error_rate_x ?? null;
  const rateY = result?.error_rate_y ?? null;

  return (
    <div className="card error-telemetry-card" style={{ marginBottom: '1.25rem' }}>
      <div className="card-header" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Compass size={18} className="text-cyan-400" />
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>POINTING ERROR TELEMETRY & MULTI-AXIS OFFSETS</h3>
      </div>

      <div className="card-body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginTop: '0.75rem' }}>
        {/* Pixel Offsets */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', fontWeight: 600, marginBottom: '8px' }}>
            <Move size={14} className="text-emerald-400" />
            <span>PIXEL DISPLACEMENTS (e)</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>X Pixel Error (ex):</span>
              <span style={{ fontWeight: 600, color: valid && ex !== null ? '#38bdf8' : '#64748b' }}>
                {valid && ex !== null ? `${ex > 0 ? '+' : ''}${ex.toFixed(1)} px` : 'N/A'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Y Pixel Error (ey):</span>
              <span style={{ fontWeight: 600, color: valid && ey !== null ? '#38bdf8' : '#64748b' }}>
                {valid && ey !== null ? `${ey > 0 ? '+' : ''}${ey.toFixed(1)} px` : 'N/A'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#e2e8f0' }}>Radial Magnitude:</span>
              <span style={{ fontWeight: 700, color: valid && emag !== null ? '#facc15' : '#64748b' }}>
                {valid && emag !== null ? `${emag.toFixed(2)} px` : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Angular Boresight Offsets */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', fontWeight: 600, marginBottom: '8px' }}>
            <Navigation size={14} className="text-cyan-400" />
            <span>ANGULAR OFFSETS (&theta;)</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Azimuth Angle (&theta;x):</span>
              <span style={{ fontWeight: 600, color: valid && angX !== null ? '#34d399' : '#64748b' }}>
                {valid && angX !== null ? `${angX > 0 ? '+' : ''}${angX.toFixed(3)}°` : 'N/A'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Elevation Angle (&theta;y):</span>
              <span style={{ fontWeight: 600, color: valid && angY !== null ? '#34d399' : '#64748b' }}>
                {valid && angY !== null ? `${angY > 0 ? '+' : ''}${angY.toFixed(3)}°` : 'N/A'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#e2e8f0' }}>Angular Magnitude:</span>
              <span style={{ fontWeight: 700, color: valid && angMag !== null ? '#38bdf8' : '#64748b' }}>
                {valid && angMag !== null ? `${angMag.toFixed(3)}°` : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Direction & Error Rates */}
        <div className="telemetry-box" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', fontWeight: 600, marginBottom: '8px' }}>
            <TrendingUp size={14} className="text-purple-400" />
            <span>DIRECTION & ERROR RATES</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Vector Direction (&phi;):</span>
              <span style={{ fontWeight: 600, color: valid && dirDeg !== null ? '#c084fc' : '#64748b' }}>
                {valid && dirDeg !== null ? `${dirDeg.toFixed(1)}°` : 'N/A'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Error Rate X (dex/dt):</span>
              <span style={{ fontWeight: 600, color: valid && rateX !== null ? '#c084fc' : '#64748b' }}>
                {valid && rateX !== null ? `${rateX > 0 ? '+' : ''}${rateX.toFixed(1)} px/s` : '0.0 px/s'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Error Rate Y (dey/dt):</span>
              <span style={{ fontWeight: 600, color: valid && rateY !== null ? '#c084fc' : '#64748b' }}>
                {valid && rateY !== null ? `${rateY > 0 ? '+' : ''}${rateY.toFixed(1)} px/s` : '0.0 px/s'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
