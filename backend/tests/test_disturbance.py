"""
Unit and Integration Tests for Disturbance & Noise Simulation Module.
Team PHARO — SIH26169

Tests sensor noise, optical blur, image vibration/jitter, beacon dropout,
severity presets, deterministic reproducibility, and REST API endpoints.
"""

import io
import math
import pytest
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.scenario.models import ScenarioConfig, DisturbanceConfig, CameraConfig, PlatformConfig, BeaconConfig
from backend.app.camera.models import CameraFrame, ProjectedPoint, CameraAngles, CameraVisibility
from backend.app.world.models import Vector3D
from backend.app.camera.renderer import render_camera_frame
from backend.app.disturbance.models import (
    NoiseMetadata,
    BlurMetadata,
    VibrationMetadata,
    DropoutMetadata,
    DisturbanceMetadata,
    DisturbanceFrame,
    DisturbanceStatus,
)
from backend.app.disturbance.noise import apply_sensor_noise, compute_noise_sigma
from backend.app.disturbance.blur import apply_image_blur
from backend.app.disturbance.vibration import apply_image_vibration, calculate_vibration_offset
from backend.app.disturbance.dropout import DropoutTracker, apply_beacon_dropout
from backend.app.disturbance.processor import DisturbanceProcessor
from backend.app.disturbance.service import disturbance_service
from backend.app.camera.service import camera_service
from backend.app.world.service import world_service
from backend.app.scenario.service import scenario_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def clean_synthetic_image():
    """Create a clean 640x480 test image with a bright spot at center (320, 240)."""
    proj = ProjectedPoint(u=320.0, v=240.0, normalized_x=0.0, normalized_y=0.0)
    vis = CameraVisibility(visible=True, in_front_of_camera=True, inside_horizontal_fov=True, inside_vertical_fov=True, reason="VISIBLE")
    return render_camera_frame(width=640, height=480, projection=proj, visibility=vis, brightness=1.0, size=6.0)


@pytest.fixture
def synthetic_camera_frame():
    """Mock clean camera frame metadata."""
    return CameraFrame(
        timestamp=0.0,
        width=640,
        height=480,
        visible=True,
        camera_position=Vector3D(x=0.0, y=0.0, z=0.0),
        camera_orientation={"pan_deg": 0.0, "tilt_deg": 0.0},
        beacon_world_position=Vector3D(x=0.0, y=0.0, z=50.0),
        beacon_camera_coordinates=Vector3D(x=0.0, y=0.0, z=50.0),
        projection=ProjectedPoint(u=320.0, v=240.0, normalized_x=0.0, normalized_y=0.0),
        angles=CameraAngles(azimuth_deg=0.0, elevation_deg=0.0),
        visibility=CameraVisibility(visible=True, in_front_of_camera=True, inside_horizontal_fov=True, inside_vertical_fov=True, reason="VISIBLE"),
        spot_radius=3.0,
        spot_intensity=255,
    )


# ==============================================================================
# 1. Lifecycle & Basic Processor Tests
# ==============================================================================

def test_disturbance_initialization():
    """Verify disturbance service initializes cleanly from ScenarioConfig."""
    scenario = ScenarioConfig(scenario_name="Test Scenario")
    status = disturbance_service.initialize_from_scenario(scenario)

    assert status.initialized is True
    assert status.scenario_name == "Test Scenario"
    assert status.severity == "off"


def test_disturbance_reset():
    """Verify disturbance reset clears tracker and generates frame at t=0."""
    frame = disturbance_service.reset()
    assert isinstance(frame, DisturbanceFrame)
    assert frame.timestamp >= 0.0
    assert frame.width == 640
    assert frame.height == 480


# ==============================================================================
# 2. OFF Severity Mode
# ==============================================================================

def test_off_severity_leaves_image_unchanged(clean_synthetic_image, synthetic_camera_frame):
    """Verify OFF severity mode leaves the clean synthetic image 100% bit-exact and unchanged."""
    processor = DisturbanceProcessor()
    config = DisturbanceConfig(severity="off")

    disturbed_img, meta = processor.process(
        clean_image=clean_synthetic_image,
        config=config,
        timestamp=1.5,
        fps=30.0,
        seed=42,
        camera_frame=synthetic_camera_frame,
    )

    np.testing.assert_array_equal(clean_synthetic_image, disturbed_img)
    assert meta.applied_effects_count == 0
    assert meta.noise.applied is False
    assert meta.blur.applied is False
    assert meta.vibration.applied is False
    assert meta.dropout.applied is False


# ==============================================================================
# 3. Sensor Noise Tests
# ==============================================================================

def test_sensor_noise_changes_image(clean_synthetic_image):
    """Verify sensor noise alters image pixel values when enabled."""
    noisy_img, meta = apply_sensor_noise(
        image=clean_synthetic_image,
        magnitude=0.15,
        enabled=True,
        seed=42,
        frame_index=1,
    )

    assert meta.applied is True
    assert meta.sigma > 0.0
    assert not np.array_equal(clean_synthetic_image, noisy_img)
    assert np.count_nonzero(noisy_img) > np.count_nonzero(clean_synthetic_image)


def test_sensor_noise_bounds_and_dtype(clean_synthetic_image):
    """Verify noisy image remains strictly bounded in [0, 255] with uint8 dtype."""
    noisy_img, _ = apply_sensor_noise(
        image=clean_synthetic_image,
        magnitude=0.5,
        enabled=True,
        seed=101,
        frame_index=5,
    )

    assert noisy_img.dtype == np.uint8
    assert noisy_img.min() >= 0
    assert noisy_img.max() <= 255
    assert noisy_img.shape == clean_synthetic_image.shape


def test_sensor_noise_zero_magnitude_leaves_image_unchanged(clean_synthetic_image):
    """Verify noise_magnitude=0 leaves image unchanged."""
    noisy_img, meta = apply_sensor_noise(
        image=clean_synthetic_image,
        magnitude=0.0,
        enabled=True,
        seed=42,
        frame_index=0,
    )

    np.testing.assert_array_equal(clean_synthetic_image, noisy_img)
    assert meta.applied is False


# ==============================================================================
# 4. Image Blur Tests
# ==============================================================================

def test_blur_changes_image_and_softens_edges(clean_synthetic_image):
    """Verify optical blur reduces peak spot intensity and spreads energy."""
    blurred_img, meta = apply_image_blur(
        image=clean_synthetic_image,
        blur_strength=2.5,
        enabled=True,
    )

    assert meta.applied is True
    assert meta.kernel_size > 1
    assert not np.array_equal(clean_synthetic_image, blurred_img)
    # Peak center intensity should decrease due to Gaussian dispersion
    assert blurred_img[240, 320] < clean_synthetic_image[240, 320]
    # Surrounding pixels should now have non-zero energy
    assert np.count_nonzero(blurred_img) > np.count_nonzero(clean_synthetic_image)


def test_blur_preserves_dimensions_and_dtype(clean_synthetic_image):
    """Verify blurred image maintains exact shape and uint8 dtype."""
    blurred_img, _ = apply_image_blur(clean_synthetic_image, blur_strength=3.0, enabled=True)
    assert blurred_img.shape == clean_synthetic_image.shape
    assert blurred_img.dtype == np.uint8


def test_blur_zero_and_negative_safe(clean_synthetic_image):
    """Verify blur handles zero and negative strength safely without errors."""
    img_zero, meta_zero = apply_image_blur(clean_synthetic_image, blur_strength=0.0, enabled=True)
    np.testing.assert_array_equal(clean_synthetic_image, img_zero)
    assert meta_zero.applied is False

    img_neg, meta_neg = apply_image_blur(clean_synthetic_image, blur_strength=-2.0, enabled=True)
    np.testing.assert_array_equal(clean_synthetic_image, img_neg)
    assert meta_neg.applied is False


# ==============================================================================
# 5. Image Vibration / Jitter Tests
# ==============================================================================

def test_vibration_shifts_image(clean_synthetic_image):
    """Verify image vibration shifts the spot center position in the frame."""
    # At t=0.05s with magnitude 5.0, displacement is non-zero
    shifted_img, meta = apply_image_vibration(
        image=clean_synthetic_image,
        magnitude=5.0,
        timestamp=0.05,
        enabled=True,
    )

    assert meta.applied is True
    assert abs(meta.offset_x) > 0.1 or abs(meta.offset_y) > 0.1
    assert not np.array_equal(clean_synthetic_image, shifted_img)
    assert shifted_img.shape == clean_synthetic_image.shape
    assert shifted_img.dtype == np.uint8


def test_vibration_black_border_no_wrap(clean_synthetic_image):
    """Verify shifted pixels do NOT wrap around opposing image edges."""
    shifted_img, _ = apply_image_vibration(
        image=clean_synthetic_image,
        magnitude=10.0,
        timestamp=0.05,
        enabled=True,
    )

    # Leftmost and topmost border edges should remain black (0)
    assert shifted_img[0, 0] == 0
    assert shifted_img[0, 639] == 0
    assert shifted_img[479, 0] == 0


def test_vibration_zero_magnitude_leaves_image_unchanged(clean_synthetic_image):
    """Verify vibration_magnitude=0 leaves image unchanged."""
    shifted_img, meta = apply_image_vibration(clean_synthetic_image, magnitude=0.0, timestamp=1.0, enabled=True)
    np.testing.assert_array_equal(clean_synthetic_image, shifted_img)
    assert meta.applied is False


# ==============================================================================
# 6. Beacon Dropout Tests
# ==============================================================================

def test_dropout_probability_zero_never_drops(clean_synthetic_image, synthetic_camera_frame):
    """Verify probability=0 never triggers dropout."""
    tracker = DropoutTracker()
    for frame_idx in range(10):
        img_out, meta = apply_beacon_dropout(
            image=clean_synthetic_image,
            tracker=tracker,
            camera_frame=synthetic_camera_frame,
            probability=0.0,
            duration=0.5,
            timestamp=frame_idx * (1.0 / 30.0),
            seed=42,
            frame_index=frame_idx,
            enabled=True,
        )
        assert meta.active is False
        assert meta.applied is False
        np.testing.assert_array_equal(clean_synthetic_image, img_out)


def test_dropout_probability_one_always_drops(clean_synthetic_image, synthetic_camera_frame):
    """Verify probability=1 always suppresses the beacon spot."""
    tracker = DropoutTracker()
    img_out, meta = apply_beacon_dropout(
        image=clean_synthetic_image,
        tracker=tracker,
        camera_frame=synthetic_camera_frame,
        probability=1.0,
        duration=0.5,
        timestamp=0.0,
        seed=42,
        frame_index=0,
        enabled=True,
    )

    assert meta.active is True
    assert meta.applied is True
    # The spot at (240, 320) must now be zeroed out
    assert img_out[240, 320] == 0
    assert np.count_nonzero(img_out) == 0


def test_dropout_duration_persistence(clean_synthetic_image, synthetic_camera_frame):
    """Verify triggered dropout persists for configured duration and then recovers."""
    tracker = DropoutTracker()
    duration = 0.2  # 6 frames at 30 fps (t=0.0 to t=0.2)

    # Frame 0 at t=0.0 (triggers with prob=1.0)
    _, meta0 = apply_beacon_dropout(clean_synthetic_image, tracker, synthetic_camera_frame, 1.0, duration, 0.0, 42, 0, True)
    assert meta0.active is True

    # Frame 3 at t=0.1 (within duration -> still active)
    _, meta1 = apply_beacon_dropout(clean_synthetic_image, tracker, synthetic_camera_frame, 0.0, duration, 0.1, 42, 3, True)
    assert meta1.active is True

    # Frame 8 at t=0.25 (duration expired -> recovers)
    _, meta2 = apply_beacon_dropout(clean_synthetic_image, tracker, synthetic_camera_frame, 0.0, duration, 0.25, 42, 8, True)
    assert meta2.active is False


# ==============================================================================
# 7. Severity Levels Progression & Multi-Disturbance
# ==============================================================================

def test_severity_levels_progression(clean_synthetic_image, synthetic_camera_frame):
    """Verify disturbance severity progressively increases from OFF to HIGH."""
    processor = DisturbanceProcessor()

    _, meta_off = processor.process(clean_synthetic_image, DisturbanceConfig(severity="off"), 1.0, 30.0, 42, synthetic_camera_frame)
    _, meta_low = processor.process(clean_synthetic_image, DisturbanceConfig(severity="low"), 1.0, 30.0, 42, synthetic_camera_frame)
    _, meta_med = processor.process(clean_synthetic_image, DisturbanceConfig(severity="medium"), 1.0, 30.0, 42, synthetic_camera_frame)
    _, meta_high = processor.process(clean_synthetic_image, DisturbanceConfig(severity="high"), 1.0, 30.0, 42, synthetic_camera_frame)

    assert meta_off.applied_effects_count == 0
    assert meta_low.noise.sigma < meta_med.noise.sigma < meta_high.noise.sigma
    assert meta_low.blur.strength < meta_med.blur.strength < meta_high.blur.strength
    assert meta_low.vibration.magnitude < meta_med.vibration.magnitude < meta_high.vibration.magnitude


def test_multiple_disturbances_simultaneously(clean_synthetic_image, synthetic_camera_frame):
    """Verify simultaneous application of vibration, blur, noise, and dropout."""
    processor = DisturbanceProcessor()
    config = DisturbanceConfig(
        severity="low",
        vibration_enabled=True,
        vibration_magnitude=2.0,
        noise_enabled=True,
        noise_magnitude=0.1,
        blur_enabled=True,
        blur_strength=1.5,
        dropout_enabled=False,
    )

    disturbed_img, meta = processor.process(
        clean_image=clean_synthetic_image,
        config=config,
        timestamp=0.5,
        fps=30.0,
        seed=42,
        camera_frame=synthetic_camera_frame,
    )

    assert meta.applied_effects_count == 3
    assert meta.vibration.applied is True
    assert meta.blur.applied is True
    assert meta.noise.applied is True
    assert meta.dropout.applied is False
    assert disturbed_img.shape == (480, 640)
    assert disturbed_img.dtype == np.uint8


# ==============================================================================
# 8. Deterministic Reproducibility Tests
# ==============================================================================

def test_deterministic_reproducibility(clean_synthetic_image, synthetic_camera_frame):
    """Verify identical (scenario, seed, timestamp, image) produces 100% bit-exact outputs."""
    processor1 = DisturbanceProcessor()
    processor2 = DisturbanceProcessor()
    config = DisturbanceConfig(severity="medium")

    img1, meta1 = processor1.process(clean_synthetic_image, config, timestamp=1.5, fps=30.0, seed=777, camera_frame=synthetic_camera_frame)
    img2, meta2 = processor2.process(clean_synthetic_image, config, timestamp=1.5, fps=30.0, seed=777, camera_frame=synthetic_camera_frame)

    np.testing.assert_array_equal(img1, img2)
    assert meta1.model_dump() == meta2.model_dump()


def test_different_seeds_produce_different_noise(clean_synthetic_image):
    """Verify different random seeds generate different stochastic noise realizations."""
    img_seed1, _ = apply_sensor_noise(clean_synthetic_image, magnitude=0.2, enabled=True, seed=10, frame_index=1)
    img_seed2, _ = apply_sensor_noise(clean_synthetic_image, magnitude=0.2, enabled=True, seed=999, frame_index=1)

    assert not np.array_equal(img_seed1, img_seed2)


# ==============================================================================
# 9. REST API Endpoints Tests
# ==============================================================================

def test_api_disturbance_status(client):
    """Test GET /disturbance/status."""
    response = client.get("/disturbance/status")
    assert response.status_code == 200
    data = response.json()
    assert data["initialized"] is True
    assert "severity" in data
    assert "config" in data


def test_api_disturbance_frame(client):
    """Test GET /disturbance/frame."""
    response = client.get("/disturbance/frame")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "width" in data
    assert "height" in data


def test_api_disturbance_telemetry(client):
    """Test GET /disturbance/telemetry."""
    response = client.get("/disturbance/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "noise_sigma" in data
    assert "blur_strength" in data
    assert "vibration_offset_x" in data
    assert "dropout_active" in data


def test_api_disturbance_image_png(client):
    """Test GET /disturbance/image returns valid PNG stream."""
    response = client.get("/disturbance/image")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0

    img = Image.open(io.BytesIO(response.content))
    assert img.format == "PNG"
    assert img.size == (640, 480)


def test_api_disturbance_config_update(client):
    """Test POST /disturbance/config updates parameters live."""
    new_cfg = {
        "severity": "high",
        "vibration_enabled": True,
        "vibration_magnitude": 4.5,
        "noise_enabled": True,
        "noise_magnitude": 0.2,
        "blur_enabled": True,
        "blur_strength": 3.0,
        "dropout_enabled": True,
        "dropout_probability": 0.2,
        "dropout_duration": 0.5,
    }
    response = client.post("/disturbance/config", json=new_cfg)
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "high"
    assert data["config"]["vibration_magnitude"] == 4.5


def test_api_disturbance_process(client):
    """Test POST /disturbance/process manually triggers a processing step."""
    response = client.post("/disturbance/process")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
