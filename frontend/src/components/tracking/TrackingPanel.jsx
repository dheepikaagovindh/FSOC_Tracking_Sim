import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Target, RefreshCw, AlertCircle, Play, Pause, RotateCcw, FastForward } from 'lucide-react';
import TrackingStatus from './TrackingStatus';
import TrackingTelemetry from './TrackingTelemetry';
import TrackingControls from './TrackingControls';
import TrackingOverlay from './TrackingOverlay';
import {
  fetchTrackingStatus,
  fetchTrackingResult,
  fetchTrackingTelemetry,
  updateTrackingConfig,
  resetTracking,
  executeTrackingStep,
} from '../../services/trackingApi';

export default function TrackingPanel({ backendOnline }) {
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [telemetry, setTelemetry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [cacheBust, setCacheBust] = useState(Date.now());

  const isRunningRef = useRef(isRunning);
  isRunningRef.current = isRunning;

  // Fetch all tracking telemetry and status packets
  const loadData = useCallback(async () => {
    try {
      const [statusData, resultData, telemetryData] = await Promise.all([
        fetchTrackingStatus(),
        fetchTrackingResult(),
        fetchTrackingTelemetry(),
      ]);
      setStatus(statusData);
      setResult(resultData);
      setTelemetry(telemetryData);
      setCacheBust(Date.now());
      setError(null);
    } catch (err) {
      console.error('Error fetching tracking data:', err);
      setError(err.message || 'Failed to communicate with tracking engine');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Real-time animation / tracking loop
  useEffect(() => {
    let interval = null;
    if (isRunning) {
      interval = setInterval(async () => {
        try {
          await executeTrackingStep();
          await loadData();
        } catch (err) {
          console.error('Loop step error:', err);
        }
      }, 100); // 10 Hz refresh
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning, loadData]);

  const handleUpdateConfig = async (newConfig) => {
    const updatedStatus = await updateTrackingConfig(newConfig);
    setStatus(updatedStatus);
    await loadData();
  };

  const handleReset = async () => {
    setIsRunning(false);
    const resetRes = await resetTracking();
    setResult(resetRes);
    await loadData();
  };

  const handleStep = async () => {
    await executeTrackingStep();
    await loadData();
  };

  const handleToggleRunning = () => {
    setIsRunning((prev) => !prev);
  };

  if (!backendOnline) {
    return (
      <div className="module-panel-container">
        <div className="alert alert-danger" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem' }}>
          <AlertCircle size={20} />
          <div>
            <strong>Backend Offline</strong>
            <p style={{ margin: 0, fontSize: '0.85rem' }}>
              Cannot connect to FSOC Simulator API. Please ensure the FastAPI backend is running on port 8000.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="module-panel-container">
      {/* Top Banner / Breadcrumb */}
      <div className="module-banner" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Target size={22} className="text-cyan-400" />
            <span>MODULE 6: BEACON TRACKING & MOTION PREDICTION</span>
          </h2>
          <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: '#94a3b8' }}>
            2D Constant-Velocity Kalman Filter State Estimator, Dropout Coasting, and Lead Extrapolation
          </p>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          style={{ fontSize: '0.75rem', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '4px' }}
          onClick={loadData}
          disabled={loading || isRunning}
          title="Refresh tracking status"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="alert alert-warning" style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem' }}>
          <AlertCircle size={16} />
          <span style={{ fontSize: '0.85rem' }}>{error}</span>
        </div>
      )}

      {/* Grid Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.25rem' }}>
        {/* State & Confidence Header */}
        <TrackingStatus status={status} result={result} telemetry={telemetry} />

        {/* Viewfinder and HUD Overlay */}
        <TrackingOverlay
          telemetry={telemetry}
          result={result}
          isRunning={isRunning}
          cacheBust={cacheBust}
        />

        {/* Kinematic Telemetry Cards */}
        <TrackingTelemetry result={result} telemetry={telemetry} />

        {/* Interactive Controls & Tuning */}
        <TrackingControls
          config={status?.config}
          onUpdateConfig={handleUpdateConfig}
          onReset={handleReset}
          onStep={handleStep}
          isRunning={isRunning}
          onToggleRunning={handleToggleRunning}
          disabled={!backendOnline}
        />
      </div>
    </div>
  );
}
