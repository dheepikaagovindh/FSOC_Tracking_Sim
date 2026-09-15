/**
 * FSOC Scenario Configuration API Service.
 * Team PHARO — SIH26169
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function fetchActiveScenario() {
  const res = await fetch(`${API_BASE}/scenario`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail?.message || `Failed to fetch scenario (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function applyScenario(scenarioConfig) {
  const res = await fetch(`${API_BASE}/scenario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scenarioConfig),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const errorMsg = data.detail?.message || data.detail || 'Validation failed';
    const errorList = data.detail?.errors || [];
    const error = new Error(errorMsg);
    error.errors = errorList;
    error.status = res.status;
    throw error;
  }
  return data;
}

export async function loadPreset(presetId) {
  const res = await fetch(`${API_BASE}/scenario/preset/${encodeURIComponent(presetId)}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to load preset '${presetId}'`);
  }
  return await res.json();
}

export async function resetScenario() {
  const res = await fetch(`${API_BASE}/scenario/reset`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to reset scenario (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchPresets() {
  try {
    const res = await fetch(`${API_BASE}/scenario/presets`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    // Return hardcoded fallback catalog if offline
    return [
      { id: 'easy_acquisition', name: 'Easy Acquisition', difficulty: 'Level 1 - Baseline', description: 'Stationary terminals with zero disturbance. Baseline optical calibration.' },
      { id: 'moving_beacon', name: 'Moving Beacon', difficulty: 'Level 2 - Mild', description: 'Linear beacon motion across camera FOV with minor sensor noise.' },
      { id: 'platform_drift', name: 'Platform Drift', difficulty: 'Level 3 - Moderate', description: 'Receiver drift and beacon sinusoidal sway dynamics.' },
      { id: 'high_vibration', name: 'High Vibration', difficulty: 'Level 4 - Challenging', description: 'High-frequency micro-vibrations and atmospheric blur.' },
      { id: 'beacon_dropout', name: 'Beacon Dropout', difficulty: 'Level 5 - Hard', description: 'Atmospheric scintillation deep fades and line-of-sight dropouts.' },
      { id: 'full_stress_test', name: 'Full Stress Test', difficulty: 'Level 6 - Extreme', description: 'Orbital kinematics, severe jitter, noise, blur, and deep fading.' },
      { id: 'custom', name: 'Custom', difficulty: 'User Defined', description: 'User-tunable scenario with full parameter customization.' },
    ];
  }
}

export async function startSimulation() {
  const res = await fetch(`${API_BASE}/scenario/start`, {
    method: 'POST',
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const error = new Error(data.detail?.message || 'Failed to initialize simulation');
    error.errors = data.detail?.errors || [];
    throw error;
  }
  return data;
}
