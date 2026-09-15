"""
Beacon Detection Service Layer.
Team PHARO — SIH26169

Thread-safe singleton service managing detector instances, runtime configuration,
frame processing, historical statistics, HUD overlay generation, and REST API access.
"""

from __future__ import annotations
import io
import threading
from typing import Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw

from ..scenario.models import ScenarioConfig
from ..scenario.service import scenario_service
from ..camera.service import camera_service
from ..disturbance.service import disturbance_service
from .models import (
    DetectionConfig,
    DetectionResult,
    DetectionStatus,
    DetectionTelemetry,
    BoundingBox,
)
from .base import BaseDetector
from .opencv_detector import OpenCVBeaconDetector
from .mock_detector import MockBeaconDetector


class DetectionService:
    """
    Singleton service managing beacon detector lifecycle, processing, and visualization.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DetectionService, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self._mutex = threading.RLock()
        self._config = DetectionConfig()
        self._detector: BaseDetector = OpenCVBeaconDetector(self._config)
        self._initialized: bool = False

        self._total_frames_processed: int = 0
        self._successful_detections: int = 0
        self._latest_result: Optional[DetectionResult] = None
        self._latest_overlay_png: Optional[bytes] = None
        self._last_processed_timestamp: float = -1.0

        active_scenario = scenario_service.get_active_scenario()
        self.initialize_from_scenario(active_scenario)

    def _instantiate_detector(self, config: DetectionConfig) -> BaseDetector:
        """
        Factory to instantiate selected detector backend.
        """
        if config.method == "mock":
            return MockBeaconDetector(config=config)
        elif config.method == "opencv":
            return OpenCVBeaconDetector(config=config)
        elif config.method == "yolo":
            # Future YOLO placeholder fallback to OpenCV with warning
            return OpenCVBeaconDetector(config=config)
        return OpenCVBeaconDetector(config=config)

    def initialize_from_scenario(self, scenario: Optional[ScenarioConfig] = None) -> DetectionStatus:
        """
        Initialize detection service state from active scenario.
        """
        with self._mutex:
            self._detector = self._instantiate_detector(self._config)
            self._total_frames_processed = 0
            self._successful_detections = 0
            self._initialized = True
            self._last_processed_timestamp = -1.0

            # Process initial frame at t=0
            self.process_frame()
            return self.get_status()

    def reset(self) -> DetectionResult:
        """
        Reset detection counters and re-process current frame.
        """
        with self._mutex:
            self._total_frames_processed = 0
            self._successful_detections = 0
            self._last_processed_timestamp = -1.0
            return self.process_frame()

    def set_config(self, config: DetectionConfig) -> DetectionStatus:
        """
        Dynamically update detection configuration and switch detector backend if needed.
        """
        with self._mutex:
            self._config = config.model_copy(deep=True)
            self._detector = self._instantiate_detector(self._config)
            self.process_frame()
            return self.get_status()

    def process_frame(self, image: Optional[np.ndarray] = None) -> DetectionResult:
        """
        Execute detection on the latest disturbed camera frame or provided image array.
        
        CRITICAL: Operates strictly on image pixels without ground-truth assistance.
        """
        with self._mutex:
            dist_frame = disturbance_service.get_latest_frame()
            sensor_image = image if image is not None else disturbance_service._latest_image

            if sensor_image is None or sensor_image.shape != (dist_frame.height, dist_frame.width):
                dist_frame = disturbance_service.process_frame()
                sensor_image = disturbance_service._latest_image

            timestamp = dist_frame.timestamp if dist_frame else 0.0

            # Execute detector on image
            result = self._detector.detect(
                image=sensor_image,
                timestamp=timestamp,
                config=self._config,
            )

            # Update historical counters
            self._total_frames_processed += 1
            if result.detected:
                self._successful_detections += 1

            self._latest_result = result
            self._last_processed_timestamp = timestamp
            self._latest_overlay_png = self._render_overlay_image(sensor_image, result)

            return result

    def get_latest_result(self) -> DetectionResult:
        """
        Retrieve latest detection result packet, re-processing if timestamp advanced.
        """
        with self._mutex:
            cam_frame = camera_service.get_latest_frame()
            if self._latest_result is None or self._latest_result.timestamp != cam_frame.timestamp:
                return self.process_frame()
            return self._latest_result

    def get_status(self) -> DetectionStatus:
        """
        Retrieve detector lifecycle status, configuration, and cumulative success percentage.
        """
        with self._mutex:
            rate = (
                (self._successful_detections / self._total_frames_processed * 100.0)
                if self._total_frames_processed > 0
                else 0.0
            )
            latest_det = self._latest_result.detected if self._latest_result else False
            ts = self._latest_result.timestamp if self._latest_result else 0.0

            return DetectionStatus(
                initialized=self._initialized,
                method=self._config.method,
                config=self._config,
                total_frames_processed=self._total_frames_processed,
                successful_detections=self._successful_detections,
                detection_rate_pct=round(rate, 2),
                latest_detected=latest_det,
                current_timestamp=ts,
            )

    def get_telemetry(self) -> DetectionTelemetry:
        """
        Retrieve real-time telemetry diagnostics.
        """
        with self._mutex:
            res = self.get_latest_result()
            bbox_w = res.bbox.width if res.bbox else None
            bbox_h = res.bbox.height if res.bbox else None

            if res.detected:
                status_text = f"BEACON DETECTED ({res.center_x:.1f}, {res.center_y:.1f})"
            else:
                status_text = "BEACON NOT DETECTED"

            return DetectionTelemetry(
                timestamp=res.timestamp,
                detected=res.detected,
                center_x=res.center_x,
                center_y=res.center_y,
                confidence=res.confidence,
                candidate_count=res.candidate_count,
                processing_time_ms=res.processing_time_ms,
                method=res.method,
                bbox_width=bbox_w,
                bbox_height=bbox_h,
                status_text=status_text,
            )

    def get_overlay_image_png(self) -> bytes:
        """
        Retrieve PNG byte stream of sensor observation with detection bounding box and centroid crosshair.
        Does NOT draw ground truth.
        """
        with self._mutex:
            cam_frame = camera_service.get_latest_frame()
            if self._latest_overlay_png is None or (self._latest_result and self._latest_result.timestamp != cam_frame.timestamp):
                self.process_frame()
            return self._latest_overlay_png

    def _render_overlay_image(self, image: np.ndarray, result: DetectionResult) -> bytes:
        """
        Render detection HUD overlay on sensor frame using PIL ImageDraw.
        """
        if image is None:
            img_pil = Image.new("RGB", (640, 480), (0, 0, 0))
        else:
            if image.ndim == 2:
                img_pil = Image.fromarray(image, mode="L").convert("RGB")
            else:
                img_pil = Image.fromarray(image).convert("RGB")

        draw = ImageDraw.Draw(img_pil)
        w, h = img_pil.size

        cyan = (0, 240, 255)
        green = (50, 255, 120)
        red = (255, 60, 60)
        dim_cyan = (0, 150, 180)

        # Draw optical center crosshair
        cx, cy = w / 2.0, h / 2.0
        draw.line([(cx - 8, cy), (cx + 8, cy)], fill=(60, 80, 100), width=1)
        draw.line([(cx, cy - 8), (cx, cy + 8)], fill=(60, 80, 100), width=1)

        if result.detected and result.center_x is not None and result.center_y is not None:
            u_px = float(result.center_x)
            v_px = float(result.center_y)

            # 1. Bounding Box
            if result.bbox:
                bx0 = result.bbox.x
                by0 = result.bbox.y
                bx1 = result.bbox.x + result.bbox.width - 1
                by1 = result.bbox.y + result.bbox.height - 1
                draw.rectangle([(bx0, by0), (bx1, by1)], outline=cyan, width=1)

            # 2. Target Reticle
            reticle_r = 12
            draw.ellipse(
                [(u_px - reticle_r, v_px - reticle_r), (u_px + reticle_r, v_px + reticle_r)],
                outline=green,
                width=2,
            )
            # Center crosshairs
            draw.line([(u_px - 16, v_px), (u_px - 4, v_px)], fill=cyan, width=1)
            draw.line([(u_px + 4, v_px), (u_px + 16, v_px)], fill=cyan, width=1)
            draw.line([(u_px, v_px - 16), (u_px, v_px - 4)], fill=cyan, width=1)
            draw.line([(u_px, v_px + 4), (u_px, v_px + 16)], fill=cyan, width=1)

            # Top status banner
            banner_text = f"BEACON DETECTED | U={u_px:.1f} V={v_px:.1f} | Conf={result.confidence:.2f} | Candidates={result.candidate_count} | {result.method.upper()}"
            draw.rectangle([(0, 0), (w, 20)], fill=(0, 30, 20))
            draw.text((8, 4), banner_text, fill=green)
        else:
            # Not detected banner
            banner_text = f"BEACON NOT DETECTED | {result.message}"
            draw.rectangle([(0, 0), (w, 20)], fill=(40, 10, 10))
            draw.text((8, 4), banner_text, fill=red)

        # Bottom latency bar
        lat_text = f"Method: {result.method.upper()} | Latency: {result.processing_time_ms:.1f}ms | t={result.timestamp:.2f}s"
        draw.rectangle([(0, h - 18), (w, h)], fill=(10, 15, 25))
        draw.text((8, h - 15), lat_text, fill=dim_cyan)

        buf = io.BytesIO()
        img_pil.save(buf, format="PNG", optimize=True)
        return buf.getvalue()


# Singleton service instance
detection_service = DetectionService()
