"""
API Endpoint Tests for Beacon Detection Router.
Team PHARO — SIH26169
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)


def test_api_initialize(client):
    res = client.post("/detection/initialize")
    assert res.status_code == 200
    data = res.json()
    assert data["initialized"] is True
    assert "method" in data
    assert "detection_rate_pct" in data


def test_api_reset(client):
    res = client.post("/detection/reset")
    assert res.status_code == 200
    data = res.json()
    assert "detected" in data
    assert "method" in data


def test_api_status(client):
    res = client.get("/detection/status")
    assert res.status_code == 200
    data = res.json()
    assert data["initialized"] is True


def test_api_detect(client):
    res = client.post("/detection/detect")
    assert res.status_code == 200
    data = res.json()
    assert "detected" in data
    assert "confidence" in data
    assert "processing_time_ms" in data


def test_api_result(client):
    res = client.get("/detection/result")
    assert res.status_code == 200
    data = res.json()
    assert "timestamp" in data
    assert "method" in data


def test_api_config_update(client):
    cfg_payload = {
        "method": "opencv",
        "threshold": 45,
        "min_area": 2.0,
        "max_area": 4000.0,
        "min_brightness": 30.0,
        "min_confidence": 0.25,
        "blur_kernel": 3,
        "morphology_enabled": True,
    }
    res = client.post("/detection/config", json=cfg_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["config"]["threshold"] == 45
    assert data["config"]["min_confidence"] == 0.25


def test_api_telemetry(client):
    res = client.get("/detection/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "detected" in data
    assert "status_text" in data
    assert "processing_time_ms" in data


def test_api_overlay_png(client):
    res = client.get("/detection/overlay")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert len(res.content) > 100


def test_api_annotated_image_alias(client):
    res = client.get("/detection/annotated-image")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"


def test_api_invalid_config_rejection(client):
    # max_area <= min_area
    bad_payload = {
        "min_area": 100.0,
        "max_area": 50.0,
    }
    res = client.post("/detection/config", json=bad_payload)
    assert res.status_code in (400, 422)


def test_api_v1_prefix_routes(client):
    res = client.get("/api/v1/detection/status")
    assert res.status_code == 200
    assert res.json()["initialized"] is True
