import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipForward, RotateCcw, RefreshCw, Zap, Camera } from 'lucide-react';
import DisturbancePreview from './DisturbancePreview';
import DisturbanceControls from './DisturbanceControls';
import DisturbanceStatus from './DisturbanceStatus';
import {
  fetchDisturbanceStatus,
  fetchDisturbanceFrame,
  fetchDisturbanceTelemetry,
  updateDisturbanceConfig,
  resetDisturbance,
  initializeDisturbance,
  processDisturbanceFrame,
} from '../../services/disturbanceApi';
import { fetchCameraFrame, fetchCameraStatus } from '../../services/cameraApi';
import { stepWorld } from '../../services/worldApi';

export default function DisturbancePanel({ backendOnline }) {
  const [disturbanceStatus, setDisturbanceStatus] = useState(null);
  const [disturbanceFrame, setDisturbanceFrame] = useState(null);
  const [disturbanceTelemetry, setDisturbanceTelemetry] = useState(null);
  const [cameraFrame, setCameraFrame] = useState(null);
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
      const [distSt, distFrm, distTelem, camFrm, camSt] = await Promise.all([
        fetchDisturbanceStatus().catch(() => null),
        fetchDisturbanceFrame().catch(() => null),
        fetchDisturbanceTelemetry().catch(() => null),
        fetchCameraFrame().catch(() => null),
        fetchCameraStatus().catch(() => null),
      ]);
      if (distSt) setDisturbanceStatus(distSt);
      if (distFrm) setDisturbanceFrame(distFrm);
      if (distTelem) setDisturbanceTelemetry(distTelem);
      if (camFrm) setCameraFrame(camFrm);
      if (camSt) setCameraStatus(camSt);
      setImageTimestamp(Date.now());
      setErrorMsg(null);
    } catch (err) {
      console.error('Failed to load disturbance data:', err);
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
      await refreshAll();
    } catch (err) {
      setErrorMsg(`Step failed: ${err.message}`);
    } finally {
      setIsStepping(false);
    }
  };

  const handleProcess = async () => {
    try {
      const frm = await processDisturbanceFrame();
      const telem = await fetchDisturbanceTelemetry();
      setDisturbanceFrame(frm);
      setDisturbanceTelemetry(telem);
      setImageTimestamp(Date.now());
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Process failed: ${err.message}`);
    }
  };

  const handleUpdateConfig = async (newConfig) => {
    try {
      const updatedStatus = await updateDisturbanceConfig(newConfig);
      setDisturbanceStatus(updatedStatus);
      await refreshAll();
    } catch (err) {
      setErrorMsg(`Update failed: ${err.message}`);
    }
  };

  const handleReset = async () => {
    try {
      await resetDisturbance();
      await refreshAll();
    } catch (err) {
      setErrorMsg(`Reset failed: ${err.message}`);
    }
  };

  const handleInitialize = async () => {
    try {
      await initializeDisturbance();
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
          const [distFrm, distTelem, camFrm] = await Promise.all([
            fetchDisturbanceFrame(),
            fetchDisturbanceTelemetry(),
            fetchCameraFrame(),
          ]);
          setDisturbanceFrame(distFrm);
          setDisturbanceTelemetry(distTelem);
          setCameraFrame(camFrm);
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
      {/* Left Column: Side-by-Side Comparative View & Controls */}
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
                title="Advance simulation and process disturbance by 1 frame"
              >
                <SkipForward size={14} />
                <span>STEP</span>
              </button>

              {/* Process */}
              <button
                type="button"
                className="btn btn-outline"
                onClick={handleProcess}
                title="Re-run disturbance pipeline on current clean frame"
              >
                <Zap size={14} />
                <span>PROCESS</span>
              </button>

              {/* Speed multiplier */}
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
                t = {(cameraFrame?.timestamp || 0).toFixed(2)}s
              </div>
              <button
                type="button"
                className="btn btn-outline"
                onClick={handleInitialize}
                style={{ fontSize: '0.72rem', padding: '4px 8px' }}
                title="Synchronize disturbance engine with scenario"
              >
                <RefreshCw size={12} style={{ marginRight: '4px' }} />
                SYNC
              </button>
            </div>
          </div>
        </div>

        {/* 1. Side-by-Side Comparative Viewfinder */}
        <DisturbancePreview
          cameraFrame={cameraFrame}
          disturbanceFrame={disturbanceFrame}
          imageTimestamp={imageTimestamp}
          intrinsics={cameraStatus?.intrinsics}
        />

        {/* 2. Interactive Parameter Configurator */}
        <DisturbanceControls
          config={disturbanceStatus?.config}
          onUpdateConfig={handleUpdateConfig}
          onReset={handleReset}
          disabled={isPlaying}
        />
      </div>

      {/* Right Column: Telemetry & Status Diagnostics */}
      <div className="summary-column">
        <DisturbanceStatus
          telemetry={disturbanceTelemetry}
          status={disturbanceStatus}
        />
      </div>
    </div>
  );
}
