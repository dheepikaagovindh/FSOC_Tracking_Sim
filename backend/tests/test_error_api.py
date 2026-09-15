"""
FastAPI REST API Endpoint Integration Tests for Error & Alignment Routes.
Team PHARO — SIH26169
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_error_status(client):
    """Test GET /error/status endpoint."""
    res = client.get("/error/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "config" in data
    assert "total_calculations" in data


def test_api_error_initialize(client):
    """Test POST /error/initialize endpoint."""
    res = client.post("/error/initialize")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data


def test_api_error_calculate_and_result(client):
    """Test POST /error/calculate and GET /error/result endpoints."""
    track_payload = {
        "timestamp": 1.5,
        "initialized": True,
        "tracking": True,
        "status": "TRACKING",
        "position_x": 350.0,
        "position_y": 220.0,
        "confidence": 0.94,
    }
    res_calc = client.post("/error/calculate", json=track_payload)
    assert res_calc.status_code == 200
    data = res_calc.json()
    assert data["valid"] is True
    assert data["source"] == "FILTERED"
    assert data["pixel_error_x"] == 30.0
    assert data["pixel_error_y"] == -20.0

    res_get = client.get("/error/result")
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert get_data["timestamp"] == 1.5
    assert get_data["pixel_error_x"] == 30.0


def test_api_error_config(client):
    """Test POST /error/config endpoint."""
    cfg_payload = {
        "enabled": True,
        "pixel_tolerance": 8.0,
        "angular_tolerance_deg": 0.35,
        "use_angular_alignment": True,
        "use_radial_alignment": True,
    }
    res = client.post("/error/config", json=cfg_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["config"]["pixel_tolerance"] == 8.0
    assert data["config"]["angular_tolerance_deg"] == 0.35


def test_api_error_telemetry(client):
    """Test GET /error/telemetry endpoint."""
    res = client.get("/error/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "status_text" in data


def test_api_error_overlay(client):
    """Test GET /error/overlay and /error/annotated-image endpoints."""
    res = client.get("/error/overlay")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert len(res.content) > 100

    res_alias = client.get("/error/annotated-image")
    assert res_alias.status_code == 200
    assert res_alias.headers["content-type"] == "image/png"


def test_api_error_reset(client):
    """Test POST /error/reset endpoint."""
    res = client.post("/error/reset")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "INVALID"
