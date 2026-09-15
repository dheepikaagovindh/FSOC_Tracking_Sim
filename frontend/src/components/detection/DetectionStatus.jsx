import React from 'react';
import { Activity, Cpu, CheckCircle2, XCircle, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function DetectionStatus({ detectionResult, detectionStatus }) {
  const detected = detectionResult?.detected || false;
  const confidence = detectionResult?.confidence || 0.0;
  const confidencePct = Math.round(confidence * 100);
  const centerU = detectionResult?.center_x ?? detectionResult?.u;
  const centerV = detectionResult?.center_y ?? detectionResult?.v;
  const bbox = detectionResult?.bbox;

  let confColor = '#ef4444';
  if (confidencePct >= 75) confColor = '#10b981';
  else if (confidencePct >= 40) confColor = '#f59e0b';

  return (
    <div className="hud-card" style={{ padding: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <Activity size={18} color="var(--color-primary)" />
        <h3 style={{ margin: 0, fontSize: '0.90rem', fontWeight: 600 }}>
          DETECTOR STATUS & TELEMETRY
        </h3>
      </div>

      {/* Status Banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 14px',
          borderRadius: '6px',
          background: detected ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
          border: detected ? '1px solid #10b981' : '1px solid #ef4444',
          marginBottom: '14px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {detected ? (
            <CheckCircle2 size={18} color="#10b981" />
          ) : (
            <XCircle size={18} color="#ef4444" />
          )}
          <div>
            <div style={{ fontSize: '0.82rem', fontWeight: 700, color: detected ? '#34d399' : '#f87171' }}>
              {detected ? 'BEACON DETECTED' : 'BEACON NOT DETECTED'}
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
              {detectionResult?.message || 'Awaiting frame...'}
            </div>
          </div>
        </div>
        <div style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
          <div>METHOD: {detectionResult?.method?.toUpperCase() || 'OPENCV'}</div>
          <div>{detectionResult?.processing_time_ms?.toFixed(1) || '0.0'} ms</div>
        </div>
      </div>

      {/* Confidence Score Bar */}
      <div style={{ marginBottom: '14px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px', fontFamily: 'var(--font-mono)' }}>
          <span style={{ color: 'var(--color-text-muted)' }}>Detection Confidence (Heuristic):</span>
          <span style={{ fontWeight: 700, color: confColor }}>{confidence.toFixed(2)} ({confidencePct}%)</span>
        </div>
        <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden' }}>
          <div
            style={{
              width: `${confidencePct}%`,
              height: '100%',
              background: confColor,
              transition: 'width 0.2s ease',
            }}
          />
        </div>
      </div>

      {/* Coordinates & Bounding Box */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
        <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem', marginBottom: '4px' }}>DETECTED BEACON CENTER</div>
          <div style={{ color: '#00e5ff', fontWeight: 700 }}>
            U = {detected && centerU != null ? centerU.toFixed(1) : 'null'}
          </div>
          <div style={{ color: '#00e5ff', fontWeight: 700 }}>
            V = {detected && centerV != null ? centerV.toFixed(1) : 'null'}
          </div>
        </div>

        <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem', marginBottom: '4px' }}>BOUNDING BOX</div>
          {bbox ? (
            <div style={{ color: 'var(--color-text)', fontSize: '0.72rem', lineHeight: 1.3 }}>
              <div>X: {bbox.x}, Y: {bbox.y}</div>
              <div>W: {bbox.width} px, H: {bbox.height} px</div>
            </div>
          ) : (
            <div style={{ color: 'var(--color-text-muted)' }}>null</div>
          )}
        </div>
      </div>

      {/* Candidates and Latency row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '10px', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
        <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem', marginBottom: '2px' }}>CANDIDATES</div>
          <div style={{ color: 'var(--color-text)', fontWeight: 600 }}>
            {detectionResult?.candidate_count ?? 0}
          </div>
        </div>

        <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem', marginBottom: '2px' }}>PROCESSING TIME</div>
          <div style={{ color: 'var(--color-text)', fontWeight: 600 }}>
            {detectionResult?.processing_time_ms?.toFixed(1) || '0.0'} ms
          </div>
        </div>
      </div>
    </div>
  );
}
