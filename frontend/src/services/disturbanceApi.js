/**
 * Disturbance & Noise Simulation API Service.
 * Team PHARO — SIH26169
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchDisturbanceStatus() {
  const res = await fetch(`${API_BASE}/disturbance/status`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch disturbance status (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchDisturbanceFrame() {
  const res = await fetch(`${API_BASE}/disturbance/frame`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch disturbance frame (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchDisturbanceTelemetry() {
  const res = await fetch(`${API_BASE}/disturbance/telemetry`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch disturbance telemetry (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function updateDisturbanceConfig(config) {
  const res = await fetch(`${API_BASE}/disturbance/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update disturbance config (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function resetDisturbance() {
  const res = await fetch(`${API_BASE}/disturbance/reset`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to reset disturbance (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function initializeDisturbance(scenario = null) {
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  };
  if (scenario) {
    options.body = JSON.stringify(scenario);
  }
  const res = await fetch(`${API_BASE}/disturbance/initialize`, options);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to initialize disturbance (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function processDisturbanceFrame() {
  const res = await fetch(`${API_BASE}/disturbance/process`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to process disturbance frame (HTTP ${res.status})`);
  }
  return await res.json();
}

export function getDisturbedImageUrl(cacheBust = Date.now()) {
  return `${API_BASE}/disturbance/image?t=${cacheBust}`;
}
