"""
Virtual Camera Simulation Engine.
Team PHARO — SIH26169

Encapsulates optical geometry, pinhole camera projection, and synthetic frame synthesis.
"""

from __future__ import annotations
from typing import Optional, Tuple
import numpy as np

from ..world.models import Vector3D, WorldState
from ..scenario.models import ScenarioConfig, CameraConfig, BeaconConfig
from .models import (
    CameraIntrinsics,
    CameraPose,
    ProjectedPoint,
    CameraAngles,
    CameraVisibility,
    CameraFrame,
    CameraStatus,
)
from .projection import (
    calculate_intrinsics,
    world_to_camera_frame,
    project_to_pixel,
    calculate_camera_angles,
    check_visibility,
)
from .renderer import (
    render_camera_frame,
    compute_spot_parameters,
)


class VirtualCamera:
    """
    Virtual Optical Receiver Camera Model.
    
    Transforms 3D world targets into 2D focal plane observations and renders
    synthetic optical sensor frames.
    """

    def __init__(self, scenario_config: Optional[ScenarioConfig] = None):
        self._scenario_name = "Default Scenario"
        self._config: Optional[CameraConfig] = None
        self._beacon_config: Optional[BeaconConfig] = None
        self._intrinsics: Optional[CameraIntrinsics] = None
        self._pose: CameraPose = CameraPose()
        self._initial_pan_deg: float = 0.0
        self._initial_tilt_deg: float = 0.0
        self._initialized: bool = False
        self._current_timestamp: float = 0.0
        self._last_frame: Optional[CameraFrame] = None
        self._last_image: Optional[np.ndarray] = None

        if scenario_config is not None:
            self.initialize_from_scenario(scenario_config)

    def initialize_from_scenario(self, scenario_config: ScenarioConfig) -> None:
        """
        Configure camera optical parameters, resolution, and initial pose from ScenarioConfig.
        """
        self._scenario_name = scenario_config.scenario_name
        self._config = scenario_config.camera
        self._beacon_config = scenario_config.beacon
        self._initial_pan_deg = scenario_config.camera.initial_pan_deg
        self._initial_tilt_deg = scenario_config.camera.initial_tilt_deg

        # Calculate camera optical intrinsics matrix
        self._intrinsics = calculate_intrinsics(
            width=self._config.width,
            height=self._config.height,
            hfov_deg=self._config.horizontal_fov_deg,
            vfov_deg=self._config.vertical_fov_deg,
        )

        # Initialize camera pose at receiver platform position with initial pan/tilt
        camera_pos = Vector3D(
            x=scenario_config.camera_platform.initial_position_x,
            y=scenario_config.camera_platform.initial_position_y,
            z=scenario_config.camera_platform.initial_position_z,
        )
        self._pose = CameraPose(
            position=camera_pos,
            pan_deg=self._initial_pan_deg,
            tilt_deg=self._initial_tilt_deg,
        )

        self._initialized = True
        self._current_timestamp = 0.0
        self._last_frame = None
        self._last_image = None

    def set_pose(
        self,
        position: Optional[Vector3D] = None,
        pan_deg: Optional[float] = None,
        tilt_deg: Optional[float] = None,
    ) -> CameraPose:
        """
        Update camera 3D position or gimbal orientation angles.
        """
        self._ensure_initialized()
        if position is not None:
            self._pose.position = position
        if pan_deg is not None:
            self._pose.pan_deg = pan_deg
        if tilt_deg is not None:
            self._pose.tilt_deg = tilt_deg
        return self._pose

    def get_pose(self) -> CameraPose:
        """Retrieve current camera pose."""
        self._ensure_initialized()
        return self._pose

    def get_intrinsics(self) -> CameraIntrinsics:
        """Retrieve optical intrinsics parameters."""
        self._ensure_initialized()
        return self._intrinsics

    def project_world_point(
        self,
        point_world: Vector3D,
    ) -> Tuple[Vector3D, ProjectedPoint, CameraAngles, CameraVisibility]:
        """
        Project an arbitrary 3D world point into camera-frame coordinates and 2D pixel coordinates.
        """
        self._ensure_initialized()

        # World-relative vector: r_world = point_world - camera_position
        r_world = point_world - self._pose.position

        # Transform to camera reference frame: X_c (right), Y_c (up), Z_c (forward)
        r_cam = world_to_camera_frame(r_world, self._pose.pan_deg, self._pose.tilt_deg)

        # Continuous pixel projection (u, v)
        proj = project_to_pixel(r_cam, self._intrinsics)

        # Apparent angles relative to camera boresight
        angles = calculate_camera_angles(r_cam)

        # Visibility and FOV classification
        visibility = check_visibility(r_cam, proj, self._intrinsics.width, self._intrinsics.height)

        return r_cam, proj, angles, visibility

    def project_beacon(self, world_state: WorldState) -> CameraFrame:
        """
        Compute projection metadata for the transmitter beacon from instantaneous WorldState.
        Synchronizes camera position with the receiver platform in world_state.
        """
        self._ensure_initialized()

        # Synchronize camera position with receiver platform
        self._pose.position = world_state.camera_platform.position
        self._current_timestamp = world_state.timestamp

        beacon_world_pos = world_state.beacon_platform.position
        r_cam, proj, angles, visibility = self.project_world_point(beacon_world_pos)

        intensity, radius = compute_spot_parameters(
            brightness=self._beacon_config.brightness if self._beacon_config else 1.0,
            size=self._beacon_config.size if self._beacon_config else 5.0,
        )

        frame = CameraFrame(
            timestamp=world_state.timestamp,
            width=self._intrinsics.width,
            height=self._intrinsics.height,
            visible=visibility.visible,
            camera_position=self._pose.position,
            camera_orientation={"pan_deg": self._pose.pan_deg, "tilt_deg": self._pose.tilt_deg},
            beacon_world_position=beacon_world_pos,
            beacon_camera_coordinates=r_cam,
            projection=proj,
            angles=angles,
            visibility=visibility,
            spot_radius=radius,
            spot_intensity=intensity,
        )
        self._last_frame = frame
        return frame

    def capture(self, world_state: WorldState) -> Tuple[CameraFrame, np.ndarray]:
        """
        Capture a complete observation frame: computes projection and renders synthetic sensor image.
        """
        frame = self.project_beacon(world_state)

        # Render clean synthetic optical sensor frame
        brightness = self._beacon_config.brightness if self._beacon_config else 1.0
        size = self._beacon_config.size if self._beacon_config else 5.0

        image_arr = render_camera_frame(
            width=self._intrinsics.width,
            height=self._intrinsics.height,
            projection=frame.projection,
            visibility=frame.visibility,
            brightness=brightness,
            size=size,
        )

        self._last_image = image_arr
        return frame, image_arr

    def reset(self) -> None:
        """
        Reset camera orientation to initial pan/tilt angles.
        """
        self._ensure_initialized()
        self._pose.pan_deg = self._initial_pan_deg
        self._pose.tilt_deg = self._initial_tilt_deg
        self._last_frame = None
        self._last_image = None

    def get_status(self) -> CameraStatus:
        """
        Get high-level status, optical parameters, and telemetry overview.
        """
        if not self._initialized:
            return CameraStatus(
                initialized=False,
                width=640,
                height=480,
                horizontal_fov_deg=30.0,
                vertical_fov_deg=22.5,
                pan_deg=0.0,
                tilt_deg=0.0,
                intrinsics=calculate_intrinsics(640, 480, 30.0, 22.5),
                current_timestamp=0.0,
                scenario_name="Uninitialized",
                last_frame_visible=None,
            )

        return CameraStatus(
            initialized=True,
            width=self._intrinsics.width,
            height=self._intrinsics.height,
            horizontal_fov_deg=self._intrinsics.hfov_deg,
            vertical_fov_deg=self._intrinsics.vfov_deg,
            pan_deg=self._pose.pan_deg,
            tilt_deg=self._pose.tilt_deg,
            intrinsics=self._intrinsics,
            current_timestamp=self._current_timestamp,
            scenario_name=self._scenario_name,
            last_frame_visible=self._last_frame.visible if self._last_frame else None,
        )

    def _ensure_initialized(self) -> None:
        if not self._initialized or self._intrinsics is None:
            raise RuntimeError("VirtualCamera is not initialized. Initialize with a ScenarioConfig first.")
