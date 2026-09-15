/**
 * Virtual Camera Simulation API Service.
 * Team PHARO — SIH26169
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchCameraStatus() {
  const res = await fetch(`${API_BASE}/camera/status`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch camera status (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchCameraFrame() {
  const res = await fetch(`${API_BASE}/camera/frame`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch camera frame (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchCameraTelemetry() {
  const res = await fetch(`${API_BASE}/camera/telemetry`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch camera telemetry (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function fetchCameraIntrinsics() {
  const res = await fetch(`${API_BASE}/camera/intrinsics`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch camera intrinsics (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function updateCameraPose(panDeg, tiltDeg) {
  const body = {};
  if (panDeg !== undefined && panDeg !== null) body.pan_deg = parseFloat(panDeg);
  if (tiltDeg !== undefined && tiltDeg !== null) body.tilt_deg = parseFloat(tiltDeg);

  const res = await fetch(`${API_BASE}/camera/pose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update camera pose (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function resetCameraPose() {
  const res = await fetch(`${API_BASE}/camera/reset`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to reset camera (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function captureCameraFrame() {
  const res = await fetch(`${API_BASE}/camera/capture`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to capture frame (HTTP ${res.status})`);
  }
  return await res.json();
}

export async function initializeCamera(scenario = null) {
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  };
  if (scenario) {
    options.body = JSON.stringify(scenario);
  }
  const res = await fetch(`${API_BASE}/camera/initialize`, options);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to initialize camera (HTTP ${res.status})`);
  }
  return await res.json();
}

export function getCameraImageUrl(cacheBust = Date.now()) {
  return `${API_BASE}/camera/image?t=${cacheBust}`;
}
