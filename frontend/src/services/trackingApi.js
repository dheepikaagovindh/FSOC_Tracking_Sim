/**
 * Beacon Tracking & Motion Prediction API Service (Module 6).
 * Team PHARO — SIH26169
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchTrackingStatus() {
  const res = await fetch(`${API_BASE}/tracking/status`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch tracking status (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchTrackingResult() {
  const res = await fetch(`${API_BASE}/tracking/result`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch tracking result (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchTrackingTelemetry() {
  const res = await fetch(`${API_BASE}/tracking/telemetry`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch tracking telemetry (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function updateTrackingConfig(config) {
  const res = await fetch(`${API_BASE}/tracking/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update tracking config (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function resetTracking() {
  const res = await fetch(`${API_BASE}/tracking/reset`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to reset tracking (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function initializeTracking(scenario = null) {
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  };
  if (scenario) {
    options.body = JSON.stringify(scenario);
  }
  const res = await fetch(`${API_BASE}/tracking/initialize`, options);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to initialize tracking (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function executeTrackingStep(detection = null) {
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  };
  if (detection) {
    options.body = JSON.stringify(detection);
  }
  const res = await fetch(`${API_BASE}/tracking/update`, options);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to execute tracking step (HTTP ${res.status})`);
  }
  return await res.json();
}

export function getTrackingOverlayUrl(cacheBust = Date.now()) {
  return `${API_BASE}/tracking/overlay?t=${cacheBust}`;
}
