import React from 'react';
import { Play, Pause, SkipForward, RotateCcw, RefreshCw, Clock, Activity, Cpu } from 'lucide-react';

export default function WorldStatus({
  status,
  isPlaying,
  playbackSpeed,
  onPlayToggle,
  onStep,
  onReset,
  onInitialize,
  onSpeedChange,
  isStepping,
}) {
  const isInit = status?.initialized;
  const currentTime = status?.current_time || 0.0;
  const duration = status?.duration || 30.0;
  const fps = status?.fps || 30.0;
  const progressPercent = Math.min(100, Math.max(0, (currentTime / (duration || 1)) * 100));

  return (
    <div className="hud-card active-card">
      <div className="card-header">
        <div className="card-title-group">
          <Cpu size={18} />
          <h2>Virtual World Simulation Clock & Controls</h2>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className={`status-pill ${isInit ? 'ready' : 'error'}`}>
            <span className="pulse-dot" />
            <span>{isInit ? 'WORLD INITIALIZED' : 'UNINITIALIZED'}</span>
          </span>
          <span className="card-badge">{status?.scenario_name || 'Active Scenario'}</span>
        </div>
      </div>
      <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Simulation Clock & Progress Bar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#38bdf8' }}>
              <Clock size={16} />
              <span>TIME: <strong>{currentTime.toFixed(3)} s</strong></span>
            </div>
            <div style={{ color: '#94a3b8' }}>
              <span>LIMIT: {duration.toFixed(1)} s @ {fps.toFixed(0)} FPS (dt={(1 / fps).toFixed(4)}s)</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div style={{
            height: '6px',
            background: '#1e293b',
            borderRadius: '3px',
            overflow: 'hidden',
            position: 'relative',
          }}>
            <div style={{
              height: '100%',
              width: `${progressPercent}%`,
              background: 'linear-gradient(90deg, #06b6d4, #10b981)',
              transition: 'width 0.1s linear',
              boxShadow: '0 0 10px rgba(6, 182, 212, 0.5)',
            }} />
          </div>
        </div>

        {/* Action Controls Toolbar */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              type="button"
              className={`btn ${isPlaying ? 'btn-danger-outline' : 'btn-emerald'}`}
              onClick={onPlayToggle}
              disabled={!isInit}
            >
              {isPlaying ? <Pause size={15} /> : <Play size={15} />}
              <span>{isPlaying ? 'PAUSE' : 'PLAY SIMULATION'}</span>
            </button>

            <button
              type="button"
              className="btn btn-cyan"
              onClick={onStep}
              disabled={!isInit || isPlaying || isStepping}
            >
              <SkipForward size={15} />
              <span>STEP (+1 FRAME)</span>
            </button>

            <button
              type="button"
              className="btn btn-outline"
              onClick={onReset}
              disabled={!isInit}
            >
              <RotateCcw size={15} />
              <span>RESET (T=0)</span>
            </button>

            <button
              type="button"
              className="btn btn-outline"
              onClick={onInitialize}
            >
              <RefreshCw size={15} />
              <span>RE-INITIALIZE</span>
            </button>
          </div>

          {/* Playback Speed Multiplier */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>SPEED:</span>
            {[1, 2, 5].map((spd) => (
              <button
                key={spd}
                type="button"
                className={`btn btn-outline ${playbackSpeed === spd ? 'active-speed' : ''}`}
                style={{
                  padding: '4px 8px',
                  fontSize: '0.72rem',
                  borderColor: playbackSpeed === spd ? '#22d3ee' : undefined,
                  color: playbackSpeed === spd ? '#22d3ee' : undefined,
                }}
                onClick={() => onSpeedChange(spd)}
              >
                {spd}x
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
