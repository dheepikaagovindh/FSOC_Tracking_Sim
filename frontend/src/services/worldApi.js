/**
 * Virtual World Simulation API Service.
 * Team PHARO — SIH26169
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function initializeWorld(scenario = null) {
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  };
  if (scenario) {
    options.body = JSON.stringify(scenario);
  }
  const res = await fetch(`${API_BASE}/world/initialize`, options);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to initialize world (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function resetWorld() {
  const res = await fetch(`${API_BASE}/world/reset`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to reset world (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function stepWorld(dt = null) {
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  };
  if (dt !== null && dt !== undefined) {
    options.body = JSON.stringify({ dt });
  }
  const res = await fetch(`${API_BASE}/world/step`, options);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to step simulation (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function setSimulationTime(time) {
  const res = await fetch(`${API_BASE}/world/time`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ time }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to set time (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchWorldState() {
  const res = await fetch(`${API_BASE}/world/state`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch world state (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchWorldStatus() {
  const res = await fetch(`${API_BASE}/world/status`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch world status (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchGeometry() {
  const res = await fetch(`${API_BASE}/world/geometry`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch geometry (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchPlatformState(platformId) {
  const res = await fetch(`${API_BASE}/world/platform/${encodeURIComponent(platformId)}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch platform '${platformId}'`);
  }
  return await res.json();
}
