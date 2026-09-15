"""
Disturbance Simulation Service Layer.
Team PHARO — SIH26169

Thread-safe singleton service orchestrating environmental disturbances,
frame processing, telemetry generation, and REST API access.
"""

from __future__ import annotations
import threading
from typing import Optional, Tuple
import numpy as np

from ..scenario.models import ScenarioConfig, DisturbanceConfig
from ..scenario.service import scenario_service
from ..camera.service import camera_service
from ..camera.renderer import encode_image_to_png
from ..world.service import world_service
from .models import (
    DisturbanceFrame,
    DisturbanceStatus,
    DisturbanceTelemetry,
    DisturbanceMetadata,
)
from .processor import DisturbanceProcessor


class DisturbanceService:
    """
    Singleton service managing disturbance simulation state, frame rendering, and API interface.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DisturbanceService, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self._mutex = threading.RLock()
        self._processor = DisturbanceProcessor()
        self._scenario_name = "Default Scenario"
        self._config: DisturbanceConfig = DisturbanceConfig()
        self._random_seed: int = 42
        self._fps: float = 30.0
        self._initialized: bool = False
        self._latest_frame: Optional[DisturbanceFrame] = None
        self._latest_image: Optional[np.ndarray] = None
        self._latest_png_bytes: Optional[bytes] = None

        active_scenario = scenario_service.get_active_scenario()
        self.initialize_from_scenario(active_scenario)

    def initialize_from_scenario(self, scenario: Optional[ScenarioConfig] = None) -> DisturbanceStatus:
        """
        Initialize or re-configure disturbance parameters from a ScenarioConfig.
        """
        with self._mutex:
            target_scenario = scenario or scenario_service.get_active_scenario()
            self._scenario_name = target_scenario.scenario_name
            self._config = target_scenario.disturbances.model_copy(deep=True)
            self._random_seed = target_scenario.simulation.random_seed
            self._fps = target_scenario.simulation.fps
            self._processor.reset()
            self._initialized = True

            # Process initial frame at t=0
            self.process_frame()
            return self.get_status()

    def reset(self) -> DisturbanceFrame:
        """
        Reset disturbance temporal tracker and stochastic sequence to t=0.
        """
        with self._mutex:
            self._processor.reset()
            return self.process_frame()

    def set_config(self, config: DisturbanceConfig) -> DisturbanceStatus:
        """
        Update active disturbance parameters dynamically in real time.
        """
        with self._mutex:
            self._config = config.model_copy(deep=True)
            self.process_frame()
            return self.get_status()

    def process_frame(self) -> DisturbanceFrame:
        """
        Retrieve latest clean camera frame, apply active disturbances, and encode output PNG.
        """
        with self._mutex:
            clean_cam_frame = camera_service.get_latest_frame()
            world_status = world_service.get_status()
            timestamp = clean_cam_frame.timestamp
            fps = world_status.fps if world_status else self._fps

            # Capture/render clean sensor image from camera service
            clean_image = camera_service._camera._last_image
            if clean_image is None or clean_image.shape != (clean_cam_frame.height, clean_cam_frame.width):
                # Ensure clean image is rendered
                _, clean_image = camera_service._camera.capture(world_service.get_world_state())

            disturbed_img, meta = self._processor.process(
                clean_image=clean_image,
                config=self._config,
                timestamp=timestamp,
                fps=fps,
                seed=self._random_seed,
                camera_frame=clean_cam_frame,
            )

            is_altered = meta.applied_effects_count > 0

            dist_frame = DisturbanceFrame(
                timestamp=timestamp,
                frame_index=meta.frame_index,
                width=clean_cam_frame.width,
                height=clean_cam_frame.height,
                metadata=meta,
                is_disturbed=is_altered,
            )

            self._latest_frame = dist_frame
            self._latest_image = disturbed_img
            self._latest_png_bytes = encode_image_to_png(disturbed_img)

            return dist_frame

    def get_latest_frame(self) -> DisturbanceFrame:
        """
        Retrieve latest disturbed frame metadata. Synchronizes with current camera timestamp if needed.
        """
        with self._mutex:
            cam_frame = camera_service.get_latest_frame()
            if self._latest_frame is None or self._latest_frame.timestamp != cam_frame.timestamp:
                return self.process_frame()
            return self._latest_frame

    def get_latest_image_png(self) -> bytes:
        """
        Retrieve PNG encoded byte stream of the latest disturbed synthetic optical image.
        """
        with self._mutex:
            cam_frame = camera_service.get_latest_frame()
            if self._latest_png_bytes is None or (self._latest_frame and self._latest_frame.timestamp != cam_frame.timestamp):
                self.process_frame()
            return self._latest_png_bytes

    def get_status(self) -> DisturbanceStatus:
        """
        Retrieve lifecycle status, active configuration, and dropout status.
        """
        with self._mutex:
            timestamp = self._latest_frame.timestamp if self._latest_frame else 0.0
            is_dropout_active = self._processor._dropout_tracker._active
            return DisturbanceStatus(
                initialized=self._initialized,
                scenario_name=self._scenario_name,
                severity=self._config.severity,
                config=self._config,
                dropout_active=is_dropout_active,
                current_timestamp=timestamp,
            )

    def get_telemetry(self) -> DisturbanceTelemetry:
        """
        Retrieve real-time disturbance diagnostics for live UI and telemetry charts.
        """
        with self._mutex:
            frame = self.get_latest_frame()
            meta = frame.metadata
            clean_cam_frame = camera_service.get_latest_frame()
            return DisturbanceTelemetry(
                timestamp=frame.timestamp,
                frame_index=frame.frame_index,
                severity=meta.severity,
                noise_sigma=meta.noise.sigma,
                blur_strength=meta.blur.strength,
                vibration_offset_x=meta.vibration.offset_x,
                vibration_offset_y=meta.vibration.offset_y,
                dropout_active=meta.dropout.active,
                dropout_remaining_duration=meta.dropout.remaining_duration,
                beacon_visible_in_clean=clean_cam_frame.visible,
                beacon_occluded_by_dropout=meta.dropout.applied,
            )


# Singleton service instance
disturbance_service = DisturbanceService()
