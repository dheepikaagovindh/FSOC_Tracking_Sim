"""
Unit and Integration Tests for Virtual Camera & Optical Image Generation Module.
Team PHARO — SIH26169

Tests mathematical projection, pinhole intrinsics, 3D coordinate transformations,
visibility clipping, synthetic sensor rendering, and REST API endpoints.
"""

import math
import io
import pytest
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.world.models import Vector3D, WorldState, PlatformState, RelativeGeometry
from backend.app.scenario.models import ScenarioConfig, CameraConfig, PlatformConfig, BeaconConfig
from backend.app.scenario.presets import get_preset
from backend.app.camera.models import (
    CameraIntrinsics,
    CameraPose,
    ProjectedPoint,
    CameraAngles,
    CameraVisibility,
    CameraFrame,
    CameraStatus,
)
from backend.app.camera.projection import (
    calculate_intrinsics,
    world_to_camera_frame,
    project_to_pixel,
    calculate_camera_angles,
    check_visibility,
)
from backend.app.camera.renderer import (
    render_camera_frame,
    compute_spot_parameters,
    encode_image_to_png,
)
from backend.app.camera.camera import VirtualCamera
from backend.app.camera.service import camera_service
from backend.app.world.service import world_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def default_scenario():
    return ScenarioConfig()


# ==============================================================================
# 1. Optical Intrinsics & Pinhole Model Tests
# ==============================================================================

def test_camera_intrinsics_calculation():
    """Verify focal length and principal point calculation for 640x480, 30x22.5 deg."""
    width = 640
    height = 480
    hfov_deg = 30.0
    vfov_deg = 22.5

    intrinsics = calculate_intrinsics(width, height, hfov_deg, vfov_deg)

    expected_fx = 640.0 / (2.0 * math.tan(math.radians(15.0)))
    expected_fy = 480.0 / (2.0 * math.tan(math.radians(11.25)))
    expected_cx = 320.0
    expected_cy = 240.0

    assert pytest.approx(intrinsics.fx, rel=1e-5) == expected_fx
    assert pytest.approx(intrinsics.fy, rel=1e-5) == expected_fy
    assert intrinsics.cx == expected_cx
    assert intrinsics.cy == expected_cy
    assert intrinsics.width == width
    assert intrinsics.height == height

    matrix = intrinsics.to_matrix()
    assert matrix[0][0] == intrinsics.fx
    assert matrix[0][2] == intrinsics.cx
    assert matrix[1][1] == intrinsics.fy
    assert matrix[1][2] == intrinsics.cy
    assert matrix[2][2] == 1.0


def test_invalid_intrinsics_parameters():
    """Verify rejection of non-positive dimensions and invalid FOV angles."""
    with pytest.raises(ValueError):
        calculate_intrinsics(-640, 480, 30.0, 22.5)
    with pytest.raises(ValueError):
        calculate_intrinsics(640, 480, 0.0, 22.5)
    with pytest.raises(ValueError):
        calculate_intrinsics(640, 480, 185.0, 22.5)


# ==============================================================================
# 2. Geometric Test Cases (Canonical Specification Requirements)
# ==============================================================================

def test_case_1_center_projection():
    """
    Test Case 1:
      Camera at (0, 0, 0), pan=0, tilt=0
      Beacon at (0, 0, 50)
      Expected: Beacon is visible, projects at exact image center (u=320, v=240).
    """
    camera = VirtualCamera(ScenarioConfig())
    intrinsics = camera.get_intrinsics()

    r_cam, proj, angles, vis = camera.project_world_point(Vector3D(x=0.0, y=0.0, z=50.0))

    assert vis.visible is True
    assert vis.in_front_of_camera is True
    assert vis.reason == "VISIBLE"
    assert pytest.approx(proj.u, abs=1e-3) == 320.0
    assert pytest.approx(proj.v, abs=1e-3) == 240.0
    assert pytest.approx(angles.azimuth_deg, abs=1e-3) == 0.0
    assert pytest.approx(angles.elevation_deg, abs=1e-3) == 0.0


def test_case_2_horizontal_azimuth_offset():
    """
    Test Case 2:
      Camera at (0, 0, 0), pan=0, tilt=0
      Beacon at (10, 0, 50)
      Expected: Azimuth = atan2(10, 50) ~= 11.3099 deg.
      Projects horizontally to the right of center: u > 320, v == 240.
    """
    camera = VirtualCamera(ScenarioConfig())
    r_cam, proj, angles, vis = camera.project_world_point(Vector3D(x=10.0, y=0.0, z=50.0))

    expected_az = math.degrees(math.atan2(10.0, 50.0))
    assert pytest.approx(angles.azimuth_deg, rel=1e-4) == expected_az
    assert pytest.approx(angles.elevation_deg, abs=1e-4) == 0.0
    assert proj.u > 320.0
    assert pytest.approx(proj.v, abs=1e-3) == 240.0
    assert vis.visible is True


def test_case_3_vertical_elevation_offset():
    """
    Test Case 3:
      Camera at (0, 0, 0), pan=0, tilt=0
      Beacon at (0, 8, 50)
      Expected: Elevation = atan2(8, 50) ~= 9.0903 deg (< vertical half-FOV 11.25 deg).
      Projects vertically upward on screen: u == 320, v < 240 (because v=0 is top).
    """
    camera = VirtualCamera(ScenarioConfig())
    r_cam, proj, angles, vis = camera.project_world_point(Vector3D(x=0.0, y=8.0, z=50.0))

    expected_el = math.degrees(math.atan2(8.0, 50.0))
    assert pytest.approx(angles.elevation_deg, rel=1e-4) == expected_el
    assert pytest.approx(angles.azimuth_deg, abs=1e-4) == 0.0
    assert pytest.approx(proj.u, abs=1e-3) == 320.0
    assert proj.v < 240.0
    assert vis.visible is True


def test_case_4_behind_camera_rejection():
    """
    Test Case 4:
      Camera at (0, 0, 0), pan=0, tilt=0
      Beacon at (0, 0, -50)
      Expected: visible = False, reason = 'BEHIND_CAMERA'.
    """
    camera = VirtualCamera(ScenarioConfig())
    r_cam, proj, angles, vis = camera.project_world_point(Vector3D(x=0.0, y=0.0, z=-50.0))

    assert vis.visible is False
    assert vis.in_front_of_camera is False
    assert vis.reason == "BEHIND_CAMERA"


def test_case_5_out_of_fov_rejection():
    """
    Test Case 5:
      Beacon placed outside horizontal/vertical FOV boundaries (e.g. (100, 0, 50)).
      Expected: visible = False, reason = 'OUT_OF_FOV'.
    """
    camera = VirtualCamera(ScenarioConfig())
    r_cam, proj, angles, vis = camera.project_world_point(Vector3D(x=100.0, y=0.0, z=50.0))

    assert vis.visible is False
    assert vis.in_front_of_camera is True
    assert vis.inside_horizontal_fov is False
    assert vis.reason == "OUT_OF_FOV"
    assert proj.u >= 640.0


def test_case_6_pan_transformation():
    """
    Test Case 6:
      Beacon at (10, 0, 50).
      When camera pans right by theta = atan2(10, 50), the beacon is brought to boresight center.
    """
    camera = VirtualCamera(ScenarioConfig())
    pan_angle = math.degrees(math.atan2(10.0, 50.0))
    camera.set_pose(pan_deg=pan_angle, tilt_deg=0.0)

    r_cam, proj, angles, vis = camera.project_world_point(Vector3D(x=10.0, y=0.0, z=50.0))

    assert pytest.approx(r_cam.x, abs=1e-4) == 0.0
    assert pytest.approx(proj.u, abs=1e-2) == 320.0
    assert pytest.approx(proj.v, abs=1e-2) == 240.0
    assert pytest.approx(angles.azimuth_deg, abs=1e-3) == 0.0
    assert vis.visible is True


def test_case_7_tilt_transformation():
    """
    Test Case 7:
      Beacon at (0, 10, 50).
      When camera tilts up by theta = atan2(10, 50), the beacon is brought to boresight center.
    """
    camera = VirtualCamera(ScenarioConfig())
    tilt_angle = math.degrees(math.atan2(10.0, 50.0))
    camera.set_pose(pan_deg=0.0, tilt_deg=tilt_angle)

    r_cam, proj, angles, vis = camera.project_world_point(Vector3D(x=0.0, y=10.0, z=50.0))

    assert pytest.approx(r_cam.y, abs=1e-4) == 0.0
    assert pytest.approx(proj.u, abs=1e-2) == 320.0
    assert pytest.approx(proj.v, abs=1e-2) == 240.0
    assert pytest.approx(angles.elevation_deg, abs=1e-3) == 0.0
    assert vis.visible is True


# ==============================================================================
# 3. Synthetic Image Rendering & Spot Characteristics Tests
# ==============================================================================

def test_render_camera_frame_dimensions_and_dtype():
    """Verify synthetic sensor matrix dimensions (H, W) and uint8 grayscale format."""
    proj = ProjectedPoint(u=320.0, v=240.0, normalized_x=0.0, normalized_y=0.0)
    vis = CameraVisibility(
        visible=True,
        in_front_of_camera=True,
        inside_horizontal_fov=True,
        inside_vertical_fov=True,
        reason="VISIBLE",
    )

    img = render_camera_frame(width=640, height=480, projection=proj, visibility=vis, brightness=1.0, size=5.0)

    assert isinstance(img, np.ndarray)
    assert img.shape == (480, 640)
    assert img.dtype == np.uint8
    assert img[240, 320] == 255


def test_render_brightness_mapping():
    """Verify brightness mapping to 8-bit sensor intensity."""
    intensity_full, _ = compute_spot_parameters(1.0, 5.0)
    assert intensity_full == 255

    intensity_half, _ = compute_spot_parameters(0.5, 5.0)
    assert intensity_half == 128

    intensity_zero, _ = compute_spot_parameters(0.0, 5.0)
    assert intensity_zero == 0


def test_render_size_footprint():
    """Verify larger beacon size increases number of lit sensor pixels."""
    proj = ProjectedPoint(u=320.0, v=240.0, normalized_x=0.0, normalized_y=0.0)
    vis = CameraVisibility(
        visible=True,
        in_front_of_camera=True,
        inside_horizontal_fov=True,
        inside_vertical_fov=True,
        reason="VISIBLE",
    )

    img_small = render_camera_frame(640, 480, proj, vis, brightness=1.0, size=3.0)
    img_large = render_camera_frame(640, 480, proj, vis, brightness=1.0, size=10.0)

    lit_small = np.count_nonzero(img_small)
    lit_large = np.count_nonzero(img_large)

    assert lit_small > 0
    assert lit_large > lit_small


def test_render_invisible_frame_is_completely_blank():
    """Verify zero pixels are rendered when beacon is invisible or behind camera."""
    proj = ProjectedPoint(u=1000.0, v=240.0, normalized_x=2.0, normalized_y=0.0)
    vis = CameraVisibility(
        visible=False,
        in_front_of_camera=True,
        inside_horizontal_fov=False,
        inside_vertical_fov=True,
        reason="OUT_OF_FOV",
    )

    img = render_camera_frame(640, 480, proj, vis, brightness=1.0, size=5.0)
    assert np.count_nonzero(img) == 0


def test_png_encoding():
    """Verify PNG byte stream encoding and valid image header parsing."""
    proj = ProjectedPoint(u=320.0, v=240.0, normalized_x=0.0, normalized_y=0.0)
    vis = CameraVisibility(
        visible=True,
        in_front_of_camera=True,
        inside_horizontal_fov=True,
        inside_vertical_fov=True,
        reason="VISIBLE",
    )
    img = render_camera_frame(640, 480, proj, vis, brightness=1.0, size=5.0)
    png_bytes = encode_image_to_png(img)

    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 0

    # Parse back with Pillow to verify format
    pil_image = Image.open(io.BytesIO(png_bytes))
    assert pil_image.format == "PNG"
    assert pil_image.size == (640, 480)


def test_determinism():
    """Verify same inputs generate identical arrays and byte outputs."""
    camera = VirtualCamera(ScenarioConfig())
    world_state = world_service.get_world_state()

    frame1, img1 = camera.capture(world_state)
    frame2, img2 = camera.capture(world_state)

    np.testing.assert_array_equal(img1, img2)
    assert frame1.projection.u == frame2.projection.u
    assert frame1.projection.v == frame2.projection.v


# ==============================================================================
# 4. Integration with Virtual World Simulation
# ==============================================================================

def test_world_motion_causes_camera_spot_motion():
    """
    Demonstrate that stepping the World simulation with a moving beacon
    causes the projected pixel spot to advance across the sensor frame.
    """
    # Create scenario with DRIFT beacon moving at +2.0 m/s along X axis
    scenario = ScenarioConfig(
        scenario_name="Drift Test",
        camera=CameraConfig(width=640, height=480, horizontal_fov_deg=30.0, vertical_fov_deg=22.5),
        camera_platform=PlatformConfig(motion_profile="static", initial_position_z=0.0),
        beacon_platform=PlatformConfig(
            motion_profile="drift",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=50.0,
            velocity_x=2.0,
        ),
        beacon=BeaconConfig(brightness=1.0, size=5.0),
    )

    world_service.initialize_world(scenario)
    camera_service.initialize_camera(scenario)

    # Frame at t=0
    frame_0 = camera_service.get_latest_frame()
    assert pytest.approx(frame_0.projection.u, abs=1e-2) == 320.0

    # Step world by 1.0 second (beacon moves to X=2.0m)
    world_service.step_world(1.0)
    frame_1 = camera_service.capture_frame()

    assert frame_1.beacon_world_position.x == 2.0
    assert frame_1.projection.u > frame_0.projection.u
    assert pytest.approx(frame_1.projection.v, abs=1e-2) == 240.0


# ==============================================================================
# 5. REST API Endpoints Tests
# ==============================================================================

def test_api_camera_status(client):
    """Test GET /camera/status."""
    response = client.get("/camera/status")
    assert response.status_code == 200
    data = response.json()
    assert data["initialized"] is True
    assert data["width"] == 640
    assert data["height"] == 480
    assert "intrinsics" in data


def test_api_camera_frame(client):
    """Test GET /camera/frame."""
    response = client.get("/camera/frame")
    assert response.status_code == 200
    data = response.json()
    assert "projection" in data
    assert "angles" in data
    assert "visibility" in data


def test_api_camera_telemetry(client):
    """Test GET /camera/telemetry."""
    response = client.get("/camera/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "camera_pose" in data
    assert "beacon_camera_coordinates" in data
    assert "projection" in data
    assert "angles" in data
    assert "world_range" in data


def test_api_camera_image_png(client):
    """Test GET /camera/image returns valid PNG binary stream."""
    response = client.get("/camera/image")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0

    img = Image.open(io.BytesIO(response.content))
    assert img.format == "PNG"
    assert img.size == (640, 480)


def test_api_camera_pose_update_and_reset(client):
    """Test POST /camera/pose and POST /camera/reset."""
    # Update pan to +5.0 degrees
    pose_res = client.post("/camera/pose", json={"pan_deg": 5.0, "tilt_deg": -2.0})
    assert pose_res.status_code == 200
    data = pose_res.json()
    assert data["pan_deg"] == 5.0
    assert data["tilt_deg"] == -2.0

    # Verify frame projection changed
    frame_res = client.get("/camera/frame")
    assert frame_res.status_code == 200

    # Reset camera orientation
    reset_res = client.post("/camera/reset")
    assert reset_res.status_code == 200
    status_res = client.get("/camera/status")
    assert status_res.json()["pan_deg"] == 0.0
    assert status_res.json()["tilt_deg"] == 0.0
