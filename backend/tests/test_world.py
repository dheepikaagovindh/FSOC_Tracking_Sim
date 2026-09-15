"""
Comprehensive Unit & Integration Test Suite for FSOC Virtual World & Platform Simulation Module.
Team PHARO — SIH26169
"""

import math
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.world.models import Vector3D, PlatformDefinition, PlatformState, RelativeGeometry, WorldState
from app.world.motion import (
    MotionEngine,
    StaticMotionProfile,
    DriftMotionProfile,
    SwayMotionProfile,
    OrbitMotionProfile,
)
from app.world.platform import Platform
from app.world.world import World
from app.world.service import world_service
from app.scenario.models import ScenarioConfig, PlatformConfig, SimulationConfig
from app.scenario.presets import get_easy_acquisition_preset, get_full_stress_test_preset

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Vector3D & Math Primitives Tests
# ---------------------------------------------------------------------------

def test_vector3d_operations():
    v1 = Vector3D(x=1.0, y=2.0, z=3.0)
    v2 = Vector3D(x=4.0, y=5.0, z=6.0)

    v_add = v1 + v2
    assert v_add.x == 5.0 and v_add.y == 7.0 and v_add.z == 9.0

    v_sub = v2 - v1
    assert v_sub.x == 3.0 and v_sub.y == 3.0 and v_sub.z == 3.0

    v_mul = v1 * 2.0
    assert v_mul.x == 2.0 and v_mul.y == 4.0 and v_mul.z == 6.0

    assert pytest.approx(v1.magnitude(), 1e-5) == math.sqrt(1 + 4 + 9)
    assert pytest.approx(v1.distance_to(v2), 1e-5) == math.sqrt(9 + 9 + 9)


# ---------------------------------------------------------------------------
# 2. Motion Profile Kinematics Tests
# ---------------------------------------------------------------------------

def test_static_motion_profile():
    p_def = PlatformDefinition(
        id="test_static",
        name="Static Platform",
        initial_position=Vector3D(x=10.0, y=-5.0, z=100.0),
        motion_profile="static",
    )
    pos, vel = MotionEngine.calculate_state(p_def, t=0.0)
    assert pos.x == 10.0 and pos.y == -5.0 and pos.z == 100.0
    assert vel.x == 0.0 and vel.y == 0.0 and vel.z == 0.0

    pos_t, vel_t = MotionEngine.calculate_state(p_def, t=100.0)
    assert pos_t.x == 10.0 and pos_t.y == -5.0 and pos_t.z == 100.0
    assert vel_t.x == 0.0 and vel_t.y == 0.0 and vel_t.z == 0.0


def test_drift_motion_profile():
    p_def = PlatformDefinition(
        id="test_drift",
        name="Drift Platform",
        initial_position=Vector3D(x=0.0, y=10.0, z=50.0),
        velocity=Vector3D(x=2.0, y=-1.0, z=0.5),
        motion_profile="drift",
    )
    pos_0, vel_0 = MotionEngine.calculate_state(p_def, t=0.0)
    assert pos_0.x == 0.0 and pos_0.y == 10.0 and pos_0.z == 50.0
    assert vel_0.x == 2.0 and vel_0.y == -1.0 and vel_0.z == 0.5

    pos_5, vel_5 = MotionEngine.calculate_state(p_def, t=5.0)
    assert pytest.approx(pos_5.x, 1e-5) == 10.0
    assert pytest.approx(pos_5.y, 1e-5) == 5.0
    assert pytest.approx(pos_5.z, 1e-5) == 52.5
    assert vel_5.x == 2.0 and vel_5.y == -1.0 and vel_5.z == 0.5


def test_sway_motion_profile():
    # Harmonic motion: x(t) = x0 + A * sin(2*pi*f*t), vx(t) = A * 2*pi*f * cos(2*pi*f*t)
    A = 10.0
    f = 0.5  # Period T = 2.0s, omega = pi
    p_def = PlatformDefinition(
        id="test_sway",
        name="Sway Platform",
        initial_position=Vector3D(x=0.0, y=0.0, z=100.0),
        motion_profile="sway",
        amplitude=A,
        frequency=f,
    )

    # t = 0.0: sin(0) = 0, cos(0) = 1 -> pos.x = 0, vel.x = A*omega = 10 * pi
    pos_0, vel_0 = MotionEngine.calculate_state(p_def, t=0.0)
    assert pytest.approx(pos_0.x, 1e-5) == 0.0
    assert pytest.approx(vel_0.x, 1e-5) == A * 2.0 * math.pi * f

    # t = 0.5s (Quarter period): sin(pi/2) = 1, cos(pi/2) = 0 -> pos.x = 10, vel.x = 0
    pos_q, vel_q = MotionEngine.calculate_state(p_def, t=0.5)
    assert pytest.approx(pos_q.x, 1e-5) == 10.0
    assert pytest.approx(vel_q.x, 1e-5) == 0.0

    # t = 1.0s (Half period): sin(pi) = 0, cos(pi) = -1 -> pos.x = 0, vel.x = -10 * pi
    pos_h, vel_h = MotionEngine.calculate_state(p_def, t=1.0)
    assert pytest.approx(pos_h.x, 1e-5) == 0.0
    assert pytest.approx(vel_h.x, 1e-5) == -A * 2.0 * math.pi * f


def test_orbit_motion_profile():
    # Orbit: x(t) = cx + R*cos(2*pi*f*t), z(t) = cz + R*sin(2*pi*f*t)
    # vx(t) = -R*omega*sin(omega*t), vz(t) = R*omega*cos(omega*t)
    R = 20.0
    f = 0.25  # Period T = 4s, omega = 0.5*pi
    p_def = PlatformDefinition(
        id="test_orbit",
        name="Orbit Platform",
        initial_position=Vector3D(x=5.0, y=2.0, z=50.0),
        motion_profile="orbit",
        amplitude=R,
        frequency=f,
    )

    # t = 0: cos(0)=1, sin(0)=0 -> x = 5 + 20 = 25, z = 50, vx = 0, vz = R*omega
    pos_0, vel_0 = MotionEngine.calculate_state(p_def, t=0.0)
    assert pytest.approx(pos_0.x, 1e-5) == 25.0
    assert pytest.approx(pos_0.y, 1e-5) == 2.0
    assert pytest.approx(pos_0.z, 1e-5) == 50.0
    assert pytest.approx(vel_0.x, 1e-5) == 0.0
    assert pytest.approx(vel_0.z, 1e-5) == R * 2.0 * math.pi * f

    # t = 1s (Quarter period): cos(pi/2)=0, sin(pi/2)=1 -> x = 5, z = 50 + 20 = 70
    pos_q, vel_q = MotionEngine.calculate_state(p_def, t=1.0)
    assert pytest.approx(pos_q.x, 1e-5) == 5.0
    assert pytest.approx(pos_q.z, 1e-5) == 70.0
    assert pytest.approx(vel_q.x, 1e-5) == -R * 2.0 * math.pi * f
    assert pytest.approx(vel_q.z, 1e-5) == 0.0


# ---------------------------------------------------------------------------
# 3. Relative Geometry & Angle Conventions Tests
# ---------------------------------------------------------------------------

def test_geometry_on_axis_forward():
    # Camera at (0,0,0), Beacon at (0,0,10)
    scenario = ScenarioConfig(
        camera_platform=PlatformConfig(initial_position_x=0.0, initial_position_y=0.0, initial_position_z=0.0),
        beacon_platform=PlatformConfig(initial_position_x=0.0, initial_position_y=0.0, initial_position_z=10.0),
    )
    world = World(scenario)
    geom = world.get_relative_geometry()

    assert geom.relative_position.x == 0.0
    assert geom.relative_position.y == 0.0
    assert geom.relative_position.z == 10.0
    assert pytest.approx(geom.range, 1e-5) == 10.0
    assert pytest.approx(geom.azimuth_deg, 1e-5) == 0.0
    assert pytest.approx(geom.elevation_deg, 1e-5) == 0.0


def test_geometry_horizontal_azimuth_offsets():
    # Camera at (0,0,0), Beacon at (10,0,10) -> Azimuth = atan2(10, 10) = 45 deg
    scenario_45 = ScenarioConfig(
        camera_platform=PlatformConfig(initial_position_x=0.0, initial_position_y=0.0, initial_position_z=0.0),
        beacon_platform=PlatformConfig(initial_position_x=10.0, initial_position_y=0.0, initial_position_z=10.0),
    )
    world_45 = World(scenario_45)
    geom_45 = world_45.get_relative_geometry()
    assert pytest.approx(geom_45.azimuth_deg, 1e-4) == 45.0
    assert pytest.approx(geom_45.range, 1e-4) == math.sqrt(200.0)

    # Beacon at (-10,0,10) -> Azimuth = -45 deg
    scenario_neg45 = ScenarioConfig(
        camera_platform=PlatformConfig(initial_position_x=0.0, initial_position_y=0.0, initial_position_z=0.0),
        beacon_platform=PlatformConfig(initial_position_x=-10.0, initial_position_y=0.0, initial_position_z=10.0),
    )
    world_neg45 = World(scenario_neg45)
    geom_neg45 = world_neg45.get_relative_geometry()
    assert pytest.approx(geom_neg45.azimuth_deg, 1e-4) == -45.0


def test_geometry_elevation_offsets():
    # Camera at (0,0,10), Beacon at (0,10,20) -> dy=10, dz=10, dx=0 -> horiz=10 -> elevation = 45 deg
    scenario_el = ScenarioConfig(
        camera_platform=PlatformConfig(initial_position_x=0.0, initial_position_y=0.0, initial_position_z=10.0),
        beacon_platform=PlatformConfig(initial_position_x=0.0, initial_position_y=10.0, initial_position_z=20.0),
    )
    world_el = World(scenario_el)
    geom_el = world_el.get_relative_geometry()
    assert pytest.approx(geom_el.elevation_deg, 1e-4) == 45.0
    assert pytest.approx(geom_el.azimuth_deg, 1e-4) == 0.0


def test_geometry_boundary_zero_range_and_vertical():
    # Both platforms at exact same coordinate (0,0,0) -> Range 0, Azimuth 0, Elevation 0
    scenario_zero = ScenarioConfig(
        camera_platform=PlatformConfig(initial_position_x=0.0, initial_position_y=0.0, initial_position_z=0.0),
        beacon_platform=PlatformConfig(initial_position_x=0.0, initial_position_y=0.0, initial_position_z=0.0),
    )
    world_zero = World(scenario_zero)
    geom_zero = world_zero.get_relative_geometry()
    assert geom_zero.range == 0.0
    assert geom_zero.azimuth_deg == 0.0
    assert geom_zero.elevation_deg == 0.0

    # Zero horizontal distance, vertical offset: Camera (0,0,0), Beacon (0,15,0) -> Elevation = 90 deg
    scenario_up = ScenarioConfig(
        camera_platform=PlatformConfig(initial_position_x=0.0, initial_position_y=0.0, initial_position_z=0.0),
        beacon_platform=PlatformConfig(initial_position_x=0.0, initial_position_y=15.0, initial_position_z=0.0),
    )
    world_up = World(scenario_up)
    geom_up = world_up.get_relative_geometry()
    assert pytest.approx(geom_up.elevation_deg, 1e-4) == 90.0
    assert geom_up.azimuth_deg == 0.0


# ---------------------------------------------------------------------------
# 4. World State & Simulation Clock Tests
# ---------------------------------------------------------------------------

def test_world_step_and_reset():
    scenario = ScenarioConfig(
        camera_platform=PlatformConfig(motion_profile="static", initial_position_x=0.0, initial_position_z=0.0),
        beacon_platform=PlatformConfig(motion_profile="drift", initial_position_z=100.0, velocity_x=10.0),
        simulation=SimulationConfig(fps=20.0, duration=10.0),
    )
    world = World(scenario)
    assert world.current_time == 0.0
    assert world.dt == 0.05

    # Step by 1 frame (0.05s)
    state_1 = world.update()
    assert pytest.approx(world.current_time, 1e-5) == 0.05
    assert pytest.approx(state_1.beacon_platform.position.x, 1e-5) == 0.5

    # Step by explicit dt = 0.5s
    state_2 = world.update(dt=0.5)
    assert pytest.approx(world.current_time, 1e-5) == 0.55
    assert pytest.approx(state_2.beacon_platform.position.x, 1e-5) == 5.5

    # Reset
    state_reset = world.reset()
    assert state_reset.timestamp == 0.0
    assert state_reset.beacon_platform.position.x == 0.0


def test_explicit_time_setting():
    scenario = ScenarioConfig(
        beacon_platform=PlatformConfig(motion_profile="drift", velocity_x=5.0, initial_position_z=50.0),
    )
    world = World(scenario)
    state_10 = world.set_time(10.0)
    assert state_10.timestamp == 10.0
    assert pytest.approx(state_10.beacon_platform.position.x, 1e-5) == 50.0

    with pytest.raises(ValueError):
        world.set_time(-1.0)


def test_deterministic_behavior():
    scenario = get_full_stress_test_preset()
    world1 = World(scenario)
    world2 = World(scenario)

    for _ in range(50):
        s1 = world1.update()
        s2 = world2.update()
        assert s1.timestamp == s2.timestamp
        assert s1.camera_platform.position.x == s2.camera_platform.position.x
        assert s1.beacon_platform.position.z == s2.beacon_platform.position.z
        assert s1.relative_geometry.range == s2.relative_geometry.range
        assert s1.relative_geometry.azimuth_deg == s2.relative_geometry.azimuth_deg


def test_initial_demo_scenario_spec():
    """
    Verify the initial demo scenario requirement:
      Camera: (0, 0, 0), static
      Beacon: (0, 0, 50), drift with velocity (0.5, 0, 0)
      At t=0: Beacon=(0,0,50), range=50
      At t=1: Beacon=(0.5,0,50), range~50.0025, azimuth~0.573 deg
      At t=2: Beacon=(1.0,0,50), range~50.01, azimuth~1.146 deg
    """
    demo_scenario = ScenarioConfig(
        scenario_name="Demo Drift Scenario",
        camera_platform=PlatformConfig(motion_profile="static", initial_position_x=0.0, initial_position_y=0.0, initial_position_z=0.0),
        beacon_platform=PlatformConfig(motion_profile="drift", initial_position_x=0.0, initial_position_y=0.0, initial_position_z=50.0, velocity_x=0.5),
        simulation=SimulationConfig(fps=30.0, duration=20.0),
    )
    world = World(demo_scenario)

    # t = 0
    s0 = world.get_state()
    assert s0.beacon_platform.position.x == 0.0
    assert s0.beacon_platform.position.z == 50.0
    assert pytest.approx(s0.relative_geometry.range, 1e-4) == 50.0
    assert pytest.approx(s0.relative_geometry.azimuth_deg, 1e-4) == 0.0

    # t = 1.0
    s1 = world.set_time(1.0)
    assert pytest.approx(s1.beacon_platform.position.x, 1e-4) == 0.5
    assert pytest.approx(s1.beacon_platform.position.z, 1e-4) == 50.0
    expected_r1 = math.sqrt(0.5**2 + 50.0**2)
    expected_az1 = math.degrees(math.atan2(0.5, 50.0))
    assert pytest.approx(s1.relative_geometry.range, 1e-4) == expected_r1
    assert pytest.approx(s1.relative_geometry.azimuth_deg, 1e-4) == expected_az1

    # t = 2.0
    s2 = world.set_time(2.0)
    assert pytest.approx(s2.beacon_platform.position.x, 1e-4) == 1.0
    assert pytest.approx(s2.beacon_platform.position.z, 1e-4) == 50.0
    expected_r2 = math.sqrt(1.0**2 + 50.0**2)
    expected_az2 = math.degrees(math.atan2(1.0, 50.0))
    assert pytest.approx(s2.relative_geometry.range, 1e-4) == expected_r2
    assert pytest.approx(s2.relative_geometry.azimuth_deg, 1e-4) == expected_az2


# ---------------------------------------------------------------------------
# 5. FastAPI World REST API Tests
# ---------------------------------------------------------------------------

def test_api_world_initialize():
    res = client.post("/world/initialize")
    assert res.status_code == 200
    data = res.json()
    assert "timestamp" in data
    assert "camera_platform" in data
    assert "beacon_platform" in data
    assert "relative_geometry" in data


def test_api_world_status():
    res = client.get("/world/status")
    assert res.status_code == 200
    status_data = res.json()
    assert status_data["initialized"] is True
    assert status_data["fps"] > 0
    assert status_data["duration"] > 0


def test_api_world_step():
    res = client.post("/world/step", json={"dt": 0.1})
    assert res.status_code == 200
    data = res.json()
    assert pytest.approx(data["timestamp"], 1e-4) == 0.1


def test_api_world_reset():
    client.post("/world/step", json={"dt": 1.0})
    res_reset = client.post("/world/reset")
    assert res_reset.status_code == 200
    assert res_reset.json()["timestamp"] == 0.0


def test_api_world_state_and_geometry():
    res_state = client.get("/world/state")
    assert res_state.status_code == 200
    assert "relative_geometry" in res_state.json()

    res_geom = client.get("/world/geometry")
    assert res_geom.status_code == 200
    assert "range" in res_geom.json()
    assert "azimuth_deg" in res_geom.json()
    assert "elevation_deg" in res_geom.json()


def test_api_world_platform_by_id():
    res_cam = client.get("/world/platform/camera")
    assert res_cam.status_code == 200
    assert res_cam.json()["platform_id"] == "camera"

    res_beacon = client.get("/world/platform/beacon")
    assert res_beacon.status_code == 200
    assert res_beacon.json()["platform_id"] == "beacon"

    res_invalid = client.get("/world/platform/satellite_dish")
    assert res_invalid.status_code == 404
