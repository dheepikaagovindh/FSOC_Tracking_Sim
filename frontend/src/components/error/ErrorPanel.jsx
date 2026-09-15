import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Crosshair, RefreshCw, AlertCircle, Play, Pause, RotateCcw, FastForward } from 'lucide-react';
import AlignmentStatus from './AlignmentStatus';
import ErrorTelemetry from './ErrorTelemetry';
import ErrorControls from './ErrorControls';
import AlignmentOverlay from './AlignmentOverlay';
import {
  fetchErrorStatus,
  fetchErrorResult,
  fetchErrorTelemetry,
  updateErrorConfig,
  resetError,
  executeErrorCalculation,
} from '../../services/errorApi';

export default function ErrorPanel({ backendOnline }) {
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [telemetry, setTelemetry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [cacheBust, setCacheBust] = useState(Date.now());

  const isRunningRef = useRef(isRunning);
  isRunningRef.current = isRunning;

  // Fetch all error calculation telemetry and status packets
  const loadData = useCallback(async () => {
    try {
      const [statusData, resultData, telemetryData] = await Promise.all([
        fetchErrorStatus(),
        fetchErrorResult(),
        fetchErrorTelemetry(),
      ]);
      setStatus(statusData);
      setResult(resultData);
      setTelemetry(telemetryData);
      setCacheBust(Date.now());
      setError(null);
    } catch (err) {
      console.error('Error fetching alignment error data:', err);
      setError(err.message || 'Failed to communicate with alignment engine');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Real-time animation / calculation loop
  useEffect(() => {
    let interval = null;
    if (isRunning) {
      interval = setInterval(async () => {
        try {
          await executeErrorCalculation();
          await loadData();
        } catch (err) {
          console.error('Alignment loop step error:', err);
        }
      }, 100); // 10 Hz refresh
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning, loadData]);

  const handleUpdateConfig = async (newConfig) => {
    const updatedStatus = await updateErrorConfig(newConfig);
    setStatus(updatedStatus);
    await loadData();
  };

  const handleReset = async () => {
    setIsRunning(false);
    const resetRes = await resetError();
    setResult(resetRes);
    await loadData();
  };

  const handleStep = async () => {
    await executeErrorCalculation();
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
            <Crosshair size={22} className="text-cyan-400" />
            <span>MODULE 7: ERROR CALCULATION & BORESIGHT ALIGNMENT</span>
          </h2>
          <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: '#94a3b8' }}>
            Pinhole Angular Transformations, Boresight Pointing Errors, and Alignment Lock Monitoring
          </p>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          style={{ fontSize: '0.75rem', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '4px' }}
          onClick={loadData}
          disabled={loading || isRunning}
          title="Refresh alignment status"
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
        {/* Alignment State & Lock Condition Header */}
        <AlignmentStatus status={status} result={result} telemetry={telemetry} />

        {/* Viewfinder and Boresight HUD Overlay */}
        <AlignmentOverlay
          telemetry={telemetry}
          result={result}
          isRunning={isRunning}
          cacheBust={cacheBust}
        />

        {/* Kinematic Error Telemetry Cards */}
        <ErrorTelemetry result={result} telemetry={telemetry} />

        {/* Interactive Tolerances & Tuning */}
        <ErrorControls
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
