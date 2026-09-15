/**
 * Beacon Detection & Centroiding API Service (Module 5).
 * Team PHARO — SIH26169
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchDetectionStatus() {
  const res = await fetch(`${API_BASE}/detection/status`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch detection status (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchDetectionResult() {
  const res = await fetch(`${API_BASE}/detection/result`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch detection result (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchDetectionTelemetry() {
  const res = await fetch(`${API_BASE}/detection/telemetry`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch detection telemetry (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function updateDetectionConfig(config) {
  const res = await fetch(`${API_BASE}/detection/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update detection config (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function resetDetection() {
  const res = await fetch(`${API_BASE}/detection/reset`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to reset detection (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function initializeDetection(scenario = null) {
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  };
  if (scenario) {
    options.body = JSON.stringify(scenario);
  }
  const res = await fetch(`${API_BASE}/detection/initialize`, options);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to initialize detection (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function executeDetection() {
  const res = await fetch(`${API_BASE}/detection/detect`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to execute detection (HTTP ${res.status})`);
  }
  return await res.json();
}

export function getAnnotatedImageUrl(cacheBust = Date.now()) {
  return `${API_BASE}/detection/annotated-image?t=${cacheBust}`;
}
