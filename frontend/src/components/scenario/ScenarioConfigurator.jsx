import React, { useState, useEffect, useMemo } from 'react';
import ScenarioSelector from './ScenarioSelector';
import CameraConfig from './CameraConfig';
import PlatformConfig from './PlatformConfig';
import BeaconConfig from './BeaconConfig';
import DisturbanceConfig from './DisturbanceConfig';
import SimulationConfig from './SimulationConfig';
import ConfigurationSummary from './ConfigurationSummary';
import {
  fetchActiveScenario,
  fetchPresets,
  applyScenario,
  loadPreset,
  resetScenario,
  startSimulation,
} from '../../services/scenarioApi';

export default function ScenarioConfigurator({ onStatusChange, backendOnline }) {
  const [config, setConfig] = useState(null);
  const [presets, setPresets] = useState([]);
  const [activePresetId, setActivePresetId] = useState('easy_acquisition');
  const [loading, setLoading] = useState(true);
  const [isApplying, setIsApplying] = useState(false);
  const [backendValidation, setBackendValidation] = useState({ is_valid: true, errors: [], warnings: [] });
  const [feedbackBanner, setFeedbackBanner] = useState(null);

  // Initialize data from API
  useEffect(() => {
    async function init() {
      setLoading(true);
      try {
        const [scenarioData, presetsData] = await Promise.all([
          fetchActiveScenario().catch(() => null),
          fetchPresets().catch(() => []),
        ]);

        if (scenarioData) {
          setConfig(scenarioData);
          const matched = presetsData.find((p) => p.name.toLowerCase() === scenarioData.scenario_name?.toLowerCase());
          if (matched) setActivePresetId(matched.id);
        } else {
          // Default baseline fallback
          setConfig(getDefaultScenario());
        }

        if (presetsData.length > 0) {
          setPresets(presetsData);
        }
      } catch (err) {
        console.error('Initialization error:', err);
        setConfig(getDefaultScenario());
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  // Client-side real-time boundary validation
  const clientErrors = useMemo(() => {
    if (!config) return [];
    const errors = [];

    // Camera
    if (config.camera.width < 64 || config.camera.width > 7680) {
      errors.push(`[camera.width] Width must be between 64 and 7680 px.`);
    }
    if (config.camera.height < 64 || config.camera.height > 4320) {
      errors.push(`[camera.height] Height must be between 64 and 4320 px.`);
    }
    if (config.camera.horizontal_fov_deg <= 0 || config.camera.horizontal_fov_deg >= 180) {
      errors.push(`[camera.horizontal_fov_deg] Horizontal FOV must be within (0°, 180°).`);
    }
    if (config.camera.vertical_fov_deg <= 0 || config.camera.vertical_fov_deg >= 180) {
      errors.push(`[camera.vertical_fov_deg] Vertical FOV must be within (0°, 180°).`);
    }

    // Platforms
    if (config.camera_platform.amplitude < 0) errors.push(`[camera_platform.amplitude] Amplitude cannot be negative.`);
    if (config.beacon_platform.amplitude < 0) errors.push(`[beacon_platform.amplitude] Amplitude cannot be negative.`);

    // Beacon
    if (config.beacon.brightness <= 0) errors.push(`[beacon.brightness] Brightness must be > 0.`);
    if (config.beacon.size <= 0) errors.push(`[beacon.size] Spot size must be > 0.`);

    // Disturbances
    if (config.disturbances.dropout_probability < 0 || config.disturbances.dropout_probability > 1) {
      errors.push(`[disturbances.dropout_probability] Dropout rate must be between 0.0 and 1.0.`);
    }

    // Simulation
    if (config.simulation.duration <= 0) errors.push(`[simulation.duration] Duration must be > 0s.`);
    if (config.simulation.fps <= 0 || config.simulation.fps > 240) errors.push(`[simulation.fps] FPS must be between 1 and 240.`);

    return errors;
  }, [config]);

  // Handle Preset Selection
  const handleSelectPreset = async (presetId) => {
    setActivePresetId(presetId);
    try {
      if (backendOnline) {
        const res = await loadPreset(presetId);
        setConfig(res.scenario);
        setBackendValidation(res.validation || { is_valid: true, errors: [], warnings: [] });
        onStatusChange?.('SCENARIO_READY');
        showBanner('success', `Activated preset: ${res.scenario.scenario_name}`);
      } else {
        // Local simulation fallback
        const local = getLocalPreset(presetId);
        setConfig(local);
        showBanner('info', `Loaded preset: ${local.scenario_name} (Local mode)`);
      }
    } catch (err) {
      showBanner('error', `Failed to load preset: ${err.message}`);
    }
  };

  // Handle Apply Scenario
  const handleApply = async () => {
    if (!config || clientErrors.length > 0) return;
    setIsApplying(true);
    try {
      if (backendOnline) {
        const res = await applyScenario(config);
        setConfig(res.scenario);
        setBackendValidation(res.validation || { is_valid: true, errors: [], warnings: [] });
        onStatusChange?.('SCENARIO_READY');
        showBanner('success', '✓ Scenario configuration validated and applied successfully.');
      } else {
        showBanner('success', '✓ Scenario verified locally in offline mode.');
      }
    } catch (err) {
      const errList = err.errors || [err.message];
      setBackendValidation({ is_valid: false, errors: errList, warnings: [] });
      onStatusChange?.('ERROR');
      showBanner('error', 'Validation failed. Please correct parameters.');
    } finally {
      setIsApplying(false);
    }
  };

  // Handle Reset to Default
  const handleReset = async () => {
    try {
      if (backendOnline) {
        const res = await resetScenario();
        setConfig(res.scenario);
        setActivePresetId('easy_acquisition');
        setBackendValidation({ is_valid: true, errors: [], warnings: [] });
        onStatusChange?.('SCENARIO_READY');
        showBanner('info', 'Scenario reset to baseline Easy Acquisition.');
      } else {
        const def = getDefaultScenario();
        setConfig(def);
        setActivePresetId('easy_acquisition');
        showBanner('info', 'Reset to baseline scenario.');
      }
    } catch (err) {
      showBanner('error', `Reset failed: ${err.message}`);
    }
  };

  const showBanner = (type, text) => {
    setFeedbackBanner({ type, text });
    setTimeout(() => setFeedbackBanner(null), 4000);
  };

  if (loading || !config) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
        <p>INITIALIZING FSOC MISSION CONTROL DASHBOARD...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-layout">
      {/* Left / Center: Scenario Configurator Cards */}
      <div className="config-column">
        {/* Feedback Alert Toast */}
        {feedbackBanner && (
          <div style={{
            padding: '12px 18px',
            borderRadius: '8px',
            background: feedbackBanner.type === 'error' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(6, 182, 212, 0.15)',
            border: `1px solid ${feedbackBanner.type === 'error' ? '#ef4444' : '#06b6d4'}`,
            color: feedbackBanner.type === 'error' ? '#fca5a5' : '#67e8f9',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.82rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}>
            <span>{feedbackBanner.text}</span>
            <button
              onClick={() => setFeedbackBanner(null)}
              style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontWeight: 700 }}
            >
              ✕
            </button>
          </div>
        )}

        {/* 1. Scenario Presets Selector */}
        <ScenarioSelector
          presets={presets}
          activePresetId={activePresetId}
          onSelectPreset={handleSelectPreset}
        />

        {/* 2. Virtual Camera & Receiver Terminal */}
        <CameraConfig
          camera={config.camera}
          onChange={(newCamera) => {
            setConfig({ ...config, camera: newCamera, scenario_name: 'Custom' });
            setActivePresetId('custom');
          }}
          errors={[...clientErrors, ...backendValidation.errors]}
        />

        {/* 3. Camera Platform (Receiver Kinematics) */}
        <PlatformConfig
          title="Receiver Platform Kinematics"
          badge="CAMERA BASE"
          fieldPrefix="camera_platform"
          platform={config.camera_platform}
          onChange={(newPlat) => {
            setConfig({ ...config, camera_platform: newPlat, scenario_name: 'Custom' });
            setActivePresetId('custom');
          }}
          errors={[...clientErrors, ...backendValidation.errors]}
        />

        {/* 4. Beacon Platform (Transmitter Kinematics) */}
        <PlatformConfig
          title="Transmitter Platform Kinematics"
          badge="BEACON BASE"
          fieldPrefix="beacon_platform"
          platform={config.beacon_platform}
          onChange={(newPlat) => {
            setConfig({ ...config, beacon_platform: newPlat, scenario_name: 'Custom' });
            setActivePresetId('custom');
          }}
          errors={[...clientErrors, ...backendValidation.errors]}
        />

        {/* 5. Optical Beacon */}
        <BeaconConfig
          beacon={config.beacon}
          onChange={(newBeacon) => {
            setConfig({ ...config, beacon: newBeacon, scenario_name: 'Custom' });
            setActivePresetId('custom');
          }}
          errors={[...clientErrors, ...backendValidation.errors]}
        />

        {/* 6. Environmental Disturbances & Sensor Noise */}
        <DisturbanceConfig
          disturbances={config.disturbances}
          onChange={(newDist) => {
            setConfig({ ...config, disturbances: newDist, scenario_name: 'Custom' });
            setActivePresetId('custom');
          }}
          errors={[...clientErrors, ...backendValidation.errors]}
        />

        {/* 7. Simulation Timing & Telemetry */}
        <SimulationConfig
          simulation={config.simulation}
          onChange={(newSim) => {
            setConfig({ ...config, simulation: newSim, scenario_name: 'Custom' });
            setActivePresetId('custom');
          }}
          errors={[...clientErrors, ...backendValidation.errors]}
        />
      </div>

      {/* Right Column: Sticky Summary & Action HUD */}
      <div className="summary-column">
        <ConfigurationSummary
          config={config}
          onReset={handleReset}
          onApply={handleApply}
          onStartSimulation={startSimulation}
          isApplying={isApplying}
          validationResult={backendValidation}
          clientErrors={clientErrors}
        />
      </div>
    </div>
  );
}

function getDefaultScenario() {
  return {
    scenario_name: 'Easy Acquisition',
    description: 'Stationary transmitter and receiver with zero disturbance',
    camera: {
      width: 640,
      height: 480,
      horizontal_fov_deg: 30.0,
      vertical_fov_deg: 22.5,
      initial_pan_deg: 0.0,
      initial_tilt_deg: 0.0,
    },
    camera_platform: {
      motion_profile: 'static',
      initial_position_x: 0.0,
      initial_position_y: 0.0,
      initial_position_z: 0.0,
      velocity_x: 0.0,
      velocity_y: 0.0,
      velocity_z: 0.0,
      amplitude: 0.0,
      frequency: 0.0,
    },
    beacon_platform: {
      motion_profile: 'static',
      initial_position_x: 0.0,
      initial_position_y: 0.0,
      initial_position_z: 1000.0,
      velocity_x: 0.0,
      velocity_y: 0.0,
      velocity_z: 0.0,
      amplitude: 0.0,
      frequency: 0.0,
    },
    beacon: {
      brightness: 1.0,
      size: 5.0,
      trajectory: 'static',
      trajectory_parameters: {},
    },
    disturbances: {
      severity: 'off',
      vibration_enabled: false,
      vibration_magnitude: 0.0,
      noise_enabled: false,
      noise_magnitude: 0.0,
      blur_enabled: false,
      blur_strength: 0.0,
      dropout_enabled: false,
      dropout_probability: 0.0,
      dropout_duration: 0.0,
    },
    simulation: {
      duration: 30.0,
      fps: 30.0,
      random_seed: 42,
      record_telemetry: true,
      record_frames: false,
    },
  };
}

function getLocalPreset(presetId) {
  const base = getDefaultScenario();
  if (presetId === 'moving_beacon') {
    base.scenario_name = 'Moving Beacon';
    base.beacon_platform.motion_profile = 'drift';
    base.beacon_platform.velocity_x = 2.5;
    base.beacon.trajectory = 'linear';
    base.disturbances.severity = 'low';
    base.disturbances.noise_enabled = true;
    base.disturbances.noise_magnitude = 0.05;
  } else if (presetId === 'high_vibration') {
    base.scenario_name = 'High Vibration';
    base.camera_platform.motion_profile = 'sway';
    base.camera_platform.amplitude = 3.0;
    base.camera_platform.frequency = 2.5;
    base.disturbances.severity = 'high';
    base.disturbances.vibration_enabled = true;
    base.disturbances.vibration_magnitude = 4.5;
    base.disturbances.noise_enabled = true;
    base.disturbances.noise_magnitude = 0.2;
    base.disturbances.blur_enabled = true;
    base.disturbances.blur_strength = 2.8;
  } else if (presetId === 'beacon_dropout') {
    base.scenario_name = 'Beacon Dropout';
    base.disturbances.severity = 'medium';
    base.disturbances.dropout_enabled = true;
    base.disturbances.dropout_probability = 0.35;
    base.disturbances.dropout_duration = 0.6;
    base.disturbances.blur_enabled = true;
    base.disturbances.blur_strength = 1.5;
  } else if (presetId === 'full_stress_test') {
    base.scenario_name = 'Full Stress Test';
    base.camera_platform.motion_profile = 'orbit';
    base.beacon_platform.motion_profile = 'sway';
    base.disturbances.severity = 'high';
    base.disturbances.vibration_enabled = true;
    base.disturbances.vibration_magnitude = 5.0;
    base.disturbances.noise_enabled = true;
    base.disturbances.noise_magnitude = 0.25;
    base.disturbances.blur_enabled = true;
    base.disturbances.blur_strength = 3.5;
    base.disturbances.dropout_enabled = true;
    base.disturbances.dropout_probability = 0.45;
    base.disturbances.dropout_duration = 0.8;
  }
  return base;
}
