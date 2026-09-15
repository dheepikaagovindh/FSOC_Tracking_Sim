import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipForward, RotateCcw, RefreshCw, Eye, Camera, Activity } from 'lucide-react';
import CameraFocalPlane from './CameraFocalPlane';
import GimbalManualControl from './GimbalManualControl';
import CameraTelemetryCard from './CameraTelemetryCard';
import CameraIntrinsicsCard from './CameraIntrinsicsCard';
import {
  fetchCameraStatus,
  fetchCameraFrame,
  fetchCameraTelemetry,
  updateCameraPose,
  resetCameraPose,
  initializeCamera,
  captureCameraFrame,
} from '../../services/cameraApi';
import { stepWorld, fetchWorldState, resetWorld } from '../../services/worldApi';

export default function VirtualCameraManager({ backendOnline }) {
  const [cameraStatus, setCameraStatus] = useState(null);
  const [cameraFrame, setCameraFrame] = useState(null);
  const [cameraTelemetry, setCameraTelemetry] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [isStepping, setIsStepping] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [imageTimestamp, setImageTimestamp] = useState(Date.now());

  const isPlayingRef = useRef(isPlaying);
  isPlayingRef.current = isPlaying;

  const speedRef = useRef(playbackSpeed);
  speedRef.current = playbackSpeed;

  // Refresh all camera data
  const refreshCamera = async () => {
    try {
      const [st, frm, telem] = await Promise.all([
        fetchCameraStatus().catch(() => null),
        fetchCameraFrame().catch(() => null),
        fetchCameraTelemetry().catch(() => null),
      ]);
      if (st) setCameraStatus(st);
      if (frm) setCameraFrame(frm);
      if (telem) setCameraTelemetry(telem);
      setImageTimestamp(Date.now());
      setErrorMsg(null);
    } catch (err) {
      console.error('Failed to load camera data:', err);
    }
  };

  useEffect(() => {
    refreshCamera();
  }, []);

  // Single step
  const handleStep = async () => {
    setIsStepping(true);
    try {
      await stepWorld();
      const [frm, telem] = await Promise.all([
        fetchCameraFrame(),
        fetchCameraTelemetry(),
      ]);
      setCameraFrame(frm);
      setCameraTelemetry(telem);
      setImageTimestamp(Date.now());
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Step failed: ${err.message}`);
    } finally {
      setIsStepping(false);
    }
  };

  // Capture frame
  const handleCapture = async () => {
    try {
      const frm = await captureCameraFrame();
      const telem = await fetchCameraTelemetry();
      setCameraFrame(frm);
      setCameraTelemetry(telem);
      setImageTimestamp(Date.now());
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Capture failed: ${err.message}`);
    }
  };

  // Reset gimbal orientation
  const handleResetPose = async () => {
    try {
      const frm = await resetCameraPose();
      const [st, telem] = await Promise.all([
        fetchCameraStatus(),
        fetchCameraTelemetry(),
      ]);
      if (st) setCameraStatus(st);
      setCameraFrame(frm);
      setCameraTelemetry(telem);
      setImageTimestamp(Date.now());
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Reset failed: ${err.message}`);
    }
  };

  // Update pan/tilt
  const handlePoseChange = async (panDeg, tiltDeg) => {
    try {
      const updatedPose = await updateCameraPose(panDeg, tiltDeg);
      setCameraStatus((prev) => prev ? { ...prev, pan_deg: updatedPose.pan_deg, tilt_deg: updatedPose.tilt_deg } : prev);
      const [frm, telem] = await Promise.all([
        fetchCameraFrame(),
        fetchCameraTelemetry(),
      ]);
      setCameraFrame(frm);
      setCameraTelemetry(telem);
      setImageTimestamp(Date.now());
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Pose update failed: ${err.message}`);
    }
  };

  // Auto-center line of sight onto beacon
  const handleAutoCenter = async () => {
    try {
      const worldState = await fetchWorldState();
      if (!worldState || !worldState.relative_geometry) return;
      const { azimuth, elevation } = worldState.relative_geometry;
      await handlePoseChange(azimuth, elevation);
    } catch (err) {
      setErrorMsg(`Auto-center failed: ${err.message}`);
    }
  };

  // Re-initialize camera
  const handleInitialize = async () => {
    try {
      await initializeCamera();
      await refreshCamera();
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Initialization failed: ${err.message}`);
    }
  };

  // Continuous playback loop
  useEffect(() => {
    let intervalId = null;
    if (isPlaying) {
      const intervalMs = Math.max(33, Math.floor(1000 / (30 * speedRef.current)));
      intervalId = setInterval(async () => {
        if (!isPlayingRef.current) return;
        try {
          await stepWorld();
          const [frm, telem] = await Promise.all([
            fetchCameraFrame(),
            fetchCameraTelemetry(),
          ]);
          setCameraFrame(frm);
          setCameraTelemetry(telem);
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
    <div className="dashboard-layout" style={{ gridTemplateColumns: '1fr 440px' }}>
      {/* Left Main View: Viewfinder & Gimbal Controls */}
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
                title="Advance simulation by 1 frame (1/FPS)"
              >
                <SkipForward size={14} />
                <span>STEP</span>
              </button>

              {/* Capture */}
              <button
                type="button"
                className="btn btn-outline"
                onClick={handleCapture}
                title="Trigger immediate frame render & capture"
              >
                <Camera size={14} />
                <span>CAPTURE</span>
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
                title="Synchronize camera with active scenario"
              >
                <RefreshCw size={12} style={{ marginRight: '4px' }} />
                SYNC
              </button>
            </div>
          </div>
        </div>

        {/* 1. Synthetic Optical Focal Plane Viewfinder */}
        <CameraFocalPlane
          frame={cameraFrame}
          intrinsics={cameraStatus?.intrinsics}
          timestamp={cameraFrame?.timestamp}
          imageTimestamp={imageTimestamp}
        />

        {/* 2. Gimbal Pan-Tilt Steering Controls */}
        <GimbalManualControl
          panDeg={cameraStatus?.pan_deg ?? cameraFrame?.camera_orientation?.pan_deg ?? 0.0}
          tiltDeg={cameraStatus?.tilt_deg ?? cameraFrame?.camera_orientation?.tilt_deg ?? 0.0}
          onPoseChange={handlePoseChange}
          onResetPose={handleResetPose}
          onAutoCenter={handleAutoCenter}
          disabled={isPlaying}
        />
      </div>

      {/* Right Column: Telemetry & Intrinsics */}
      <div className="summary-column">
        {/* 1. Real-Time Tracking Telemetry */}
        <CameraTelemetryCard
          telemetry={cameraTelemetry}
          intrinsics={cameraStatus?.intrinsics}
        />

        {/* 2. Optical Intrinsics & Sensor Specs */}
        <CameraIntrinsicsCard
          intrinsics={cameraStatus?.intrinsics}
        />
      </div>
    </div>
  );
}
