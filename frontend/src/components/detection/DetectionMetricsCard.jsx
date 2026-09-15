import React from 'react';
import { Activity, Radio, Gauge, Compass, CheckCircle2, XCircle, BarChart3, Clock } from 'lucide-react';

export default function DetectionMetricsCard({ detectionResult, detectionStatus, detectionTelemetry }) {
  const detected = detectionResult?.detected || false;
  const metrics = detectionResult?.metrics;
  const error = detectionResult?.error;
  const status = detectionStatus;

  const pnr = metrics?.pnr || 0;
  const snrDb = metrics?.snr_db || 0;
  const confidencePct = Math.round((metrics?.confidence || 0) * 100);

  // Confidence color
  let confColor = '#ef4444'; // Red
  if (confidencePct >= 75) confColor = '#10b981'; // Green
  else if (confidencePct >= 40) confColor = '#f59e0b'; // Amber

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* 1. Primary Acquisition State Card */}
      <div className="hud-card" style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Activity size={18} color="var(--color-primary)" />
          <h3 style={{ margin: 0, fontSize: '0.90rem', fontWeight: 600 }}>
            OPTICAL ACQUISITION TELEMETRY
          </h3>
        </div>

        {/* Lock Banner */}
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
                {detected ? 'OPTICAL BEACON ACQUIRED' : 'SIGNAL LOST / OCCLUDED'}
              </div>
              <div style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                {detectionResult?.message || 'Awaiting frame...'}
              </div>
            </div>
          </div>
          <div style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            <div>{detectionResult?.algorithm_used?.toUpperCase() || 'HYBRID'}</div>
            <div>{detectionResult?.execution_time_ms?.toFixed(1) || '0.0'} ms</div>
          </div>
        </div>

        {/* Confidence Gauge Bar */}
        <div style={{ marginBottom: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px', fontFamily: 'var(--font-mono)' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Detection Confidence:</span>
            <span style={{ fontWeight: 700, color: confColor }}>{confidencePct}%</span>
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

        {/* Estimated Coordinates vs Ground Truth */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem', marginBottom: '2px' }}>ESTIMATED CENTROID</div>
            <div style={{ color: '#00e5ff', fontWeight: 700 }}>
              û: {detected ? detectionResult?.u?.toFixed(2) : '---'} px
            </div>
            <div style={{ color: '#00e5ff', fontWeight: 700 }}>
              v̂: {detected ? detectionResult?.v?.toFixed(2) : '---'} px
            </div>
          </div>

          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem', marginBottom: '2px' }}>GROUND TRUTH</div>
            <div style={{ color: '#fbbf24' }}>
              u: {error?.true_u != null ? error.true_u.toFixed(2) : '---'} px
            </div>
            <div style={{ color: '#fbbf24' }}>
              v: {error?.true_v != null ? error.true_v.toFixed(2) : '---'} px
            </div>
          </div>
        </div>

        {/* Radial Error */}
        {error?.radial_error != null && (
          <div style={{ marginTop: '10px', padding: '8px 12px', background: 'rgba(0, 229, 255, 0.05)', borderRadius: '6px', border: '1px solid rgba(0, 229, 255, 0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Radial Localization Error (Δr):</span>
            <span style={{ fontWeight: 700, color: error.radial_error < 0.2 ? '#34d399' : '#fbbf24' }}>
              {error.radial_error.toFixed(3)} px
            </span>
          </div>
        )}
      </div>

      {/* 2. Optical Signal & Noise Quality */}
      <div className="hud-card" style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Gauge size={18} color="var(--color-primary)" />
          <h3 style={{ margin: 0, fontSize: '0.90rem', fontWeight: 600 }}>
            SIGNAL & NOISE METRICS
          </h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem' }}>PEAK INTENSITY</div>
            <div style={{ fontWeight: 600, fontSize: '0.90rem', color: 'var(--color-text)' }}>
              {metrics?.peak_intensity?.toFixed(0) || '0'} / 255
            </div>
          </div>

          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem' }}>NOISE FLOOR (μ ± σ)</div>
            <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--color-text)' }}>
              {metrics?.background_mean?.toFixed(1) || '0.0'} ± {metrics?.background_std?.toFixed(1) || '0.0'}
            </div>
          </div>

          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem' }}>PEAK-TO-NOISE (PNR)</div>
            <div style={{ fontWeight: 700, fontSize: '0.90rem', color: pnr >= 3.0 ? '#34d399' : '#f59e0b' }}>
              {pnr.toFixed(1)}x
            </div>
          </div>

          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem' }}>SIGNAL-TO-NOISE (SNR)</div>
            <div style={{ fontWeight: 700, fontSize: '0.90rem', color: snrDb >= 10.0 ? '#34d399' : '#f59e0b' }}>
              {snrDb.toFixed(1)} dB
            </div>
          </div>

          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem' }}>DYNAMIC THRESHOLD (T)</div>
            <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--color-text)' }}>
              {metrics?.threshold?.toFixed(1) || '0.0'}
            </div>
          </div>

          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem' }}>INTEGRATED FLUX</div>
            <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--color-text)' }}>
              {metrics?.flux?.toFixed(1) || '0.0'}
            </div>
          </div>
        </div>
      </div>

      {/* 3. Boresight Angular Bearings */}
      <div className="hud-card" style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Compass size={18} color="var(--color-primary)" />
          <h3 style={{ margin: 0, fontSize: '0.90rem', fontWeight: 600 }}>
            BORESIGHT ANGULAR BEARINGS
          </h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem' }}>ESTIMATED AZIMUTH (θ̂_az)</div>
            <div style={{ color: '#00e5ff', fontWeight: 700, fontSize: '0.88rem' }}>
              {detected ? `${detectionResult?.azimuth_deg?.toFixed(3)}°` : '---'}
            </div>
            {error?.error_azimuth_deg != null && (
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem', marginTop: '2px' }}>
                Δ: {error.error_azimuth_deg.toFixed(4)}°
              </div>
            )}
          </div>

          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem' }}>ESTIMATED ELEVATION (θ̂_el)</div>
            <div style={{ color: '#00e5ff', fontWeight: 700, fontSize: '0.88rem' }}>
              {detected ? `${detectionResult?.elevation_deg?.toFixed(3)}°` : '---'}
            </div>
            {error?.error_elevation_deg != null && (
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem', marginTop: '2px' }}>
                Δ: {error.error_elevation_deg.toFixed(4)}°
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 4. Cumulative Performance Statistics */}
      <div className="hud-card" style={{ padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <BarChart3 size={18} color="var(--color-primary)" />
          <h3 style={{ margin: 0, fontSize: '0.90rem', fontWeight: 600 }}>
            CUMULATIVE BENCHMARKS
          </h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem' }}>DETECTION RATE</div>
            <div style={{ color: '#10b981', fontWeight: 700, fontSize: '0.92rem' }}>
              {status?.detection_rate_pct?.toFixed(1) || '0.0'}%
            </div>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem', marginTop: '2px' }}>
              {status?.successful_detections || 0} / {status?.total_frames_processed || 0} frames
            </div>
          </div>

          <div style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.68rem' }}>MEAN RADIAL ERROR</div>
            <div style={{ color: '#00e5ff', fontWeight: 700, fontSize: '0.92rem' }}>
              {status?.mean_radial_error_px?.toFixed(3) || '0.000'} px
            </div>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.65rem', marginTop: '2px' }}>
              Sub-pixel average
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
