import React from 'react';
import { Target, Compass, ArrowUpRight, Crosshair } from 'lucide-react';

export default function WorldTelemetry({ geometry }) {
  const relPos = geometry?.relative_position;
  const range = geometry?.range ?? 0.0;
  const azimuth = geometry?.azimuth_deg ?? 0.0;
  const elevation = geometry?.elevation_deg ?? 0.0;

  return (
    <div className="hud-card">
      <div className="card-header">
        <div className="card-title-group">
          <Target size={18} color="#f59e0b" />
          <h2>Ground-Truth Relative Geometry</h2>
        </div>
        <span className="card-badge" style={{ color: '#f59e0b', borderColor: 'rgba(245,158,11,0.4)' }}>
          LOS VECTOR
        </span>
      </div>
      <div className="card-body">
        {/* Geometry Metrics Grid */}
        <div className="form-grid-3" style={{ marginBottom: '16px' }}>
          {/* Euclidean Range */}
          <div className="telemetry-box">
            <div className="telemetry-box-header">
              <Crosshair size={14} color="#38bdf8" />
              <span>GROUND-TRUTH RANGE</span>
            </div>
            <div className="telemetry-box-val highlight-cyan">
              {range.toFixed(3)} <span className="unit-label">m</span>
            </div>
            <div className="telemetry-box-footer">Distance Pb to Pc</div>
          </div>

          {/* Azimuth / Bearing */}
          <div className="telemetry-box">
            <div className="telemetry-box-header">
              <Compass size={14} color="#34d399" />
              <span>AZIMUTH (BEARING)</span>
            </div>
            <div className="telemetry-box-val highlight-emerald">
              {azimuth.toFixed(3)} <span className="unit-label">deg</span>
            </div>
            <div className="telemetry-box-footer">atan2(Δx, Δz)</div>
          </div>

          {/* Elevation */}
          <div className="telemetry-box">
            <div className="telemetry-box-header">
              <ArrowUpRight size={14} color="#fbbf24" />
              <span>ELEVATION ANGLE</span>
            </div>
            <div className="telemetry-box-val highlight-amber">
              {elevation.toFixed(3)} <span className="unit-label">deg</span>
            </div>
            <div className="telemetry-box-footer">atan2(Δy, R_horiz)</div>
          </div>
        </div>

        {/* Relative Displacement Vector Readout */}
        <div className="coordinate-row-container">
          <div className="form-label" style={{ marginBottom: '6px' }}>
            <span>Relative Offset Vector (Δx, Δy, Δz)</span>
            <span className="unit-badge">Pb - Pc (meters)</span>
          </div>
          <div className="form-grid-3">
            <div className="coordinate-readout">
              <span className="coord-axis">ΔX:</span>
              <span className="coord-val">{relPos?.x?.toFixed(3) ?? '0.000'} m</span>
            </div>
            <div className="coordinate-readout">
              <span className="coord-axis">ΔY:</span>
              <span className="coord-val">{relPos?.y?.toFixed(3) ?? '0.000'} m</span>
            </div>
            <div className="coordinate-readout">
              <span className="coord-axis">ΔZ:</span>
              <span className="coord-val">{relPos?.z?.toFixed(3) ?? '0.000'} m</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
