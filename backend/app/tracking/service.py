"""
Beacon Tracking & Motion Prediction Service Layer.
Team PHARO — SIH26169

Thread-safe singleton service managing Kalman tracker lifecycle, multi-rate updates,
dropout coasting, tracking confidence computation, telemetry, and HUD overlays.
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
from ..detection.service import detection_service
from ..detection.models import DetectionResult
from .models import (
    TrackingConfig,
    TrackingResult,
    TrackingStatus,
    TrackingStatusInfo,
    TrackingTelemetry,
)
from .kalman_tracker import KalmanTracker

logger = logging.getLogger("fsoc.tracking.service")


class TrackingService:
    """
    Singleton service managing 2D beacon tracking and motion prediction.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TrackingService, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self._mutex = threading.RLock()
        self._config = TrackingConfig()
        self._tracker = KalmanTracker(self._config)

        self._status: TrackingStatus = TrackingStatus.UNINITIALIZED
        self._consecutive_hits: int = 0
        self._consecutive_misses: int = 0
        self._total_updates: int = 0
        self._tracking_hits: int = 0
        self._tracking_misses: int = 0
        self._last_timestamp: float = -1.0
        self._latest_measured_x: Optional[float] = None
        self._latest_measured_y: Optional[float] = None
        self._latest_result: Optional[TrackingResult] = None
        self._latest_overlay_png: Optional[bytes] = None

        active_scenario = scenario_service.get_active_scenario()
        self.initialize_from_scenario(active_scenario)

    def initialize_from_scenario(self, scenario: Optional[ScenarioConfig] = None) -> TrackingStatusInfo:
        """
        Initialize or reconfigure tracking service state.
        """
        with self._mutex:
            self._tracker.reset()
            self._tracker.config = self._config
            self._status = TrackingStatus.UNINITIALIZED
            self._consecutive_hits = 0
            self._consecutive_misses = 0
            self._total_updates = 0
            self._tracking_hits = 0
            self._tracking_misses = 0
            self._last_timestamp = -1.0
            self._latest_measured_x = None
            self._latest_measured_y = None
            self._latest_result = TrackingResult(
                timestamp=0.0,
                initialized=False,
                tracking=False,
                status=TrackingStatus.UNINITIALIZED,
                message="Tracker initialized and awaiting beacon detection",
            )
            self._latest_overlay_png = None
            return self.get_status()

    def reset(self) -> TrackingResult:
        """
        Reset all internal tracker state to UNINITIALIZED.
        """
        with self._mutex:
            self._tracker.reset()
            self._status = TrackingStatus.UNINITIALIZED
            self._consecutive_hits = 0
            self._consecutive_misses = 0
            self._total_updates = 0
            self._tracking_hits = 0
            self._tracking_misses = 0
            self._last_timestamp = -1.0
            self._latest_measured_x = None
            self._latest_measured_y = None
            result = TrackingResult(
                timestamp=0.0,
                initialized=False,
                tracking=False,
                status=TrackingStatus.UNINITIALIZED,
                message="Tracker reset to uninitialized state",
            )
            self._latest_result = result
            self._latest_overlay_png = None
            return result

    def set_config(self, config: TrackingConfig) -> TrackingStatusInfo:
        """
        Dynamically update tracker parameters in real time.
        """
        with self._mutex:
            self._config = config.model_copy(deep=True)
            self._tracker.config = self._config
            return self.get_status()

    def process_detection(
        self,
        detection: Optional[DetectionResult] = None,
        timestamp: Optional[float] = None,
    ) -> TrackingResult:
        """
        Execute one tracking predict & update step from a DetectionResult.

        CRITICAL: Operates solely on detection measurements and internal Kalman state.
        Never accesses ground truth.
        """
        start_time = time.perf_counter()

        with self._mutex:
            if detection is None:
                detection = detection_service.get_latest_result()

            frame_time = float(timestamp if timestamp is not None else (detection.timestamp if detection else 0.0))

            # Compute dt safely
            if self._last_timestamp < 0.0:
                dt = 1.0 / 30.0  # Nominal default timestep on first frame
            else:
                dt = frame_time - self._last_timestamp
                if dt <= 0.0 or dt > self._config.max_dt:
                    dt = 1.0 / 30.0  # Fallback to nominal if timestamp non-monotonic or huge jump
                else:
                    dt = max(self._config.min_dt, min(dt, self._config.max_dt))

            self._total_updates += 1
            is_measurement_valid = self._validate_measurement(detection)

            # Measurement data
            z_meas: Optional[np.ndarray] = None
            r_mat: Optional[np.ndarray] = None
            meas_conf = float(detection.confidence) if detection and detection.confidence is not None else 0.0

            if is_measurement_valid and detection is not None:
                cx = float(detection.center_x)  # type: ignore
                cy = float(detection.center_y)  # type: ignore
                self._latest_measured_x = cx
                self._latest_measured_y = cy
                z_meas = np.array([cx, cy], dtype=np.float64)

                # Adaptive measurement noise scaling
                if self._config.adaptive_measurement_noise:
                    base_r = float(self._config.measurement_noise)
                    scaled_r = base_r / max(0.1, meas_conf)
                    r_mat = np.diag([scaled_r, scaled_r]).astype(np.float64)
            else:
                self._latest_measured_x = None
                self._latest_measured_y = None

            # State Machine & Kalman Execution
            pos_x: Optional[float] = None
            pos_y: Optional[float] = None
            vel_x: Optional[float] = None
            vel_y: Optional[float] = None
            pred_x: Optional[float] = None
            pred_y: Optional[float] = None
            unc_x: Optional[float] = None
            unc_y: Optional[float] = None
            unc_vx: Optional[float] = None
            unc_vy: Optional[float] = None
            tracking_confidence: float = 0.0
            tracking_flag: bool = False
            prediction_valid_flag: bool = False
            message: str = ""

            if is_measurement_valid and z_meas is not None:
                # Valid Detection Frame
                self._tracking_hits += 1
                self._consecutive_hits += 1
                self._consecutive_misses = 0

                if not self._tracker.is_initialized() or self._status == TrackingStatus.LOST:
                    # First measurement or re-acquisition after track loss: initialize
                    self._tracker.initialize(
                        initial_position=z_meas,
                        initial_velocity=np.zeros(2, dtype=np.float64),
                        timestamp=frame_time,
                    )
                    self._status = TrackingStatus.TRACKING
                    message = "Tracker initialized from valid beacon detection"
                else:
                    # Normal tracking: Predict forward then Update
                    self._tracker.predict(dt)
                    self._tracker.update(z_meas, measurement_cov=r_mat)
                    self._status = TrackingStatus.TRACKING
                    message = f"Measurement update accepted (conf={meas_conf:.2f})"

                pos = self._tracker.get_position()
                vel = self._tracker.get_velocity()
                p_unc = self._tracker.get_position_uncertainty()
                v_unc = self._tracker.get_velocity_uncertainty()

                if pos is not None and vel is not None and p_unc is not None and v_unc is not None:
                    pos_x, pos_y = pos
                    vel_x, vel_y = vel
                    unc_x, unc_y = p_unc
                    unc_vx, unc_vy = v_unc

                    # Lead prediction
                    lead_t = self._config.prediction_lead_time if self._config.prediction_lead_time > 0.0 else dt
                    lead_state = self._tracker.predict_lead(lead_t)
                    pred_x = float(lead_state[0, 0])
                    pred_y = float(lead_state[1, 0])

                    # Calculate tracking confidence
                    tracking_confidence = self._compute_tracking_confidence(
                        detector_confidence=meas_conf,
                        is_hit=True,
                        consecutive_hits=self._consecutive_hits,
                        consecutive_misses=0,
                        pos_uncertainty=(unc_x, unc_y),
                    )
                    tracking_flag = True
                    prediction_valid_flag = True

            else:
                # Missed / Rejected Detection Frame
                self._tracking_misses += 1
                self._consecutive_misses += 1
                self._consecutive_hits = 0

                if not self._tracker.is_initialized():
                    self._status = TrackingStatus.UNINITIALIZED
                    message = "Awaiting initial beacon detection"
                    tracking_flag = False
                    prediction_valid_flag = False
                    tracking_confidence = 0.0
                elif self._status == TrackingStatus.LOST:
                    # Already lost, remain lost
                    self._status = TrackingStatus.LOST
                    message = f"Track lost — awaiting re-acquisition ({self._consecutive_misses} missed frames)"
                    tracking_flag = False
                    prediction_valid_flag = False
                    tracking_confidence = 0.0
                elif self._consecutive_misses <= self._config.max_missed_frames:
                    # Coasting in PREDICTING mode
                    self._tracker.predict(dt)
                    self._status = TrackingStatus.PREDICTING
                    message = f"Measurement dropout — coasting prediction (miss {self._consecutive_misses}/{self._config.max_missed_frames})"

                    pos = self._tracker.get_position()
                    vel = self._tracker.get_velocity()
                    p_unc = self._tracker.get_position_uncertainty()
                    v_unc = self._tracker.get_velocity_uncertainty()

                    if pos is not None and vel is not None and p_unc is not None and v_unc is not None:
                        pos_x, pos_y = pos
                        vel_x, vel_y = vel
                        unc_x, unc_y = p_unc
                        unc_vx, unc_vy = v_unc

                        lead_t = self._config.prediction_lead_time if self._config.prediction_lead_time > 0.0 else dt
                        lead_state = self._tracker.predict_lead(lead_t)
                        pred_x = float(lead_state[0, 0])
                        pred_y = float(lead_state[1, 0])

                        tracking_confidence = self._compute_tracking_confidence(
                            detector_confidence=0.0,
                            is_hit=False,
                            consecutive_hits=0,
                            consecutive_misses=self._consecutive_misses,
                            pos_uncertainty=(unc_x, unc_y),
                        )
                        tracking_flag = True
                        prediction_valid_flag = True
                else:
                    # Exceeded max missed frames -> LOST
                    self._status = TrackingStatus.LOST
                    message = f"Track lost — exceeded {self._config.max_missed_frames} consecutive missed frames"
                    tracking_flag = False
                    prediction_valid_flag = False
                    tracking_confidence = 0.0

            self._last_timestamp = frame_time
            proc_time_ms = (time.perf_counter() - start_time) * 1000.0

            result = TrackingResult(
                timestamp=frame_time,
                initialized=self._tracker.is_initialized(),
                tracking=tracking_flag,
                status=self._status,
                position_x=pos_x,
                position_y=pos_y,
                velocity_x=vel_x,
                velocity_y=vel_y,
                predicted_x=pred_x,
                predicted_y=pred_y,
                confidence=round(tracking_confidence, 4),
                measurement_available=is_measurement_valid,
                measurement_confidence=meas_conf,
                consecutive_hits=self._consecutive_hits,
                consecutive_misses=self._consecutive_misses,
                state_uncertainty_x=unc_x,
                state_uncertainty_y=unc_y,
                velocity_uncertainty_x=unc_vx,
                velocity_uncertainty_y=unc_vy,
                prediction_valid=prediction_valid_flag,
                processing_time_ms=round(proc_time_ms, 3),
                message=message,
            )

            self._latest_result = result
            self._latest_overlay_png = self._render_overlay_image(detection, result)
            return result

    def _validate_measurement(self, detection: Optional[DetectionResult]) -> bool:
        """
        Validate incoming DetectionResult against corruption, NaNs, and threshold constraints.
        """
        if detection is None or not detection.detected:
            return False
        if detection.center_x is None or detection.center_y is None:
            return False
        if not (math.isfinite(detection.center_x) and math.isfinite(detection.center_y)):
            return False
        if detection.confidence < self._config.min_detection_confidence:
            return False
        if not (0.0 <= detection.confidence <= 1.0):
            return False
        return True

    def _compute_tracking_confidence(
        self,
        detector_confidence: float,
        is_hit: bool,
        consecutive_hits: int,
        consecutive_misses: int,
        pos_uncertainty: Tuple[float, float],
    ) -> float:
        """
        Compute deterministic tracking confidence score [0.0, 1.0].
        Considers measurement confidence, hit streak saturation, dropout decay, and covariance trace.
        """
        sigma_x, sigma_y = pos_uncertainty
        trace_pos = sigma_x * sigma_x + sigma_y * sigma_y
        
        # Uncertainty attenuation: baseline sigma_0_sq = 400.0 (20 px std dev)
        sigma_0_sq = 400.0
        unc_factor = math.exp(-min(5.0, trace_pos / (2.0 * sigma_0_sq)))

        if is_hit:
            # Hit streak ramp: weight detector confidence 70%, streak 30%
            streak_factor = 1.0 - math.exp(-consecutive_hits / 1.5)
            base_conf = 0.7 * detector_confidence + 0.3 * streak_factor
            conf = base_conf * (0.5 + 0.5 * unc_factor)
        else:
            # Coasting dropout decay
            max_miss = max(1, self._config.max_missed_frames)
            decay = max(0.0, 1.0 - (consecutive_misses / (max_miss + 1.0)))
            conf = 0.8 * decay * unc_factor

        return float(np.clip(conf, 0.0, 1.0))

    def get_latest_result(self) -> TrackingResult:
        """
        Retrieve latest tracking result packet.
        """
        with self._mutex:
            if self._latest_result is None:
                return self.process_detection()
            return self._latest_result

    def get_status(self) -> TrackingStatusInfo:
        """
        Retrieve lifecycle status, active configuration, and performance statistics.
        """
        with self._mutex:
            res = self._latest_result
            return TrackingStatusInfo(
                initialized=self._tracker.is_initialized(),
                status=self._status,
                config=self._config,
                total_updates=self._total_updates,
                tracking_hits=self._tracking_hits,
                tracking_misses=self._tracking_misses,
                current_confidence=res.confidence if res else 0.0,
                current_timestamp=res.timestamp if res else 0.0,
                latest_position_x=res.position_x if res else None,
                latest_position_y=res.position_y if res else None,
                latest_velocity_x=res.velocity_x if res else None,
                latest_velocity_y=res.velocity_y if res else None,
            )

    def get_telemetry(self) -> TrackingTelemetry:
        """
        Retrieve real-time tracking telemetry packet for HUD displays.
        """
        with self._mutex:
            res = self.get_latest_result()
            speed = None
            if res.velocity_x is not None and res.velocity_y is not None:
                speed = float(np.hypot(res.velocity_x, res.velocity_y))

            meas_x = self._latest_measured_x
            meas_y = self._latest_measured_y

            if res.status == TrackingStatus.TRACKING:
                status_text = f"TRACKING (Hits: {res.consecutive_hits} | Conf: {res.confidence*100:.0f}%)"
            elif res.status == TrackingStatus.PREDICTING:
                status_text = f"PREDICTING / COASTING (Miss: {res.consecutive_misses}/{self._config.max_missed_frames})"
            elif res.status == TrackingStatus.LOST:
                status_text = "TRACK LOST (Awaiting Re-acquisition)"
            else:
                status_text = "TRACKER UNINITIALIZED"

            return TrackingTelemetry(
                timestamp=res.timestamp,
                status=res.status.value,
                tracking=res.tracking,
                measured_x=meas_x,
                measured_y=meas_y,
                filtered_x=res.position_x,
                filtered_y=res.position_y,
                predicted_x=res.predicted_x,
                predicted_y=res.predicted_y,
                velocity_x=res.velocity_x,
                velocity_y=res.velocity_y,
                speed=speed,
                confidence=res.confidence,
                measurement_available=res.measurement_available,
                consecutive_hits=res.consecutive_hits,
                consecutive_misses=res.consecutive_misses,
                state_uncertainty_x=res.state_uncertainty_x,
                state_uncertainty_y=res.state_uncertainty_y,
                processing_time_ms=res.processing_time_ms,
                status_text=status_text,
            )

    def get_overlay_image_png(self) -> bytes:
        """
        Retrieve PNG byte stream of disturbed observation with Tracking HUD overlay.
        """
        with self._mutex:
            if self._latest_overlay_png is None:
                self.process_detection()
            return self._latest_overlay_png or b""

    def _render_overlay_image(
        self,
        detection: Optional[DetectionResult],
        tracking: TrackingResult,
    ) -> bytes:
        """
        Render multi-layer tracking HUD overlay on disturbed camera sensor observation.
        """
        sensor_image = disturbance_service._latest_image
        cam_frame = camera_service.get_latest_frame()
        w = cam_frame.width if cam_frame else 640
        h = cam_frame.height if cam_frame else 480

        if sensor_image is None or sensor_image.shape != (h, w):
            img_pil = Image.new("RGB", (w, h), (5, 10, 20))
        else:
            if sensor_image.ndim == 2:
                img_pil = Image.fromarray(sensor_image, mode="L").convert("RGB")
            else:
                img_pil = Image.fromarray(sensor_image).convert("RGB")

        draw = ImageDraw.Draw(img_pil)

        cyan = (0, 220, 255)       # Raw detector measurement
        lime = (50, 255, 100)      # Filtered Kalman state
        amber = (255, 180, 20)     # Predicted lead state
        red = (255, 60, 60)        # Track lost
        dim_gray = (60, 80, 100)   # Reticle markings
        yellow = (255, 230, 80)

        # 1. Optical Center Crosshair
        cx, cy = w / 2.0, h / 2.0
        draw.line([(cx - 10, cy), (cx + 10, cy)], fill=dim_gray, width=1)
        draw.line([(cx, cy - 10), (cx, cy + 10)], fill=dim_gray, width=1)

        # 2. Raw Measurement Layer (Cyan)
        if detection and detection.detected and detection.center_x is not None and detection.center_y is not None:
            mx, my = float(detection.center_x), float(detection.center_y)
            if detection.bbox:
                bx0 = detection.bbox.x
                by0 = detection.bbox.y
                bx1 = detection.bbox.x + detection.bbox.width - 1
                by1 = detection.bbox.y + detection.bbox.height - 1
                draw.rectangle([(bx0, by0), (bx1, by1)], outline=cyan, width=1)
            # Small crosshair
            draw.line([(mx - 6, my), (mx + 6, my)], fill=cyan, width=1)
            draw.line([(mx, my - 6), (mx, my + 6)], fill=cyan, width=1)

        # 3. Filtered State Layer (Lime Green)
        if tracking.tracking and tracking.position_x is not None and tracking.position_y is not None:
            fx, fy = float(tracking.position_x), float(tracking.position_y)
            r_reticle = 14

            draw.ellipse([(fx - r_reticle, fy - r_reticle), (fx + r_reticle, fy + r_reticle)], outline=lime, width=2)
            draw.line([(fx - 18, fy), (fx - 6, fy)], fill=lime, width=1)
            draw.line([(fx + 6, fy), (fx + 18, fy)], fill=lime, width=1)
            draw.line([(fx, fy - 18), (fx, fy - 6)], fill=lime, width=1)
            draw.line([(fx, fy + 6), (fx, fy + 18)], fill=lime, width=1)

            # 4. Velocity Vector Arrow
            if tracking.velocity_x is not None and tracking.velocity_y is not None:
                vx, vy = float(tracking.velocity_x), float(tracking.velocity_y)
                v_scale = 0.5
                end_vx = fx + vx * v_scale
                end_vy = fy + vy * v_scale
                draw.line([(fx, fy), (end_vx, end_vy)], fill=yellow, width=2)

            # 5. Lead Predicted State Layer (Amber)
            if tracking.predicted_x is not None and tracking.predicted_y is not None:
                px, py = float(tracking.predicted_x), float(tracking.predicted_y)
                draw.rectangle([(px - 6, py - 6), (px + 6, py + 6)], outline=amber, width=1)
                draw.line([(fx, fy), (px, py)], fill=amber, width=1)

        # 6. Top Status Banner
        if tracking.status == TrackingStatus.TRACKING:
            banner_bg = (0, 35, 20)
            banner_fg = lime
            banner_txt = f"TRACKING | Pos=({tracking.position_x:.1f}, {tracking.position_y:.1f}) | Vel=({tracking.velocity_x:.1f}, {tracking.velocity_y:.1f}) px/s | Conf={tracking.confidence*100:.0f}%"
        elif tracking.status == TrackingStatus.PREDICTING:
            banner_bg = (40, 30, 0)
            banner_fg = amber
            banner_txt = f"PREDICTING (COASTING) | Miss {tracking.consecutive_misses}/{self._config.max_missed_frames} | Pred=({tracking.predicted_x:.1f}, {tracking.predicted_y:.1f}) | Conf={tracking.confidence*100:.0f}%"
        elif tracking.status == TrackingStatus.LOST:
            banner_bg = (45, 10, 10)
            banner_fg = red
            banner_txt = f"TRACK LOST | Missed {tracking.consecutive_misses} Frames | Awaiting Detection"
        else:
            banner_bg = (20, 25, 35)
            banner_fg = cyan
            banner_txt = "TRACKER UNINITIALIZED | Awaiting Beacon Measurement"

        draw.rectangle([(0, 0), (w, 22)], fill=banner_bg)
        draw.text((8, 5), banner_txt, fill=banner_fg)

        # 7. Bottom Diagnostics Footer
        q_val = self._config.process_noise
        r_val = self._config.measurement_noise
        footer_txt = f"KF 2D | Q={q_val:.1f} R={r_val:.1f} | Latency={tracking.processing_time_ms:.2f}ms | Hits={tracking.consecutive_hits} Misses={tracking.consecutive_misses} | t={tracking.timestamp:.2f}s"
        draw.rectangle([(0, h - 20), (w, h)], fill=(10, 15, 25))
        draw.text((8, h - 16), footer_txt, fill=(0, 180, 210))

        buf = io.BytesIO()
        img_pil.save(buf, format="PNG", optimize=True)
        return buf.getvalue()


# Singleton service instance
tracking_service = TrackingService()
