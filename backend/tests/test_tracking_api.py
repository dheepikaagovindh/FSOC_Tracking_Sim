"""
FastAPI REST API Endpoint Integration Tests for Tracking Routes.
Team PHARO — SIH26169
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_tracking_status(client):
    """Test GET /tracking/status endpoint."""
    res = client.get("/tracking/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "config" in data
    assert "initialized" in data


def test_api_tracking_initialize(client):
    """Test POST /tracking/initialize endpoint."""
    res = client.post("/tracking/initialize")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert data["status"] in ["UNINITIALIZED", "TRACKING", "PREDICTING", "LOST"]


def test_api_tracking_update_and_result(client):
    """Test POST /tracking/update and GET /tracking/result endpoints."""
    det_payload = {
        "detected": True,
        "center_x": 320.0,
        "center_y": 240.0,
        "confidence": 0.95,
        "timestamp": 1.5,
    }
    res_up = client.post("/tracking/update", json=det_payload)
    assert res_up.status_code == 200
    up_data = res_up.json()
    assert up_data["status"] == "TRACKING"
    assert up_data["tracking"] is True
    assert pytest.approx(up_data["position_x"], abs=0.1) == 320.0

    res_get = client.get("/tracking/result")
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert get_data["timestamp"] == 1.5
    assert get_data["position_x"] == up_data["position_x"]


def test_api_tracking_config(client):
    """Test POST /tracking/config endpoint."""
    cfg_payload = {
        "enabled": True,
        "process_noise": 15.0,
        "measurement_noise": 2.5,
        "max_missed_frames": 8,
        "min_detection_confidence": 0.25,
    }
    res = client.post("/tracking/config", json=cfg_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["config"]["process_noise"] == 15.0
    assert data["config"]["measurement_noise"] == 2.5
    assert data["config"]["max_missed_frames"] == 8


def test_api_tracking_telemetry(client):
    """Test GET /tracking/telemetry endpoint."""
    res = client.get("/tracking/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "confidence" in data
    assert "status_text" in data


def test_api_tracking_overlay(client):
    """Test GET /tracking/overlay and /tracking/annotated-image endpoints."""
    res = client.get("/tracking/overlay")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert len(res.content) > 100

    res_alias = client.get("/tracking/annotated-image")
    assert res_alias.status_code == 200
    assert res_alias.headers["content-type"] == "image/png"


def test_api_tracking_reset(client):
    """Test POST /tracking/reset endpoint."""
    res = client.post("/tracking/reset")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
