"""
Beacon Detection & Centroiding Engine.
Team PHARO — SIH26169

Core detection pipeline for Free-Space Optical Communication (FSOC) coarse alignment.
Performs adaptive background estimation, spot detection, sub-pixel centroid localization,
signal quality evaluation, and boresight error estimation.
"""

from __future__ import annotations
import math
import time
from typing import Optional, Tuple
import numpy as np

from .models import (
    DetectionConfig,
    DetectionResult,
    DetectionError,
    BoundingBox,
    SignalMetrics,
)
from .threshold import (
    estimate_background_noise,
    compute_adaptive_threshold,
    find_candidate_peak,
    extract_roi,
)
from .centroid import (
    intensity_weighted_centroid,
    gaussian_subpixel_refinement,
    calculate_bounding_box,
)
from .metrics import calculate_signal_metrics


class BeaconDetector:
    """
    High-performance optical beacon detector and sub-pixel centroiding engine.
    """

    def __init__(self, default_config: Optional[DetectionConfig] = None):
        self._config = default_config or DetectionConfig()

    @property
    def config(self) -> DetectionConfig:
        return self._config

    @config.setter
    def config(self, new_config: DetectionConfig):
        self._config = new_config

    def detect(
        self,
        image: np.ndarray,
        config: Optional[DetectionConfig] = None,
        timestamp: float = 0.0,
        frame_index: int = 0,
        fx: float = 800.0,
        fy: float = 800.0,
        cx: float = 320.0,
        cy: float = 240.0,
        ground_truth_u: Optional[float] = None,
        ground_truth_v: Optional[float] = None,
        beacon_visible: bool = True,
    ) -> DetectionResult:
        """
        Execute beacon detection and sub-pixel localization on a 2D sensor image array.

        Parameters:
          image: 2D uint8 NumPy grayscale sensor array (H, W).
          config: Optional override DetectionConfig.
          timestamp: Simulation timestamp in seconds.
          frame_index: Discrete frame index.
          fx, fy, cx, cy: Camera optical intrinsics.
          ground_truth_u, ground_truth_v: True focal plane coordinates (benchmarking only).
          beacon_visible: Whether ground truth beacon is physically visible in front of camera.

        Returns:
          DetectionResult containing detection state, coordinates, quality metrics, and errors.
        """
        t_start = time.perf_counter()
        active_config = config or self._config

        if image is None or image.size == 0:
            t_exec = (time.perf_counter() - t_start) * 1000.0
            return self._build_null_result(
                timestamp=timestamp,
                frame_index=frame_index,
                algorithm=active_config.algorithm,
                t_exec=t_exec,
                message="Empty or invalid image array received",
            )

        # 1. Background Noise Floor Estimation and Dynamic Thresholding
        threshold, mu_bg, sigma_bg = compute_adaptive_threshold(
            image=image,
            k_sigma=active_config.k_sigma,
        )

        # 2. Candidate Peak Search
        peak_match = find_candidate_peak(
            image=image,
            threshold=threshold,
            min_pnr=active_config.min_pnr,
            mu_bg=mu_bg,
            sigma_bg=sigma_bg,
        )

        if peak_match is None:
            t_exec = (time.perf_counter() - t_start) * 1000.0
            flat_idx = int(np.argmax(image))
            py, px = divmod(flat_idx, image.shape[1])
            peak_val = float(image[py, px])
            metrics = calculate_signal_metrics(
                image=image,
                roi=np.zeros((1, 1), dtype=np.uint8),
                peak_val=peak_val,
                mu_bg=mu_bg,
                sigma_bg=sigma_bg,
                threshold=threshold,
                flux=0.0,
                detected=False,
            )
            err_diag = self._evaluate_error(
                u_est=None,
                v_est=None,
                az_est=None,
                el_est=None,
                gt_u=ground_truth_u,
                gt_v=ground_truth_v,
                fx=fx,
                fy=fy,
                cx=cx,
                cy=cy,
                visible=beacon_visible,
            )
            return DetectionResult(
                timestamp=timestamp,
                frame_index=frame_index,
                detected=False,
                u=None,
                v=None,
                azimuth_deg=None,
                elevation_deg=None,
                bbox=None,
                metrics=metrics,
                error=err_diag,
                algorithm_used=active_config.algorithm,
                execution_time_ms=round(t_exec, 3),
                message="Beacon signal below detection threshold or absent",
            )

        peak_x, peak_y, peak_val, pnr = peak_match

        # 3. Localized ROI Extraction
        roi, x_min, y_min, x_max, y_max = extract_roi(
            image=image,
            center_x=peak_x,
            center_y=peak_y,
            radius=active_config.roi_radius,
        )

        local_peak_x = peak_x - x_min
        local_peak_y = peak_y - y_min

        # 4. Centroiding Algorithm Execution
        algo = active_config.algorithm
        u_est: float = 0.0
        v_est: float = 0.0
        flux: float = 0.0

        if algo == "com":
            x_rel, y_rel, flux = intensity_weighted_centroid(roi, threshold)
            u_est = x_min + x_rel
            v_est = y_min + y_rel

        elif algo == "adaptive_threshold":
            x_rel, y_rel, flux = intensity_weighted_centroid(roi, threshold)
            u_est = x_min + x_rel
            v_est = y_min + y_rel

        elif algo == "gaussian_fit":
            x_sub, y_sub = gaussian_subpixel_refinement(roi, local_peak_x, local_peak_y)
            u_est = x_min + x_sub
            v_est = y_min + y_sub
            _, _, flux = intensity_weighted_centroid(roi, threshold)

        elif algo == "hybrid":
            # Multi-stage: Localized Intensity-Weighted CoM + Gaussian Sub-Pixel Refinement
            x_rel, y_rel, flux = intensity_weighted_centroid(roi, threshold)
            u_com = x_min + x_rel
            v_com = y_min + y_rel

            if active_config.subpixel_refinement:
                x_sub, y_sub = gaussian_subpixel_refinement(roi, local_peak_x, local_peak_y)
                u_gauss = x_min + x_sub
                v_gauss = y_min + y_sub
                # Blend CoM and Gaussian fit with 70% CoM, 30% Gaussian peak fit for robust stability
                u_est = 0.70 * u_com + 0.30 * u_gauss
                v_est = 0.70 * v_com + 0.30 * v_gauss
            else:
                u_est = u_com
                v_est = v_com
        else:
            # Default fallback
            x_rel, y_rel, flux = intensity_weighted_centroid(roi, threshold)
            u_est = x_min + x_rel
            v_est = y_min + y_rel

        # 5. Spot Flux Validation
        if flux < active_config.min_flux:
            t_exec = (time.perf_counter() - t_start) * 1000.0
            metrics = calculate_signal_metrics(
                image=image,
                roi=roi,
                peak_val=peak_val,
                mu_bg=mu_bg,
                sigma_bg=sigma_bg,
                threshold=threshold,
                flux=flux,
                detected=False,
            )
            err_diag = self._evaluate_error(
                u_est=None,
                v_est=None,
                az_est=None,
                el_est=None,
                gt_u=ground_truth_u,
                gt_v=ground_truth_v,
                fx=fx,
                fy=fy,
                cx=cx,
                cy=cy,
                visible=beacon_visible,
            )
            return DetectionResult(
                timestamp=timestamp,
                frame_index=frame_index,
                detected=False,
                u=None,
                v=None,
                azimuth_deg=None,
                elevation_deg=None,
                bbox=None,
                metrics=metrics,
                error=err_diag,
                algorithm_used=algo,
                execution_time_ms=round(t_exec, 3),
                message="Spot integrated flux below minimum threshold",
            )

        # 6. Bounding Box Calculation
        bbox = calculate_bounding_box(
            roi=roi,
            threshold=threshold,
            origin_x=x_min,
            origin_y=y_min,
        )

        # 7. Signal Quality & Confidence Metrics
        metrics = calculate_signal_metrics(
            image=image,
            roi=roi,
            peak_val=peak_val,
            mu_bg=mu_bg,
            sigma_bg=sigma_bg,
            threshold=threshold,
            flux=flux,
            detected=True,
        )

        # 8. Boresight Angular Bearings Estimation
        norm_x = (u_est - cx) / fx
        norm_y = (cy - v_est) / fy
        r_horiz = math.sqrt(norm_x * norm_x + 1.0)
        azimuth_deg = math.degrees(math.atan2(norm_x, 1.0))
        elevation_deg = math.degrees(math.atan2(norm_y, r_horiz))

        # 9. Ground-Truth Error Diagnostics
        err_diag = self._evaluate_error(
            u_est=u_est,
            v_est=v_est,
            az_est=azimuth_deg,
            el_est=elevation_deg,
            gt_u=ground_truth_u,
            gt_v=ground_truth_v,
            fx=fx,
            fy=fy,
            cx=cx,
            cy=cy,
            visible=beacon_visible,
        )

        t_exec = (time.perf_counter() - t_start) * 1000.0

        return DetectionResult(
            timestamp=timestamp,
            frame_index=frame_index,
            detected=True,
            u=round(u_est, 3),
            v=round(v_est, 3),
            azimuth_deg=round(azimuth_deg, 4),
            elevation_deg=round(elevation_deg, 4),
            bbox=bbox,
            metrics=metrics,
            error=err_diag,
            algorithm_used=algo,
            execution_time_ms=round(t_exec, 3),
            message="Beacon successfully acquired and centroid localized",
        )

    def _evaluate_error(
        self,
        u_est: Optional[float],
        v_est: Optional[float],
        az_est: Optional[float],
        el_est: Optional[float],
        gt_u: Optional[float],
        gt_v: Optional[float],
        fx: float,
        fy: float,
        cx: float,
        cy: float,
        visible: bool,
    ) -> DetectionError:
        """
        Compute localization and angular estimation errors against ground-truth beacon position.
        """
        if gt_u is None or gt_v is None or not visible:
            return DetectionError(
                has_ground_truth=False,
                true_u=gt_u,
                true_v=gt_v,
                error_u=None,
                error_v=None,
                radial_error=None,
                error_azimuth_deg=None,
                error_elevation_deg=None,
            )

        if u_est is None or v_est is None:
            return DetectionError(
                has_ground_truth=True,
                true_u=round(gt_u, 3),
                true_v=round(gt_v, 3),
                error_u=None,
                error_v=None,
                radial_error=None,
                error_azimuth_deg=None,
                error_elevation_deg=None,
            )

        du = u_est - gt_u
        dv = v_est - gt_v
        dr = math.sqrt(du * du + dv * dv)

        # True angles from ground truth
        gt_norm_x = (gt_u - cx) / fx
        gt_norm_y = (cy - gt_v) / fy
        gt_r_horiz = math.sqrt(gt_norm_x * gt_norm_x + 1.0)
        gt_az = math.degrees(math.atan2(gt_norm_x, 1.0))
        gt_el = math.degrees(math.atan2(gt_norm_y, gt_r_horiz))

        d_az = az_est - gt_az if az_est is not None else None
        d_el = el_est - gt_el if el_est is not None else None

        return DetectionError(
            has_ground_truth=True,
            true_u=round(gt_u, 3),
            true_v=round(gt_v, 3),
            error_u=round(du, 4),
            error_v=round(dv, 4),
            radial_error=round(dr, 4),
            error_azimuth_deg=round(d_az, 4) if d_az is not None else None,
            error_elevation_deg=round(d_el, 4) if d_el is not None else None,
        )

    def _build_null_result(
        self,
        timestamp: float,
        frame_index: int,
        algorithm: str,
        t_exec: float,
        message: str,
    ) -> DetectionResult:
        """
        Construct empty DetectionResult when no image or fatal error occurs.
        """
        return DetectionResult(
            timestamp=timestamp,
            frame_index=frame_index,
            detected=False,
            u=None,
            v=None,
            azimuth_deg=None,
            elevation_deg=None,
            bbox=None,
            metrics=SignalMetrics(
                peak_intensity=0.0,
                background_mean=0.0,
                background_std=1.0,
                threshold=0.0,
                pnr=0.0,
                snr_db=-20.0,
                flux=0.0,
                confidence=0.0,
            ),
            error=DetectionError(has_ground_truth=False),
            algorithm_used=algorithm,
            execution_time_ms=round(t_exec, 3),
            message=message,
        )
