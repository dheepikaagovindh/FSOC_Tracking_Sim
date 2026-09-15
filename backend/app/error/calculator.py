"""
Pure Mathematical Engine for Optical Boresight Alignment Error Transformation.
Team PHARO — SIH26169

Converts focal-plane pixel coordinates into relative pixel, normalized, and angular errors
using pinhole optical camera intrinsics.
"""

from __future__ import annotations
import math
from typing import Optional, Tuple
import numpy as np

from .models import AlignmentConfig, AlignmentError, ErrorStatus, ErrorSource


class ErrorCalculator:
    """
    Stateless geometric calculator for optical boresight alignment errors.
    """

    @staticmethod
    def calculate_intrinsics(
        width: int,
        height: int,
        hfov_deg: float,
        vfov_deg: float,
    ) -> Tuple[float, float, float, float]:
        """
        Compute pinhole camera focal lengths and principal point.
        
        Returns:
            (fx, fy, cx, cy)
        """
        if width <= 0 or height <= 0:
            raise ValueError(f"Image dimensions must be positive integers, got {width}x{height}")
        if not (0.0 < hfov_deg < 180.0):
            raise ValueError(f"Horizontal FOV must be in (0, 180) degrees, got {hfov_deg}")
        if not (0.0 < vfov_deg < 180.0):
            raise ValueError(f"Vertical FOV must be in (0, 180) degrees, got {vfov_deg}")

        hfov_rad = math.radians(hfov_deg)
        vfov_rad = math.radians(vfov_deg)

        fx = float(width) / (2.0 * math.tan(hfov_rad / 2.0))
        fy = float(height) / (2.0 * math.tan(vfov_rad / 2.0))
        cx = float(width) / 2.0
        cy = float(height) / 2.0

        return fx, fy, cx, cy

    @classmethod
    def compute_error(
        cls,
        target_x: Optional[float],
        target_y: Optional[float],
        source: ErrorSource,
        width: int,
        height: int,
        hfov_deg: float,
        vfov_deg: float,
        config: AlignmentConfig,
        timestamp: float = 0.0,
        tracking_confidence: float = 0.0,
        prev_error: Optional[Tuple[float, float, float]] = None,  # (prev_ex, prev_ey, prev_t)
    ) -> AlignmentError:
        """
        Compute complete AlignmentError contract from target pixel coordinates.

        Coordinate System Conventions:
          ex > 0: target is to the RIGHT of optical center
          ex < 0: target is to the LEFT of optical center
          ey > 0: target is BELOW optical center (+Y is downward in image pixels)
          ey < 0: target is ABOVE optical center
        """
        fx, fy, cx, cy = cls.calculate_intrinsics(width, height, hfov_deg, vfov_deg)

        # Check validity
        if (
            target_x is None
            or target_y is None
            or not math.isfinite(target_x)
            or not math.isfinite(target_y)
            or source == ErrorSource.NONE
        ):
            return AlignmentError(
                timestamp=timestamp,
                valid=False,
                status=ErrorStatus.INVALID,
                source=ErrorSource.NONE,
                target_x=None,
                target_y=None,
                center_x=cx,
                center_y=cy,
                pixel_error_x=None,
                pixel_error_y=None,
                pixel_error_magnitude=None,
                normalized_error_x=None,
                normalized_error_y=None,
                normalized_error_magnitude=None,
                angular_error_x_deg=None,
                angular_error_y_deg=None,
                angular_error_magnitude_deg=None,
                true_angular_separation_deg=None,
                error_direction_deg=None,
                delta_error_x=None,
                delta_error_y=None,
                error_rate_x=None,
                error_rate_y=None,
                aligned=False,
                radially_aligned=False,
                tracking_confidence=0.0,
                image_width=width,
                image_height=height,
                horizontal_fov_deg=hfov_deg,
                vertical_fov_deg=vfov_deg,
                pixel_tolerance=config.pixel_tolerance,
                angular_tolerance_deg=config.angular_tolerance_deg,
                message="Invalid or missing target tracking state",
            )

        # 1. Pixel Errors
        ex = float(target_x - cx)
        ey = float(target_y - cy)
        pixel_mag = float(math.hypot(ex, ey))

        # 2. Normalized Errors [-1.0, 1.0] relative to half-dimensions
        norm_ex = float(ex / cx) if cx > 0 else 0.0
        norm_ey = float(ey / cy) if cy > 0 else 0.0
        norm_mag = float(math.hypot(norm_ex, norm_ey))

        # 3. Angular Errors (Pinhole projection in degrees)
        # angle_x: atan2(ex, fx) (positive = right)
        # angle_y: atan2(ey, fy) (positive = below)
        ang_x_deg = float(math.degrees(math.atan2(ex, fx)))
        ang_y_deg = float(math.degrees(math.atan2(ey, fy)))
        ang_mag_deg = float(math.hypot(ang_x_deg, ang_y_deg))

        # Exact 3D conical angle off optical boresight axis
        tan_norm_sq = (ex / fx) ** 2 + (ey / fy) ** 2
        true_sep_deg = float(math.degrees(math.atan2(math.sqrt(tan_norm_sq), 1.0)))

        # 4. Error Direction Vector Angle in [-180, 180] deg (0 = Right, 90 = Down, 180/-180 = Left, -90 = Up)
        direction_deg = float(math.degrees(math.atan2(ey, ex))) if (ex != 0.0 or ey != 0.0) else 0.0

        # 5. Delta & Derivative Rates
        delta_ex: Optional[float] = None
        delta_ey: Optional[float] = None
        rate_x: Optional[float] = None
        rate_y: Optional[float] = None

        if prev_error is not None:
            pex, pey, pt = prev_error
            dt = timestamp - pt
            if dt > 1e-4:
                delta_ex = float(ex - pex)
                delta_ey = float(ey - pey)
                rate_x = float(delta_ex / dt)
                rate_y = float(delta_ey / dt)

        # 6. Alignment Lock Condition Evaluation
        if config.use_angular_alignment:
            is_component_aligned = (
                abs(ang_x_deg) <= config.angular_tolerance_deg
                and abs(ang_y_deg) <= config.angular_tolerance_deg
            )
            is_radial_aligned = ang_mag_deg <= config.angular_tolerance_deg
        else:
            is_component_aligned = (
                abs(ex) <= config.pixel_tolerance
                and abs(ey) <= config.pixel_tolerance
            )
            is_radial_aligned = pixel_mag <= config.pixel_tolerance

        is_aligned = is_radial_aligned if config.use_radial_alignment else is_component_aligned
        status = ErrorStatus.ALIGNED if is_aligned else ErrorStatus.VALID

        source_label = "Filtered Track" if source == ErrorSource.FILTERED else "Predicted Motion"
        msg = f"Target {status.value} ({source_label} | Pixel: {pixel_mag:.1f}px | Angular: {ang_mag_deg:.2f}°)"

        return AlignmentError(
            timestamp=timestamp,
            valid=True,
            status=status,
            source=source,
            target_x=round(target_x, 3),
            target_y=round(target_y, 3),
            center_x=cx,
            center_y=cy,
            pixel_error_x=round(ex, 3),
            pixel_error_y=round(ey, 3),
            pixel_error_magnitude=round(pixel_mag, 3),
            normalized_error_x=round(norm_ex, 4),
            normalized_error_y=round(norm_ey, 4),
            normalized_error_magnitude=round(norm_mag, 4),
            angular_error_x_deg=round(ang_x_deg, 4),
            angular_error_y_deg=round(ang_y_deg, 4),
            angular_error_magnitude_deg=round(ang_mag_deg, 4),
            true_angular_separation_deg=round(true_sep_deg, 4),
            error_direction_deg=round(direction_deg, 2),
            delta_error_x=round(delta_ex, 3) if delta_ex is not None else None,
            delta_error_y=round(delta_ey, 3) if delta_ey is not None else None,
            error_rate_x=round(rate_x, 2) if rate_x is not None else None,
            error_rate_y=round(rate_y, 2) if rate_y is not None else None,
            aligned=is_aligned,
            radially_aligned=is_radial_aligned,
            tracking_confidence=round(tracking_confidence, 4),
            image_width=width,
            image_height=height,
            horizontal_fov_deg=hfov_deg,
            vertical_fov_deg=vfov_deg,
            pixel_tolerance=config.pixel_tolerance,
            angular_tolerance_deg=config.angular_tolerance_deg,
            message=msg,
        )
