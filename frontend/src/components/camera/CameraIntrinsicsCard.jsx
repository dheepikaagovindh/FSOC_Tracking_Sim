import React from 'react';
import { Sliders, Cpu, Grid } from 'lucide-react';

export default function CameraIntrinsicsCard({ intrinsics }) {
  if (!intrinsics) return null;

  const {
    width = 640,
    height = 480,
    fx = 1194.27,
    fy = 1206.56,
    cx = 320.0,
    cy = 240.0,
    hfov_deg = 30.0,
    vfov_deg = 22.5,
  } = intrinsics;

  const aspectRatio = (width / height).toFixed(2);

  return (
    <div className="hud-card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Cpu size={18} style={{ color: 'var(--color-primary)' }} />
          <h2 style={{ fontSize: '1rem', margin: 0 }}>OPTICAL SENSOR INTRINSICS (PINHOLE MODEL)</h2>
        </div>
        <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
          K MATRIX DERIVED
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px' }}>
        {/* Optical Parameters Summary */}
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ color: 'var(--color-primary)', fontSize: '0.75rem', fontWeight: 'bold', marginBottom: '6px' }}>
            DERIVED PARAMETERS
          </div>
          <table style={{ width: '100%', fontSize: '0.78rem', fontFamily: 'var(--font-mono)', borderCollapse: 'collapse' }}>
            <tbody>
              <tr>
                <td style={{ color: 'var(--color-text-muted)', padding: '2px 0' }}>Focal Length fx:</td>
                <td style={{ textAlign: 'right', color: '#38bdf8' }}>{fx.toFixed(2)} px</td>
              </tr>
              <tr>
                <td style={{ color: 'var(--color-text-muted)', padding: '2px 0' }}>Focal Length fy:</td>
                <td style={{ textAlign: 'right', color: '#38bdf8' }}>{fy.toFixed(2)} px</td>
              </tr>
              <tr>
                <td style={{ color: 'var(--color-text-muted)', padding: '2px 0' }}>Center cx:</td>
                <td style={{ textAlign: 'right', color: '#34d399' }}>{cx.toFixed(1)} px</td>
              </tr>
              <tr>
                <td style={{ color: 'var(--color-text-muted)', padding: '2px 0' }}>Center cy:</td>
                <td style={{ textAlign: 'right', color: '#34d399' }}>{cy.toFixed(1)} px</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Intrinsic Matrix K Display */}
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ color: 'var(--color-primary)', fontSize: '0.75rem', fontWeight: 'bold', marginBottom: '6px' }}>
            3x3 INTRINSIC MATRIX K
          </div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.75rem',
            background: '#05070a',
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid rgba(0, 229, 255, 0.2)',
            display: 'flex',
            flexDirection: 'column',
            gap: '2px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#38bdf8' }}>{fx.toFixed(1)}</span>
              <span style={{ color: 'var(--color-text-muted)' }}>0.0</span>
              <span style={{ color: '#34d399' }}>{cx.toFixed(1)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>0.0</span>
              <span style={{ color: '#38bdf8' }}>{fy.toFixed(1)}</span>
              <span style={{ color: '#34d399' }}>{cy.toFixed(1)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>0.0</span>
              <span style={{ color: 'var(--color-text-muted)' }}>0.0</span>
              <span style={{ color: '#f59e0b' }}>1.0</span>
            </div>
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
            Aspect Ratio: {aspectRatio}:1 ({width}x{height})
          </div>
        </div>
      </div>
    </div>
  );
}
