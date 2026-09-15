import React from 'react';
import { Camera, RadioTower, Navigation, Activity } from 'lucide-react';

export default function PlatformStatus({ cameraPlatform, beaconPlatform }) {
  return (
    <div className="form-grid-2">
      {/* 1. Camera Platform Card */}
      <div className="hud-card">
        <div className="card-header">
          <div className="card-title-group">
            <Camera size={18} color="#22d3ee" />
            <h2>Camera Platform (Receiver)</h2>
          </div>
          <span className="card-badge" style={{ color: '#22d3ee', borderColor: 'rgba(6,182,212,0.4)' }}>
            {cameraPlatform?.motion_profile?.toUpperCase() || 'STATIC'}
          </span>
        </div>
        <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {/* Position Coordinates */}
          <div>
            <div className="form-label" style={{ marginBottom: '6px' }}>
              <span>Instantaneous 3D Position</span>
              <span className="unit-badge">meters (X, Y, Z)</span>
            </div>
            <div className="form-grid-3">
              <div className="coordinate-readout">
                <span className="coord-axis">X:</span>
                <span className="coord-val">{cameraPlatform?.position?.x?.toFixed(3) ?? '0.000'} m</span>
              </div>
              <div className="coordinate-readout">
                <span className="coord-axis">Y:</span>
                <span className="coord-val">{cameraPlatform?.position?.y?.toFixed(3) ?? '0.000'} m</span>
              </div>
              <div className="coordinate-readout">
                <span className="coord-axis">Z:</span>
                <span className="coord-val">{cameraPlatform?.position?.z?.toFixed(3) ?? '0.000'} m</span>
              </div>
            </div>
          </div>

          {/* Velocity Vector */}
          <div>
            <div className="form-label" style={{ marginBottom: '6px' }}>
              <span>Instantaneous Linear Velocity</span>
              <span className="unit-badge">m/s (Vx, Vy, Vz)</span>
            </div>
            <div className="form-grid-3">
              <div className="coordinate-readout">
                <span className="coord-axis">Vx:</span>
                <span className="coord-val">{cameraPlatform?.velocity?.x?.toFixed(3) ?? '0.000'}</span>
              </div>
              <div className="coordinate-readout">
                <span className="coord-axis">Vy:</span>
                <span className="coord-val">{cameraPlatform?.velocity?.y?.toFixed(3) ?? '0.000'}</span>
              </div>
              <div className="coordinate-readout">
                <span className="coord-axis">Vz:</span>
                <span className="coord-val">{cameraPlatform?.velocity?.z?.toFixed(3) ?? '0.000'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Beacon Platform Card */}
      <div className="hud-card">
        <div className="card-header">
          <div className="card-title-group">
            <RadioTower size={18} color="#34d399" />
            <h2>Beacon Platform (Transmitter)</h2>
          </div>
          <span className="card-badge" style={{ color: '#34d399', borderColor: 'rgba(16,185,129,0.4)' }}>
            {beaconPlatform?.motion_profile?.toUpperCase() || 'STATIC'}
          </span>
        </div>
        <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {/* Position Coordinates */}
          <div>
            <div className="form-label" style={{ marginBottom: '6px' }}>
              <span>Instantaneous 3D Position</span>
              <span className="unit-badge">meters (X, Y, Z)</span>
            </div>
            <div className="form-grid-3">
              <div className="coordinate-readout highlight-beacon">
                <span className="coord-axis">X:</span>
                <span className="coord-val">{beaconPlatform?.position?.x?.toFixed(3) ?? '0.000'} m</span>
              </div>
              <div className="coordinate-readout highlight-beacon">
                <span className="coord-axis">Y:</span>
                <span className="coord-val">{beaconPlatform?.position?.y?.toFixed(3) ?? '0.000'} m</span>
              </div>
              <div className="coordinate-readout highlight-beacon">
                <span className="coord-axis">Z:</span>
                <span className="coord-val">{beaconPlatform?.position?.z?.toFixed(3) ?? '0.000'} m</span>
              </div>
            </div>
          </div>

          {/* Velocity Vector */}
          <div>
            <div className="form-label" style={{ marginBottom: '6px' }}>
              <span>Instantaneous Linear Velocity</span>
              <span className="unit-badge">m/s (Vx, Vy, Vz)</span>
            </div>
            <div className="form-grid-3">
              <div className="coordinate-readout highlight-beacon">
                <span className="coord-axis">Vx:</span>
                <span className="coord-val">{beaconPlatform?.velocity?.x?.toFixed(3) ?? '0.000'}</span>
              </div>
              <div className="coordinate-readout highlight-beacon">
                <span className="coord-axis">Vy:</span>
                <span className="coord-val">{beaconPlatform?.velocity?.y?.toFixed(3) ?? '0.000'}</span>
              </div>
              <div className="coordinate-readout highlight-beacon">
                <span className="coord-axis">Vz:</span>
                <span className="coord-val">{beaconPlatform?.velocity?.z?.toFixed(3) ?? '0.000'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
