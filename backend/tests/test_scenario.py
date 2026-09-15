"""
Comprehensive Unit & Integration Test Suite for FSOC Scenario Configuration Module.
Team PHARO — SIH26169
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.scenario.models import (
    ScenarioConfig,
    CameraConfig,
    PlatformConfig,
    BeaconConfig,
    DisturbanceConfig,
    SimulationConfig,
)
from app.scenario.presets import (
    get_preset,
    list_available_presets,
    get_easy_acquisition_preset,
    get_moving_beacon_preset,
    get_platform_drift_preset,
    get_high_vibration_preset,
    get_beacon_dropout_preset,
    get_full_stress_test_preset,
    get_custom_preset,
    PRESET_FACTORIES,
)
from app.scenario.validator import ScenarioValidator, ValidationResult
from app.scenario.service import scenario_service
from app.scenario.factory import ScenarioFactory

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Model & Default Configuration Tests
# ---------------------------------------------------------------------------

def test_default_scenario_is_valid():
    """Verify default ScenarioConfig instantiates cleanly and passes validation."""
    config = ScenarioConfig()
    val_result = ScenarioValidator.validate(config)
    assert val_result.is_valid is True
    assert len(val_result.errors) == 0
    assert config.camera.width == 640
    assert config.camera.height == 480
    assert config.camera.horizontal_fov_deg == 30.0
    assert config.camera.vertical_fov_deg == 22.5
    assert config.disturbances.severity == "off"


# ---------------------------------------------------------------------------
# 2. Preset Validation Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("preset_key", list(PRESET_FACTORIES.keys()))
def test_all_presets_are_valid(preset_key):
    """Verify that every registered preset produces a strictly valid ScenarioConfig."""
    preset_config = get_preset(preset_key)
    assert isinstance(preset_config, ScenarioConfig)
    val_result = ScenarioValidator.validate(preset_config)
    assert val_result.is_valid is True, f"Preset '{preset_key}' failed validation: {val_result.errors}"


def test_preset_catalog_completeness():
    """Verify preset catalog returns expected metadata fields."""
    presets = list_available_presets()
    assert len(presets) >= 7
    ids = [p["id"] for p in presets]
    assert "easy_acquisition" in ids
    assert "moving_beacon" in ids
    assert "platform_drift" in ids
    assert "high_vibration" in ids
    assert "beacon_dropout" in ids
    assert "full_stress_test" in ids
    assert "custom" in ids


# ---------------------------------------------------------------------------
# 3. Dedicated Validator & Constraint Tests
# ---------------------------------------------------------------------------

def test_invalid_fov_rejection():
    """FOV values must be strictly within (0, 180)."""
    # Negative FOV rejected at pydantic model level
    with pytest.raises(ValidationError):
        CameraConfig(horizontal_fov_deg=-10.0)

    with pytest.raises(ValidationError):
        CameraConfig(vertical_fov_deg=0.0)

    with pytest.raises(ValidationError):
        CameraConfig(horizontal_fov_deg=200.0)

    # Validator check
    config = ScenarioConfig()
    config.camera.horizontal_fov_deg = 190.0  # bypass pydantic via mutation
    val = ScenarioValidator.validate(config)
    assert val.is_valid is False
    assert any("horizontal_fov_deg" in err for err in val.errors)


def test_invalid_resolution_rejection():
    """Resolution must be positive and within reasonable bounds."""
    with pytest.raises(ValidationError):
        CameraConfig(width=0, height=480)

    with pytest.raises(ValidationError):
        CameraConfig(width=640, height=-100)

    # Out of bounds check
    with pytest.raises(ValidationError):
        CameraConfig(width=10000, height=480)


def test_invalid_pan_tilt_rejection():
    """Pan [-180, 180] and Tilt [-90, 90] bounds."""
    with pytest.raises(ValidationError):
        CameraConfig(initial_pan_deg=200.0)

    with pytest.raises(ValidationError):
        CameraConfig(initial_tilt_deg=100.0)


def test_invalid_motion_profile_rejection():
    """Motion profiles outside 'static', 'drift', 'sway', 'orbit' must fail."""
    with pytest.raises(ValidationError):
        PlatformConfig(motion_profile="flying_saucer")

    # Dictionary validation path
    payload = ScenarioConfig().model_dump()
    payload["camera_platform"]["motion_profile"] = "teleportation"
    cfg, val = ScenarioValidator.validate_dict(payload)
    assert cfg is None
    assert val.is_valid is False
    assert any("motion_profile" in err for err in val.errors)


def test_invalid_beacon_trajectory_rejection():
    """Beacon trajectory outside valid set must fail."""
    with pytest.raises(ValidationError):
        BeaconConfig(trajectory="zigzag_spiral")


def test_invalid_disturbance_severity_rejection():
    """Disturbance severity outside 'off', 'low', 'medium', 'high' must fail."""
    with pytest.raises(ValidationError):
        DisturbanceConfig(severity="apocalyptic")


def test_invalid_dropout_probability_rejection():
    """Dropout probability must be between 0.0 and 1.0."""
    with pytest.raises(ValidationError):
        DisturbanceConfig(dropout_probability=1.5)

    with pytest.raises(ValidationError):
        DisturbanceConfig(dropout_probability=-0.1)


def test_invalid_simulation_duration_and_fps():
    """Simulation duration and FPS must be > 0."""
    with pytest.raises(ValidationError):
        SimulationConfig(duration=0.0)

    with pytest.raises(ValidationError):
        SimulationConfig(fps=-30.0)

    with pytest.raises(ValidationError):
        SimulationConfig(random_seed=-5)


def test_negative_magnitudes_rejection():
    """Magnitudes and amplitudes cannot be negative."""
    with pytest.raises(ValidationError):
        PlatformConfig(amplitude=-2.0)

    with pytest.raises(ValidationError):
        DisturbanceConfig(vibration_magnitude=-1.0)

    with pytest.raises(ValidationError):
        DisturbanceConfig(noise_magnitude=-0.5)

    with pytest.raises(ValidationError):
        DisturbanceConfig(blur_strength=-3.0)


# ---------------------------------------------------------------------------
# 4. Factory & Initialization Contract Tests
# ---------------------------------------------------------------------------

def test_scenario_factory_output():
    """Verify ScenarioFactory translates ScenarioConfig into structured module parameters."""
    config = get_full_stress_test_preset()
    context = ScenarioFactory.build_simulation_context(config)

    assert context["status"] == "INITIALIZED_READY"
    assert "world_initialization" in context
    assert "camera_initialization" in context
    assert "disturbance_initialization" in context
    assert "simulation_runtime" in context

    runtime = context["simulation_runtime"]
    assert runtime["duration_seconds"] == 60.0
    assert runtime["target_fps"] == 30.0
    assert runtime["total_frames"] == 1800
    assert runtime["record_frames"] is True


# ---------------------------------------------------------------------------
# 5. REST API Integration Tests
# ---------------------------------------------------------------------------

def test_api_root_and_health():
    """Test API root and health check endpoints."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["project"] == "FSOC Coarse Alignment Simulator"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"


def test_api_get_active_scenario():
    """GET /scenario returns active configuration."""
    response = client.get("/scenario")
    assert response.status_code == 200
    data = response.json()
    assert "scenario_name" in data
    assert "camera" in data
    assert "disturbances" in data


def test_api_post_valid_scenario():
    """POST /scenario applies valid configuration and returns SCENARIO_READY."""
    new_scenario = get_high_vibration_preset().model_dump()
    response = client.post("/scenario", json=new_scenario)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SCENARIO_READY"
    assert body["scenario"]["scenario_name"] == "High Vibration"
    assert body["validation"]["is_valid"] is True


def test_api_post_invalid_scenario():
    """POST /scenario with invalid payload returns 422 Unprocessable Entity."""
    invalid_payload = ScenarioConfig().model_dump()
    invalid_payload["camera"]["width"] = -500  # invalid resolution
    response = client.post("/scenario", json=invalid_payload)
    assert response.status_code == 422


def test_api_preset_loading():
    """POST /scenario/preset/{preset_name} activates preset."""
    response = client.post("/scenario/preset/beacon_dropout")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SCENARIO_READY"
    assert body["scenario"]["scenario_name"] == "Beacon Dropout"

    # Verify active scenario was updated
    active = client.get("/scenario").json()
    assert active["scenario_name"] == "Beacon Dropout"


def test_api_preset_not_found():
    """POST /scenario/preset/{unknown} returns 404."""
    response = client.post("/scenario/preset/mars_rover_drift")
    assert response.status_code == 404


def test_api_reset_scenario():
    """POST /scenario/reset resets to default Easy Acquisition."""
    # First change preset
    client.post("/scenario/preset/full_stress_test")
    # Reset
    response = client.post("/scenario/reset")
    assert response.status_code == 200
    body = response.json()
    assert body["scenario"]["scenario_name"] == "Easy Acquisition"


def test_api_dry_run_validate():
    """POST /scenario/validate returns validation results without mutating state."""
    payload = get_moving_beacon_preset().model_dump()
    response = client.post("/scenario/validate", json=payload)
    assert response.status_code == 200
    assert response.json()["is_valid"] is True


def test_api_start_simulation():
    """POST /scenario/start returns simulation readiness confirmation."""
    response = client.post("/scenario/start")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SCENARIO_READY"
    assert "simulation_context" in body
