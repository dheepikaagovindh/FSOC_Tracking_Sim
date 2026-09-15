/**
 * Boresight Alignment & Error Calculation API Service (Module 7).
 * Team PHARO — SIH26169
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchErrorStatus() {
  const res = await fetch(`${API_BASE}/error/status`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch error status (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchErrorResult() {
  const res = await fetch(`${API_BASE}/error/result`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch error result (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchErrorTelemetry() {
  const res = await fetch(`${API_BASE}/error/telemetry`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch error telemetry (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function updateErrorConfig(config) {
  const res = await fetch(`${API_BASE}/error/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update error config (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function resetError() {
  const res = await fetch(`${API_BASE}/error/reset`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to reset error engine (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function initializeError(scenario = null) {
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  };
  if (scenario) {
    options.body = JSON.stringify(scenario);
  }
  const res = await fetch(`${API_BASE}/error/initialize`, options);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to initialize error engine (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function executeErrorCalculation(tracking = null) {
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  };
  if (tracking) {
    options.body = JSON.stringify(tracking);
  }
  const res = await fetch(`${API_BASE}/error/calculate`, options);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to calculate error (HTTP ${res.status})`);
  }
  return await res.json();
}

export function getErrorOverlayUrl(cacheBust = Date.now()) {
  return `${API_BASE}/error/overlay?t=${cacheBust}`;
}
