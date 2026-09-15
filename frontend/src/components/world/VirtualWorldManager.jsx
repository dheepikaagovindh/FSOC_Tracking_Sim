import React, { useState, useEffect, useRef } from 'react';
import WorldStatus from './WorldStatus';
import PlatformStatus from './PlatformStatus';
import WorldTelemetry from './WorldTelemetry';
import WorldPreview from './WorldPreview';
import {
  fetchWorldStatus,
  fetchWorldState,
  initializeWorld,
  resetWorld,
  stepWorld,
} from '../../services/worldApi';

export default function VirtualWorldManager({ backendOnline }) {
  const [worldState, setWorldState] = useState(null);
  const [worldStatus, setWorldStatus] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [isStepping, setIsStepping] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const isPlayingRef = useRef(isPlaying);
  isPlayingRef.current = isPlaying;

  const speedRef = useRef(playbackSpeed);
  speedRef.current = playbackSpeed;

  // Poll / load initial world state
  const refreshState = async () => {
    try {
      const [st, stus] = await Promise.all([
        fetchWorldState().catch(() => null),
        fetchWorldStatus().catch(() => null),
      ]);
      if (st) setWorldState(st);
      if (stus) setWorldStatus(stus);
      setErrorMsg(null);
    } catch (err) {
      console.error('Failed to load world state:', err);
    }
  };

  useEffect(() => {
    refreshState();
  }, []);

  // Step simulation
  const handleStep = async () => {
    setIsStepping(true);
    try {
      const newState = await stepWorld();
      setWorldState(newState);
      if (worldStatus) {
        setWorldStatus({
          ...worldStatus,
          current_time: newState.timestamp,
        });
      }
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Step failed: ${err.message}`);
    } finally {
      setIsStepping(false);
    }
  };

  // Reset simulation
  const handleReset = async () => {
    setIsPlaying(false);
    try {
      const resetState = await resetWorld();
      setWorldState(resetState);
      if (worldStatus) {
        setWorldStatus({
          ...worldStatus,
          current_time: 0.0,
        });
      }
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Reset failed: ${err.message}`);
    }
  };

  // Re-initialize world
  const handleInitialize = async () => {
    try {
      const initState = await initializeWorld();
      setWorldState(initState);
      await refreshState();
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(`Initialization failed: ${err.message}`);
    }
  };

  // Play / Pause continuous stepping loop
  useEffect(() => {
    let intervalId = null;
    if (isPlaying) {
      const intervalMs = Math.max(20, Math.floor(1000 / (30 * speedRef.current)));
      intervalId = setInterval(async () => {
        if (!isPlayingRef.current) return;
        try {
          const newState = await stepWorld();
          setWorldState(newState);
          setWorldStatus((prev) => prev ? { ...prev, current_time: newState.timestamp } : prev);
          // Check if duration exceeded
          if (worldStatus?.duration && newState.timestamp >= worldStatus.duration) {
            setIsPlaying(false);
          }
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
      {/* Left Column: World Status, Platforms & Spatial Telemetry */}
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

        {/* 1. Simulation Status & Clock Controls */}
        <WorldStatus
          status={worldStatus}
          isPlaying={isPlaying}
          playbackSpeed={playbackSpeed}
          onPlayToggle={() => setIsPlaying(!isPlaying)}
          onStep={handleStep}
          onReset={handleReset}
          onInitialize={handleInitialize}
          onSpeedChange={setPlaybackSpeed}
          isStepping={isStepping}
        />

        {/* 2. Platform 3D Kinematics */}
        <PlatformStatus
          cameraPlatform={worldState?.camera_platform}
          beaconPlatform={worldState?.beacon_platform}
        />

        {/* 3. Ground-Truth Relative Geometry */}
        <WorldTelemetry
          geometry={worldState?.relative_geometry}
        />
      </div>

      {/* Right Column: 2D Tactical Radar Preview */}
      <div className="summary-column">
        <WorldPreview
          cameraPlatform={worldState?.camera_platform}
          beaconPlatform={worldState?.beacon_platform}
          geometry={worldState?.relative_geometry}
        />
      </div>
    </div>
  );
}
