import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipForward, RotateCcw, RefreshCw, Zap, Scan } from 'lucide-react';
import DetectionViewfinder from './DetectionViewfinder';
import DetectionOverlay from './DetectionOverlay';
import DetectionStatus from './DetectionStatus';
import DetectionTelemetry from './DetectionTelemetry';
import DetectionControls from './DetectionControls';
import DetectionMetricsCard from './DetectionMetricsCard';
import {
  fetchDetectionStatus,
  fetchDetectionResult,
  fetchDetectionTelemetry,
  updateDetectionConfig,
  resetDetection,
  initializeDetection,
  executeDetection,
} from '../../services/detectionApi';
import { fetchDisturbanceFrame, processDisturbanceFrame } from '../../services/disturbanceApi';
import { fetchCameraStatus } from '../../services/cameraApi';
import { stepWorld } from '../../services/worldApi';

export default function DetectionPanel({ backendOnline }) {
  const [detectionStatus, setDetectionStatus] = useState(null);
  const [detectionResult, setDetectionResult] = useState(null);
  const [detectionTelemetry, setDetectionTelemetry] = useState(null);
  const [disturbanceFrame, setDisturbanceFrame] = useState(null);
  const [cameraStatus, setCameraStatus] = useState(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [isStepping, setIsStepping] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [imageTimestamp, setImageTimestamp] = useState(Date.now());

  const isPlayingRef = useRef(isPlaying);
  isPlayingRef.current = isPlaying;

  const speedRef = useRef(playbackSpeed);
  speedRef.current = playbackSpeed;

  const refreshAll = async () => {
    try {
      const [detSt, detRes, detTelem, distFrm, camSt] = await Promise.all([
        fetchDetectionStatus().catch(() => null),
        fetchDetectionResult().catch(() => null),
        fetchDetectionTelemetry().catch(() => null),
        fetchDisturbanceFrame().catch(() => null),
        fetchCameraStatus().catch(() => null),
      ]);
      if (detSt) setDetectionStatus(detSt);
      if (detRes) setDetectionResult(detRes);
      if (detTelem) setDetectionTelemetry(detTelem);
      if (distFrm) setDisturbanceFrame(distFrm);
      if (camSt) setCameraStatus(camSt);
      setImageTimestamp(Date.now());
      setErrorMsg(null);
    } catch (err) {
      console.error('Failed to load detection data:', err);
    }
  };

  useEffect(() => {
    refreshAll();
  }, []);

  const handleStep = async () => {
    setIsStepping(true);
    try {
      await stepWorld();
      await processDisturbanceFrame();
      const detRes = await executeDetection();
      const [detSt, detTelem, distFrm] = await Promise.all([
        fetchDetectionStatus(),
        fetchDetectionTelemetry(),
        fetchDisturbanceFrame(),
      ]);
      setDetectionResult(detRes);
      setDetectionStatus(detSt);
      setDetectionTelemetry(detTelem);
      setDisturbanceFrame(distFrm);
      setImageTimestamp(Date.now());
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Step failed: ${err.message}`);
    } finally {
      setIsStepping(false);
    }
  };

  const handleProcess = async () => {
    try {
      const detRes = await executeDetection();
      const [detSt, detTelem] = await Promise.all([
        fetchDetectionStatus(),
        fetchDetectionTelemetry(),
      ]);
      setDetectionResult(detRes);
      setDetectionStatus(detSt);
      setDetectionTelemetry(detTelem);
      setImageTimestamp(Date.now());
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Detection execution failed: ${err.message}`);
    }
  };

  const handleUpdateConfig = async (newConfig) => {
    try {
      const updatedStatus = await updateDetectionConfig(newConfig);
      setDetectionStatus(updatedStatus);
      await refreshAll();
    } catch (err) {
      setErrorMsg(`Update failed: ${err.message}`);
    }
  };

  const handleReset = async () => {
    try {
      await resetDetection();
      await refreshAll();
    } catch (err) {
      setErrorMsg(`Reset failed: ${err.message}`);
    }
  };

  const handleInitialize = async () => {
    try {
      await initializeDetection();
      await refreshAll();
    } catch (err) {
      setErrorMsg(`Initialize failed: ${err.message}`);
    }
  };

  // Playback stepping loop
  useEffect(() => {
    let intervalId = null;
    if (isPlaying) {
      const intervalMs = Math.max(33, Math.floor(1000 / (30 * speedRef.current)));
      intervalId = setInterval(async () => {
        if (!isPlayingRef.current) return;
        try {
          await stepWorld();
          await processDisturbanceFrame();
          const detRes = await executeDetection();
          const [detSt, detTelem, distFrm] = await Promise.all([
            fetchDetectionStatus(),
            fetchDetectionTelemetry(),
            fetchDisturbanceFrame(),
          ]);
          setDetectionResult(detRes);
          setDetectionStatus(detSt);
          setDetectionTelemetry(detTelem);
          setDisturbanceFrame(distFrm);
          setImageTimestamp(Date.now());
        } catch (err) {
          setIsPlaying(false);
          setErrorMsg(`Simulation stopped: ${err.message}`);
        }
      }, intervalMs);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isPlaying, playbackSpeed]);

  return (
    <div className="dashboard-layout" style={{ gridTemplateColumns: '1fr 400px' }}>
      {/* Left Column: Viewfinder & Controls */}
      <div className="config-column">
        {errorMsg && (
          <div style={{
            padding: '12px 18px',
            borderRadius: '8px',
            background: 'rgba(239, 68, 68, 0.2)',
            border: '1px solid #ef4444',
            color: '#fca5a5',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.82rem',
          }}>
            {errorMsg}
          </div>
        )}

        {/* Playback & Viewfinder Control Bar */}
        <div className="hud-card" style={{ padding: '10px 16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {/* Play / Pause */}
              <button
                type="button"
                className={`btn ${isPlaying ? 'btn-danger' : 'btn-primary'}`}
                onClick={() => setIsPlaying(!isPlaying)}
                style={{ minWidth: '95px' }}
              >
                {isPlaying ? <Pause size={14} /> : <Play size={14} />}
                <span>{isPlaying ? 'PAUSE' : 'PLAY'}</span>
              </button>

              {/* Step */}
              <button
                type="button"
                className="btn btn-outline"
                onClick={handleStep}
                disabled={isPlaying || isStepping}
                title="Advance world simulation, disturbance, and detection by 1 frame"
              >
                <SkipForward size={14} />
                <span>STEP</span>
              </button>

              {/* Detect Frame */}
              <button
                type="button"
                className="btn btn-outline"
                onClick={handleProcess}
                title="Execute centroiding on current sensor frame"
              >
                <Scan size={14} />
                <span>DETECT</span>
              </button>

              {/* Speed Multiplier */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginLeft: '6px' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>SPD:</span>
                {[1, 2, 5].map((spd) => (
                  <button
                    key={spd}
                    type="button"
                    className={`btn btn-outline ${playbackSpeed === spd ? 'btn-active' : ''}`}
                    onClick={() => setPlaybackSpeed(spd)}
                    style={{
                      fontSize: '0.68rem',
                      padding: '2px 6px',
                      background: playbackSpeed === spd ? 'rgba(0, 229, 255, 0.2)' : 'transparent',
                      borderColor: playbackSpeed === spd ? 'var(--color-primary)' : 'var(--color-border)',
                    }}
                  >
                    {spd}x
                  </button>
                ))}
              </div>
            </div>

            {/* Time readout & Sync */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--color-primary)' }}>
                t = {(detectionResult?.timestamp || 0).toFixed(2)}s
              </div>
              <button
                type="button"
                className="btn btn-outline"
                onClick={handleInitialize}
                style={{ fontSize: '0.72rem', padding: '4px 8px' }}
                title="Synchronize detector with current scenario"
              >
                <RefreshCw size={12} style={{ marginRight: '4px' }} />
                SYNC
              </button>
            </div>
          </div>
        </div>

        {/* 1. Interactive Centroid Viewfinder */}
        <DetectionViewfinder
          detectionResult={detectionResult}
          detectionTelemetry={detectionTelemetry}
          disturbanceFrame={disturbanceFrame}
          imageTimestamp={imageTimestamp}
          intrinsics={cameraStatus?.intrinsics}
        />

        {/* 2. Detection Algorithm & Parameter Controls */}
        <DetectionControls
          config={detectionStatus?.config}
          onUpdateConfig={handleUpdateConfig}
          onReset={handleReset}
          disabled={isPlaying}
        />
      </div>

      {/* Right Column: Telemetry & Status Cards */}
      <div className="summary-column" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <DetectionStatus
          detectionResult={detectionResult}
          detectionStatus={detectionStatus}
        />
        <DetectionTelemetry
          detectionResult={detectionResult}
          detectionStatus={detectionStatus}
          detectionTelemetry={detectionTelemetry}
        />
        <DetectionMetricsCard
          detectionResult={detectionResult}
          detectionStatus={detectionStatus}
          detectionTelemetry={detectionTelemetry}
        />
      </div>
    </div>
  );
}
