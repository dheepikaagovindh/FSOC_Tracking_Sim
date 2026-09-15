"""
Virtual Camera Service Layer.
Team PHARO — SIH26169

Provides thread-safe singleton state and application orchestration for the Virtual Camera module,
bridging Scenario Configuration and Virtual World simulation state.
"""

from __future__ import annotations
import threading
from typing import Optional, Tuple
import numpy as np

from .camera import VirtualCamera
from .models import CameraFrame, CameraStatus, CameraPose, CameraIntrinsics
from .renderer import encode_image_to_png
from ..scenario.models import ScenarioConfig
from ..scenario.service import scenario_service
from ..world.service import world_service


class CameraService:
    """
    Singleton service orchestrating Virtual Camera instances, frame rendering,
    and REST API interactions.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CameraService, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self._mutex = threading.RLock()
        active_scenario = scenario_service.get_active_scenario()
        self._camera = VirtualCamera(active_scenario)
        # Capture initial frame at t=0
        world_state = world_service.get_world_state()
        self._latest_frame, self._latest_image = self._camera.capture(world_state)
        self._latest_png_bytes = encode_image_to_png(self._latest_image)

    def initialize_camera(self, scenario: Optional[ScenarioConfig] = None) -> CameraStatus:
        """
        Initialize or re-initialize camera from ScenarioConfig and sync with current world state.
        """
        with self._mutex:
            target_scenario = scenario or scenario_service.get_active_scenario()
            self._camera.initialize_from_scenario(target_scenario)
            world_state = world_service.get_world_state()
            self._latest_frame, self._latest_image = self._camera.capture(world_state)
            self._latest_png_bytes = encode_image_to_png(self._latest_image)
            return self._camera.get_status()

    def reset_camera(self) -> CameraFrame:
        """
        Reset camera gimbal orientation to initial configured pan/tilt.
        """
        with self._mutex:
            self._camera.reset()
            world_state = world_service.get_world_state()
            self._latest_frame, self._latest_image = self._camera.capture(world_state)
            self._latest_png_bytes = encode_image_to_png(self._latest_image)
            return self._latest_frame

    def set_pose(
        self,
        pan_deg: Optional[float] = None,
        tilt_deg: Optional[float] = None,
    ) -> CameraPose:
        """
        Update camera gimbal pan/tilt angles directly (development / testing control).
        """
        with self._mutex:
            pose = self._camera.set_pose(pan_deg=pan_deg, tilt_deg=tilt_deg)
            world_state = world_service.get_world_state()
            self._latest_frame, self._latest_image = self._camera.capture(world_state)
            self._latest_png_bytes = encode_image_to_png(self._latest_image)
            return pose

    def capture_frame(self) -> CameraFrame:
        """
        Capture a fresh frame from current World state and render synthetic image.
        """
        with self._mutex:
            world_state = world_service.get_world_state()
            self._latest_frame, self._latest_image = self._camera.capture(world_state)
            self._latest_png_bytes = encode_image_to_png(self._latest_image)
            return self._latest_frame

    def get_latest_frame(self) -> CameraFrame:
        """
        Retrieve the latest captured camera frame metadata.
        Synchronizes with world state if timestamps differ.
        """
        with self._mutex:
            world_state = world_service.get_world_state()
            if self._latest_frame is None or self._latest_frame.timestamp != world_state.timestamp:
                return self.capture_frame()
            return self._latest_frame

    def get_latest_image_png(self) -> bytes:
        """
        Retrieve PNG encoded byte stream of the latest synthetic camera frame.
        """
        with self._mutex:
            world_state = world_service.get_world_state()
            if self._latest_png_bytes is None or (self._latest_frame and self._latest_frame.timestamp != world_state.timestamp):
                self.capture_frame()
            return self._latest_png_bytes

    def get_telemetry(self) -> dict:
        """
        Retrieve comprehensive telemetry for real-time tracking display.
        """
        with self._mutex:
            frame = self.get_latest_frame()
            intrinsics = self._camera.get_intrinsics()
            world_status = world_service.get_status()
            return {
                "timestamp": frame.timestamp,
                "visible": frame.visible,
                "visibility_reason": frame.visibility.reason,
                "camera_pose": {
                    "position": frame.camera_position.model_dump(),
                    "pan_deg": frame.camera_orientation["pan_deg"],
                    "tilt_deg": frame.camera_orientation["tilt_deg"],
                },
                "beacon_world_position": frame.beacon_world_position.model_dump(),
                "beacon_camera_coordinates": frame.beacon_camera_coordinates.model_dump(),
                "projection": frame.projection.model_dump(),
                "angles": frame.angles.model_dump(),
                "visibility": frame.visibility.model_dump(),
                "spot": {
                    "radius": frame.spot_radius,
                    "intensity": frame.spot_intensity,
                },
                "intrinsics": intrinsics.model_dump(),
                "world_range": world_status.relative_geometry.range if world_status.relative_geometry else None,
            }

    def get_status(self) -> CameraStatus:
        """
        Retrieve camera initialization status, optical parameters, and pose.
        """
        with self._mutex:
            return self._camera.get_status()


# Singleton service instance
camera_service = CameraService()
