import React from 'react';
import { Activity, Target, Navigation, Radio, AlertCircle } from 'lucide-react';

export default function CameraTelemetryCard({ telemetry, intrinsics }) {
  if (!telemetry) {
    return (
      <div className="hud-card">
        <div className="card-header">
          <Activity size={18} style={{ color: 'var(--color-primary)' }} />
          <h2 style={{ fontSize: '1rem', margin: 0 }}>OPTICAL TELEMETRY</h2>
        </div>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.8rem', padding: '12px' }}>
          No telemetry stream active. Step or run simulation to capture frames.
        </p>
      </div>
    );
  }

  const {
    timestamp = 0.0,
    visible = false,
    visibility_reason = 'UNKNOWN',
    projection = { u: 0, v: 0, normalized_x: 0, normalized_y: 0 },
    angles = { azimuth_deg: 0, elevation_deg: 0 },
    beacon_camera_coordinates = { x: 0, y: 0, z: 0 },
    camera_pose = { pan_deg: 0, tilt_deg: 0 },
    spot = { radius: 2.5, intensity: 255 },
    world_range = null,
  } = telemetry;

  const cx = intrinsics?.cx || 320.0;
  const cy = intrinsics?.cy || 240.0;
  const deltaU = projection.u - cx;
  const deltaV = projection.v - cy;
  const radialPixelError = Math.sqrt(deltaU * deltaU + deltaV * deltaV);

  return (
    <div className="hud-card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={18} style={{ color: 'var(--color-primary)' }} />
          <h2 style={{ fontSize: '1rem', margin: 0 }}>OPTICAL TELEMETRY & TRACKING ERROR</h2>
        </div>
        <span
          className={`status-pill ${visible ? 'status-pill-success' : 'status-pill-danger'}`}
          style={{ fontSize: '0.72rem', padding: '3px 8px' }}
        >
          {visible ? 'BEACON ACQUIRED' : visibility_reason}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px' }}>
        {/* 1. Focal Plane Pixel Coordinates */}
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', color: 'var(--color-primary)', fontSize: '0.75rem', fontWeight: 'bold' }}>
            <Target size={14} />
            <span>FOCAL PLANE COORDS (u, v)</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
            <div>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>u: </span>
              <span style={{ color: '#38bdf8' }}>{projection.u.toFixed(2)} px</span>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>v: </span>
              <span style={{ color: '#38bdf8' }}>{projection.v.toFixed(2)} px</span>
            </div>
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
            Center: [{cx.toFixed(1)}, {cy.toFixed(1)}]
          </div>
        </div>

        {/* 2. Boresight Pixel Error Offsets */}
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', color: 'var(--color-primary)', fontSize: '0.75rem', fontWeight: 'bold' }}>
            <Radio size={14} />
            <span>BORESIGHT ERROR (Δu, Δv)</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
            <div>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>Δu: </span>
              <span style={{ color: Math.abs(deltaU) < 5 ? '#22c55e' : '#f59e0b' }}>
                {deltaU > 0 ? `+${deltaU.toFixed(2)}` : deltaU.toFixed(2)} px
              </span>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>Δv: </span>
              <span style={{ color: Math.abs(deltaV) < 5 ? '#22c55e' : '#f59e0b' }}>
                {deltaV > 0 ? `+${deltaV.toFixed(2)}` : deltaV.toFixed(2)} px
              </span>
            </div>
          </div>
          <div style={{ fontSize: '0.68rem', color: '#a78bfa', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
            Radial Error: {radialPixelError.toFixed(2)} px
          </div>
        </div>

        {/* 3. Apparent Angular Bearing Relative to Boresight */}
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', color: 'var(--color-primary)', fontSize: '0.75rem', fontWeight: 'bold' }}>
            <Navigation size={14} />
            <span>APPARENT ANGLES (AZ / EL)</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
            <div>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>θ_az: </span>
              <span style={{ color: '#34d399' }}>{angles.azimuth_deg.toFixed(3)}°</span>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>θ_el: </span>
              <span style={{ color: '#34d399' }}>{angles.elevation_deg.toFixed(3)}°</span>
            </div>
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
            Gimbal Pan: {camera_pose.pan_deg?.toFixed(2)}° | Tilt: {camera_pose.tilt_deg?.toFixed(2)}°
          </div>
        </div>

        {/* 4. Beacon Coordinates in Camera Reference Frame */}
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', color: 'var(--color-primary)', fontSize: '0.75rem', fontWeight: 'bold' }}>
            <AlertCircle size={14} />
            <span>CAMERA FRAME 3D (X_c, Y_c, Z_c)</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
            <span>X: {beacon_camera_coordinates.x.toFixed(2)}m</span>
            <span>Y: {beacon_camera_coordinates.y.toFixed(2)}m</span>
            <span>Z: {beacon_camera_coordinates.z.toFixed(2)}m</span>
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
            Range: {world_range ? `${world_range.toFixed(2)} m` : `${beacon_camera_coordinates.z.toFixed(2)} m`} | Spot: r={spot.radius}px, I={spot.intensity}
          </div>
        </div>
      </div>
    </div>
  );
}
