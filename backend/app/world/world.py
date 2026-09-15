"""
Virtual World Simulation Engine.
Team PHARO — SIH26169

Encapsulates 3D spatial coordinate frames, platforms, simulation clock,
ground-truth relative geometry calculations, and deterministic time propagation.
"""

from __future__ import annotations
import math
from typing import Optional, Dict, Any
from .models import (
    Vector3D,
    PlatformDefinition,
    PlatformState,
    RelativeGeometry,
    WorldState,
    WorldStatus,
)
from .platform import Platform
from ..scenario.models import ScenarioConfig


class World:
    """
    Core Virtual World Environment.
    Maintains ground-truth spatial coordinates, terminal platforms, and simulation time.
    """

    def __init__(self, scenario_config: Optional[ScenarioConfig] = None):
        self._current_time: float = 0.0
        self._duration: float = 30.0
        self._fps: float = 30.0
        self._dt: float = 1.0 / 30.0
        self._random_seed: int = 42
        self._scenario_name: str = "Unconfigured"
        self._initialized: bool = False

        self._camera_platform: Optional[Platform] = None
        self._beacon_platform: Optional[Platform] = None

        if scenario_config is not None:
            self.initialize_from_scenario(scenario_config)

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def current_time(self) -> float:
        return self._current_time

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def dt(self) -> float:
        return self._dt

    def initialize_from_scenario(self, scenario: ScenarioConfig) -> None:
        """Initialize world state and platform kinematics from ScenarioConfig."""
        self._scenario_name = scenario.scenario_name
        self._duration = scenario.simulation.duration
        self._fps = scenario.simulation.fps
        self._dt = 1.0 / scenario.simulation.fps if scenario.simulation.fps > 0 else 0.03333333333333333
        self._random_seed = scenario.simulation.random_seed
        self._current_time = 0.0

        # Receiver Camera Platform Definition
        cam_plat = scenario.camera_platform
        camera_def = PlatformDefinition(
            id="camera",
            name="Receiver Camera Platform",
            initial_position=Vector3D(
                x=cam_plat.initial_position_x,
                y=cam_plat.initial_position_y,
                z=cam_plat.initial_position_z,
            ),
            velocity=Vector3D(
                x=cam_plat.velocity_x,
                y=cam_plat.velocity_y,
                z=cam_plat.velocity_z,
            ),
            motion_profile=cam_plat.motion_profile,
            amplitude=cam_plat.amplitude,
            frequency=cam_plat.frequency,
        )
        self._camera_platform = Platform(camera_def)

        # Transmitter Beacon Platform Definition
        b_plat = scenario.beacon_platform
        beacon_def = PlatformDefinition(
            id="beacon",
            name="Transmitter Beacon Platform",
            initial_position=Vector3D(
                x=b_plat.initial_position_x,
                y=b_plat.initial_position_y,
                z=b_plat.initial_position_z,
            ),
            velocity=Vector3D(
                x=b_plat.velocity_x,
                y=b_plat.velocity_y,
                z=b_plat.velocity_z,
            ),
            motion_profile=b_plat.motion_profile,
            amplitude=b_plat.amplitude,
            frequency=b_plat.frequency,
        )
        self._beacon_platform = Platform(beacon_def)

        self._initialized = True

    def reset(self) -> WorldState:
        """Reset simulation clock back to t = 0.0 and re-evaluate initial state."""
        self._ensure_initialized()
        self._current_time = 0.0
        return self.get_state()

    def set_time(self, t: float) -> WorldState:
        """Explicitly set simulation clock to time t."""
        self._ensure_initialized()
        if t < 0.0:
            raise ValueError(f"Simulation time cannot be negative. Received t={t}")
        self._current_time = t
        return self.get_state()

    def update(self, dt: Optional[float] = None) -> WorldState:
        """Advance simulation clock by dt and return updated ground-truth state."""
        self._ensure_initialized()
        step_dt = self._dt if dt is None else dt
        if step_dt < 0.0:
            raise ValueError(f"Timestep dt cannot be negative. Received dt={step_dt}")
        self._current_time += step_dt
        return self.get_state()

    def get_time(self) -> float:
        return self._current_time

    def get_camera_platform(self) -> PlatformState:
        self._ensure_initialized()
        return self._camera_platform.get_state(self._current_time)

    def get_beacon_platform(self) -> PlatformState:
        self._ensure_initialized()
        return self._beacon_platform.get_state(self._current_time)

    def get_platform_state(self, platform_id: str) -> PlatformState:
        self._ensure_initialized()
        pid = platform_id.strip().lower()
        if pid in {"camera", "camera_platform", "receiver"}:
            return self.get_camera_platform()
        elif pid in {"beacon", "beacon_platform", "transmitter"}:
            return self.get_beacon_platform()
        raise KeyError(f"Unknown platform ID '{platform_id}'. Valid IDs are 'camera' or 'beacon'.")

    def get_relative_geometry(self) -> RelativeGeometry:
        """
        Calculate ground-truth relative geometry from Camera Platform to Beacon Platform.

        Equations:
          dx = x_b - x_c
          dy = y_b - y_c
          dz = z_b - z_c
          range = sqrt(dx^2 + dy^2 + dz^2)
          azimuth_deg = atan2(dx, dz) in degrees
          elevation_deg = atan2(dy, sqrt(dx^2 + dz^2)) in degrees
        """
        self._ensure_initialized()
        p_cam = self._camera_platform.get_position(self._current_time)
        p_beacon = self._beacon_platform.get_position(self._current_time)

        dx = p_beacon.x - p_cam.x
        dy = p_beacon.y - p_cam.y
        dz = p_beacon.z - p_cam.z

        range_val = math.sqrt(dx * dx + dy * dy + dz * dz)
        horiz_dist = math.sqrt(dx * dx + dz * dz)

        # Azimuth calculation: angle in horizontal X-Z plane
        if dx == 0.0 and dz == 0.0:
            azimuth_deg = 0.0
        else:
            azimuth_deg = math.degrees(math.atan2(dx, dz))

        # Elevation calculation: angle above/below horizontal plane
        if horiz_dist == 0.0:
            if dy > 0.0:
                elevation_deg = 90.0
            elif dy < 0.0:
                elevation_deg = -90.0
            else:
                elevation_deg = 0.0
        else:
            elevation_deg = math.degrees(math.atan2(dy, horiz_dist))

        return RelativeGeometry(
            relative_position=Vector3D(x=dx, y=dy, z=dz),
            range=range_val,
            azimuth_deg=azimuth_deg,
            elevation_deg=elevation_deg,
        )

    def get_state(self) -> WorldState:
        """Generate and return full ground-truth WorldState snapshot."""
        self._ensure_initialized()
        cam_state = self.get_camera_platform()
        beacon_state = self.get_beacon_platform()
        rel_geom = self.get_relative_geometry()

        return WorldState(
            timestamp=self._current_time,
            camera_platform=cam_state,
            beacon_platform=beacon_state,
            relative_geometry=rel_geom,
        )

    def get_status(self) -> WorldStatus:
        """Return world simulation status."""
        if not self._initialized:
            return WorldStatus(
                initialized=False,
                current_time=0.0,
                duration=30.0,
                fps=30.0,
                dt=0.03333333333333333,
                scenario_name="Uninitialized",
            )

        return WorldStatus(
            initialized=True,
            current_time=self._current_time,
            duration=self._duration,
            fps=self._fps,
            dt=self._dt,
            scenario_name=self._scenario_name,
            camera_platform=self.get_camera_platform(),
            beacon_platform=self.get_beacon_platform(),
            relative_geometry=self.get_relative_geometry(),
        )

    def _ensure_initialized(self) -> None:
        if not self._initialized or self._camera_platform is None or self._beacon_platform is None:
            raise RuntimeError("World has not been initialized. Please call initialize_from_scenario() first.")
