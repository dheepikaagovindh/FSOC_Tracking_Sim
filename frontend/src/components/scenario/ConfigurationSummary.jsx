import React, { useState } from 'react';
import { Activity, RotateCcw, Send, Play, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function ConfigurationSummary({
  config,
  onReset,
  onApply,
  onStartSimulation,
  isApplying,
  validationResult,
  clientErrors = [],
}) {
  const [showReadyModal, setShowReadyModal] = useState(false);
  const [initContext, setInitContext] = useState(null);

  const errors = [...clientErrors, ...(validationResult?.errors || [])];
  const isValid = errors.length === 0;

  const handleStart = async () => {
    try {
      const res = await onStartSimulation();
      setInitContext(res.simulation_context);
      setShowReadyModal(true);
    } catch (err) {
      // Error handled by parent alert
    }
  };

  const getSeverityClass = (sev) => {
    switch (sev?.toLowerCase()) {
      case 'high': return 'highlight-red';
      case 'medium': return 'highlight-amber';
      case 'low': return 'highlight-cyan';
      default: return '';
    }
  };

  return (
    <div className="hud-card active-card">
      <div className="card-header">
        <div className="card-title-group">
          <Activity size={18} />
          <h2>Live Configuration HUD</h2>
        </div>
        <span className="card-badge">TELEMETRY SUMMARY</span>
      </div>
      <div className="card-body summary-container">
        {/* Telemetry Summary Table */}
        <table className="telemetry-table">
          <tbody>
            <tr className="telemetry-row">
              <td className="telemetry-label">Scenario Name</td>
              <td className="telemetry-value highlight-cyan">{config.scenario_name || 'Custom'}</td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Camera Resolution</td>
              <td className="telemetry-value">{config.camera?.width} × {config.camera?.height} px</td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Camera FOV</td>
              <td className="telemetry-value">{config.camera?.horizontal_fov_deg}° H × {config.camera?.vertical_fov_deg}° V</td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Camera Platform Motion</td>
              <td className="telemetry-value highlight-cyan">{config.camera_platform?.motion_profile?.toUpperCase()}</td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Beacon Platform Motion</td>
              <td className="telemetry-value highlight-cyan">{config.beacon_platform?.motion_profile?.toUpperCase()}</td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Beacon Trajectory</td>
              <td className="telemetry-value">{config.beacon?.trajectory?.toUpperCase()}</td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Disturbance Severity</td>
              <td className={`telemetry-value ${getSeverityClass(config.disturbances?.severity)}`}>
                {config.disturbances?.severity?.toUpperCase()}
              </td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Vibration</td>
              <td className="telemetry-value">
                {config.disturbances?.vibration_enabled ? `ON (${config.disturbances.vibration_magnitude} px)` : 'OFF'}
              </td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Sensor Noise</td>
              <td className="telemetry-value">
                {config.disturbances?.noise_enabled ? `ON (σ=${config.disturbances.noise_magnitude})` : 'OFF'}
              </td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Optical Blur</td>
              <td className="telemetry-value">
                {config.disturbances?.blur_enabled ? `ON (${config.disturbances.blur_strength} σ)` : 'OFF'}
              </td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Beacon Dropout</td>
              <td className="telemetry-value">
                {config.disturbances?.dropout_enabled ? `ON (${(config.disturbances.dropout_probability * 100).toFixed(0)}%)` : 'OFF'}
              </td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Simulation Duration</td>
              <td className="telemetry-value">{config.simulation?.duration} s</td>
            </tr>
            <tr className="telemetry-row">
              <td className="telemetry-label">Frame Rate</td>
              <td className="telemetry-value highlight-cyan">{config.simulation?.fps} FPS</td>
            </tr>
          </tbody>
        </table>

        {/* Validation Errors Callout */}
        {errors.length > 0 && (
          <div className="validation-alert-box">
            <div className="validation-alert-header">
              <AlertTriangle size={16} />
              <span>Validation Issues ({errors.length})</span>
            </div>
            <ul className="validation-error-list">
              {errors.map((err, idx) => (
                <li key={idx} className="validation-error-item">{err}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Validated Confirmation Badge */}
        {isValid && (
          <div className="ready-confirmation-box">
            <CheckCircle2 size={24} color="#10b981" />
            <div className="ready-confirmation-text">
              <h4>✓ SCENARIO READY</h4>
              <p>Parameters validated and compliant with simulation bounds.</p>
            </div>
          </div>
        )}

        {/* Action Button Stack */}
        <div className="summary-actions-stack">
          <button
            type="button"
            className="btn btn-cyan"
            onClick={onApply}
            disabled={isApplying || !isValid}
            style={{ width: '100%' }}
          >
            <Send size={15} />
            <span>{isApplying ? 'APPLYING...' : 'APPLY SCENARIO'}</span>
          </button>

          <button
            type="button"
            className="btn btn-emerald"
            onClick={handleStart}
            disabled={!isValid}
            style={{ width: '100%' }}
          >
            <Play size={15} />
            <span>START SIMULATION</span>
          </button>

          <button
            type="button"
            className="btn btn-danger-outline"
            onClick={onReset}
            style={{ width: '100%' }}
          >
            <RotateCcw size={15} />
            <span>RESET TO DEFAULT</span>
          </button>
        </div>
      </div>

      {/* Start Simulation Confirmation Modal */}
      {showReadyModal && (
        <div className="modal-backdrop" onClick={() => setShowReadyModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ShieldCheck size={28} color="#10b981" />
              <div>
                <h3 style={{ color: '#fff', fontSize: '1.1rem', fontWeight: 800 }}>✓ SCENARIO INITIALIZED & READY</h3>
                <p style={{ color: '#94a3b8', fontSize: '0.8rem', fontFamily: 'var(--font-mono)' }}>
                  Team PHARO — FSOC Coarse Alignment Architecture
                </p>
              </div>
            </div>
            <div style={{ background: '#020617', padding: '12px', borderRadius: '6px', fontSize: '0.78rem', color: '#cbd5e1', lineHeight: '1.6' }}>
              <p><strong>Scenario:</strong> {config.scenario_name}</p>
              <p><strong>Total Simulation Frames:</strong> {config.simulation.duration * config.simulation.fps} ({config.simulation.duration}s @ {config.simulation.fps} FPS)</p>
              <p><strong>Sensor Specs:</strong> {config.camera.width}x{config.camera.height} px | FOV: {config.camera.horizontal_fov_deg}° x {config.camera.vertical_fov_deg}°</p>
              <p style={{ marginTop: '8px', color: '#38bdf8' }}>
                All optical, kinematic, and disturbance parameter contracts have been compiled and passed to the simulation engine factory.
              </p>
              <p style={{ marginTop: '6px', color: '#64748b', fontSize: '0.74rem' }}>
                <em>Note: Tracking algorithms (Kalman, PID, Gimbal dynamics) will execute in the next development stage.</em>
              </p>
            </div>
            <button
              type="button"
              className="btn btn-cyan"
              onClick={() => setShowReadyModal(false)}
            >
              ACKNOWLEDGE & RETURN
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
