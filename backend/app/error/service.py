"""
Boresight Alignment & Error Calculation Service Layer.
Team PHARO — SIH26169

Thread-safe singleton service managing optical boresight error transformation,
alignment lock verification, real-time telemetry, and multi-layer HUD overlays.
"""

from __future__ import annotations
import io
import logging
import math
import threading
import time
from typing import Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw

from ..scenario.models import ScenarioConfig
from ..scenario.service import scenario_service
from ..camera.service import camera_service
from ..disturbance.service import disturbance_service
from ..tracking.service import tracking_service
from ..tracking.models import TrackingResult, TrackingStatus
from .models import (
    AlignmentConfig,
    AlignmentError,
    ErrorStatus,
    ErrorSource,
    ErrorStatusInfo,
    ErrorTelemetry,
)
from .calculator import ErrorCalculator

logger = logging.getLogger("fsoc.error.service")


class AlignmentService:
    """
    Singleton service managing boresight pointing error calculation and lock monitoring.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AlignmentService, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self._mutex = threading.RLock()
        self._config = AlignmentConfig()
        self._prev_error: Optional[Tuple[float, float, float]] = None  # (ex, ey, timestamp)
        self._total_calculations: int = 0
        self._aligned_frames_count: int = 0
        self._latest_result: Optional[AlignmentError] = None
        self._latest_overlay_png: Optional[bytes] = None

        active_scenario = scenario_service.get_active_scenario()
        self.initialize_from_scenario(active_scenario)

    def initialize_from_scenario(self, scenario: Optional[ScenarioConfig] = None) -> ErrorStatusInfo:
        """
        Initialize or reconfigure error calculation state.
        """
        with self._mutex:
            self._prev_error = None
            self._total_calculations = 0
            self._aligned_frames_count = 0
            self._latest_result = AlignmentError(
                timestamp=0.0,
                valid=False,
                status=ErrorStatus.INVALID,
                source=ErrorSource.NONE,
                center_x=320.0,
                center_y=240.0,
                pixel_tolerance=self._config.pixel_tolerance,
                angular_tolerance_deg=self._config.angular_tolerance_deg,
                message="Alignment engine initialized and awaiting tracking data",
            )
            self._latest_overlay_png = None
            return self.get_status()

    def reset(self) -> AlignmentError:
        """
        Reset error calculation state and history to INVALID uninitialized.
        """
        with self._mutex:
            self._prev_error = None
            self._total_calculations = 0
            self._aligned_frames_count = 0
            result = AlignmentError(
                timestamp=0.0,
                valid=False,
                status=ErrorStatus.INVALID,
                source=ErrorSource.NONE,
                center_x=320.0,
                center_y=240.0,
                pixel_tolerance=self._config.pixel_tolerance,
                angular_tolerance_deg=self._config.angular_tolerance_deg,
                message="Alignment engine reset to uninitialized state",
            )
            self._latest_result = result
            self._latest_overlay_png = None
            return result

    def set_config(self, config: AlignmentConfig) -> ErrorStatusInfo:
        """
        Dynamically update alignment tolerances and evaluation parameters.
        """
        with self._mutex:
            self._config = config.model_copy(deep=True)
            return self.get_status()

    def process_tracking(
        self,
        tracking: Optional[TrackingResult] = None,
    ) -> AlignmentError:
        """
        Compute boresight alignment error from the latest or provided TrackingResult.

        CRITICAL: Operates purely on tracking/prediction focal plane estimates.
        Never accesses ground truth.
        """
        with self._mutex:
            if tracking is None:
                tracking = tracking_service.get_latest_result()

            # Retrieve active camera geometry
            cam_frame = camera_service.get_latest_frame()
            intrinsics = camera_service._camera.get_intrinsics() if hasattr(camera_service, "_camera") else None

            width = cam_frame.width if cam_frame else 640
            height = cam_frame.height if cam_frame else 480
            hfov_deg = intrinsics.hfov_deg if intrinsics else 30.0
            vfov_deg = intrinsics.vfov_deg if intrinsics else 22.5
            timestamp = tracking.timestamp if tracking else 0.0

            # Select target position and source based on tracking lifecycle state
            target_x: Optional[float] = None
            target_y: Optional[float] = None
            source = ErrorSource.NONE
            tracking_conf = tracking.confidence if tracking else 0.0

            if tracking is not None:
                if tracking.status == TrackingStatus.TRACKING and tracking.position_x is not None and tracking.position_y is not None:
                    target_x = tracking.position_x
                    target_y = tracking.position_y
                    source = ErrorSource.FILTERED
                elif (
                    tracking.status == TrackingStatus.PREDICTING
                    and self._config.use_prediction_when_tracking_missing
                    and tracking.prediction_valid
                    and tracking.predicted_x is not None
                    and tracking.predicted_y is not None
                ):
                    target_x = tracking.predicted_x
                    target_y = tracking.predicted_y
                    source = ErrorSource.PREDICTED

            error_result = ErrorCalculator.compute_error(
                target_x=target_x,
                target_y=target_y,
                source=source,
                width=width,
                height=height,
                hfov_deg=hfov_deg,
                vfov_deg=vfov_deg,
                config=self._config,
                timestamp=timestamp,
                tracking_confidence=tracking_conf,
                prev_error=self._prev_error,
            )

            self._total_calculations += 1
            if error_result.aligned:
                self._aligned_frames_count += 1

            if error_result.valid and error_result.pixel_error_x is not None and error_result.pixel_error_y is not None:
                self._prev_error = (error_result.pixel_error_x, error_result.pixel_error_y, timestamp)

            self._latest_result = error_result
            self._latest_overlay_png = self._render_overlay_image(error_result, tracking)
            return error_result

    def get_latest_result(self) -> AlignmentError:
        """
        Retrieve latest computed AlignmentError.
        """
        with self._mutex:
            if self._latest_result is None:
                return self.process_tracking()
            return self._latest_result

    def get_status(self) -> ErrorStatusInfo:
        """
        Retrieve error module status, active configuration, and alignment metrics.
        """
        with self._mutex:
            res = self._latest_result
            return ErrorStatusInfo(
                initialized=res.valid if res else False,
                status=res.status if res else ErrorStatus.INVALID,
                config=self._config,
                total_calculations=self._total_calculations,
                aligned_frames_count=self._aligned_frames_count,
                current_pixel_error_magnitude=res.pixel_error_magnitude if res else None,
                current_angular_error_magnitude_deg=res.angular_error_magnitude_deg if res else None,
                current_aligned=res.aligned if res else False,
                current_timestamp=res.timestamp if res else 0.0,
            )

    def get_telemetry(self) -> ErrorTelemetry:
        """
        Retrieve real-time telemetry packet for HUD displays and diagnostics.
        """
        with self._mutex:
            res = self.get_latest_result()

            if res.status == ErrorStatus.ALIGNED:
                status_text = f"ALIGNED (LOCK ACQUIRED) | Angular Error: {res.angular_error_magnitude_deg:.2f}° <= {res.angular_tolerance_deg:.2f}°"
            elif res.status == ErrorStatus.VALID:
                status_text = f"TRACKING ERROR | ΔX: {res.pixel_error_x:+.1f}px ΔY: {res.pixel_error_y:+.1f}px ({res.angular_error_magnitude_deg:.2f}°)"
            else:
                status_text = "ALIGNMENT INVALID (Awaiting Reliable Target Track)"

            return ErrorTelemetry(
                timestamp=res.timestamp,
                valid=res.valid,
                status=res.status.value,
                source=res.source.value,
                target_x=res.target_x,
                target_y=res.target_y,
                center_x=res.center_x,
                center_y=res.center_y,
                pixel_error_x=res.pixel_error_x,
                pixel_error_y=res.pixel_error_y,
                pixel_error_magnitude=res.pixel_error_magnitude,
                angular_error_x_deg=res.angular_error_x_deg,
                angular_error_y_deg=res.angular_error_y_deg,
                angular_error_magnitude_deg=res.angular_error_magnitude_deg,
                error_direction_deg=res.error_direction_deg,
                error_rate_x=res.error_rate_x,
                error_rate_y=res.error_rate_y,
                aligned=res.aligned,
                radially_aligned=res.radially_aligned,
                tracking_confidence=res.tracking_confidence,
                pixel_tolerance=res.pixel_tolerance,
                angular_tolerance_deg=res.angular_tolerance_deg,
                status_text=status_text,
            )

    def get_overlay_image_png(self) -> bytes:
        """
        Retrieve PNG byte stream of sensor observation with Alignment HUD overlay.
        """
        with self._mutex:
            if self._latest_overlay_png is None:
                self.process_tracking()
            return self._latest_overlay_png or b""

    def _render_overlay_image(
        self,
        error: AlignmentError,
        tracking: Optional[TrackingResult],
    ) -> bytes:
        """
        Render multi-layer alignment HUD overlay on disturbed camera sensor observation.
        """
        sensor_image = disturbance_service._latest_image
        w = error.image_width
        h = error.image_height

        if sensor_image is None or sensor_image.shape != (h, w):
            img_pil = Image.new("RGB", (w, h), (5, 10, 20))
        else:
            if sensor_image.ndim == 2:
                img_pil = Image.fromarray(sensor_image, mode="L").convert("RGB")
            else:
                img_pil = Image.fromarray(sensor_image).convert("RGB")

        draw = ImageDraw.Draw(img_pil)

        # Palette
        cyan = (0, 220, 255)
        lime = (50, 255, 100)
        amber = (255, 180, 20)
        red = (255, 60, 60)
        dim_gray = (70, 90, 110)
        yellow = (255, 230, 80)
        magenta = (230, 80, 255)

        cx, cy = error.center_x, error.center_y

        # 1. Optical Axis Boresight Reticle at (cx, cy)
        draw.line([(cx - 16, cy), (cx + 16, cy)], fill=cyan, width=1)
        draw.line([(cx, cy - 16), (cx, cy + 16)], fill=cyan, width=1)

        # 2. Alignment Lock Tolerance Ring / Reticle
        # Convert angular tolerance to approximate pixels for visual circle
        fx = error.image_width / (2.0 * math.tan(math.radians(error.horizontal_fov_deg) / 2.0))
        tol_px = fx * math.tan(math.radians(error.angular_tolerance_deg)) if error.angular_tolerance_deg > 0 else error.pixel_tolerance
        tol_r = max(4.0, tol_px)

        tol_color = lime if error.aligned else dim_gray
        draw.ellipse([(cx - tol_r, cy - tol_r), (cx + tol_r, cy + tol_r)], outline=tol_color, width=1)

        # 3. Target Marker & Error Vector
        if error.valid and error.target_x is not None and error.target_y is not None:
            tx, ty = error.target_x, error.target_y

            # Error vector line from center to target
            vector_color = lime if error.aligned else amber
            draw.line([(cx, cy), (tx, ty)], fill=vector_color, width=2)

            # Target position marker
            r_tgt = 12
            if error.source == ErrorSource.FILTERED:
                draw.ellipse([(tx - r_tgt, ty - r_tgt), (tx + r_tgt, ty + r_tgt)], outline=lime, width=2)
            else:
                draw.rectangle([(tx - r_tgt, ty - r_tgt), (tx + r_tgt, ty + r_tgt)], outline=amber, width=2)

            # Center target crosshair
            draw.line([(tx - 6, ty), (tx + 6, ty)], fill=yellow, width=1)
            draw.line([(tx, ty - 6), (tx, ty + 6)], fill=yellow, width=1)

        # 4. Top Status Banner
        if error.status == ErrorStatus.ALIGNED:
            banner_bg = (0, 45, 25)
            banner_fg = lime
            banner_txt = f"ALIGNED (BORESIGHT LOCKED) | ΔX={error.pixel_error_x:+.1f}px ΔY={error.pixel_error_y:+.1f}px | Err={error.angular_error_magnitude_deg:.2f}° <= {error.angular_tolerance_deg:.2f}°"
        elif error.status == ErrorStatus.VALID:
            banner_bg = (40, 30, 0)
            banner_fg = amber
            src_str = "FILTERED" if error.source == ErrorSource.FILTERED else "PREDICTED"
            banner_txt = f"ALIGNMENT ERROR ({src_str}) | ΔX={error.pixel_error_x:+.1f}px ΔY={error.pixel_error_y:+.1f}px | Mag={error.pixel_error_magnitude:.1f}px ({error.angular_error_magnitude_deg:.2f}°)"
        else:
            banner_bg = (45, 10, 10)
            banner_fg = red
            banner_txt = "ALIGNMENT INVALID | No Target Track Available"

        draw.rectangle([(0, 0), (w, 22)], fill=banner_bg)
        draw.text((8, 5), banner_txt, fill=banner_fg)

        # 5. Bottom Diagnostics Footer
        src_label = error.source.value
        rate_str = f"Rate=({error.error_rate_x or 0:+.1f}, {error.error_rate_y or 0:+.1f})px/s" if error.valid else "Rate=N/A"
        footer_txt = f"Boresight: ({cx:.0f}, {cy:.0f}) | Src: {src_label} | {rate_str} | Tol: ±{error.angular_tolerance_deg}° | t={error.timestamp:.2f}s"
        draw.rectangle([(0, h - 20), (w, h)], fill=(10, 15, 25))
        draw.text((8, h - 16), footer_txt, fill=(0, 200, 230))

        buf = io.BytesIO()
        img_pil.save(buf, format="PNG", optimize=True)
        return buf.getvalue()


# Singleton service instance
alignment_service = AlignmentService()
