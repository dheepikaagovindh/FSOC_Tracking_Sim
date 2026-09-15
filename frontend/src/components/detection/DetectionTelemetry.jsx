import React from 'react';
import { Gauge, BarChart3, Clock, Layers, Sparkles } from 'lucide-react';

export default function DetectionTelemetry({ detectionResult, detectionStatus, detectionTelemetry }) {
  const detected = detectionResult?.detected || false;
  const status = detectionStatus;
  const telemetry = detectionTelemetry;

  return (
    <div className="hud-card" style={{ padding: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <Gauge size={18} color="var(--color-primary)" />
        <h3 style={{ margin: 0, fontSize: '0.90rem', fontWeight: 600 }}>
          EXECUTION & BENCHMARK TELEMETRY
        </h3>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', marginBottom: '12px' }}>
        <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem' }}>DETECTION METHOD</div>
          <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#00e5ff' }}>
            {detectionResult?.method?.toUpperCase() || 'OPENCV'}
          </div>
        </div>

        <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem' }}>PROCESSING LATENCY</div>
          <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--color-text)' }}>
            {detectionResult?.processing_time_ms?.toFixed(1) || '0.0'} ms
          </div>
        </div>

        <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem' }}>CANDIDATES FOUND</div>
          <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--color-text)' }}>
            {detectionResult?.candidate_count || 0} blobs
          </div>
        </div>

        <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem' }}>SUCCESS RATE</div>
          <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#10b981' }}>
            {status?.detection_rate_pct?.toFixed(1) || '0.0'}%
          </div>
        </div>
      </div>

      {/* Frame Counter Summary */}
      <div style={{ padding: '8px 12px', background: 'rgba(0, 229, 255, 0.04)', borderRadius: '6px', border: '1px solid rgba(0, 229, 255, 0.15)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: 'var(--font-mono)', fontSize: '0.72rem' }}>
        <span style={{ color: 'var(--color-text-muted)' }}>Frames Processed:</span>
        <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>
          {status?.successful_detections || 0} / {status?.total_frames_processed || 0}
        </span>
      </div>
    </div>
  );
}
