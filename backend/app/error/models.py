"""
Data Models and Schemas for Error Calculation & Boresight Alignment.
Team PHARO — SIH26169
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ErrorStatus(str, Enum):
    """
    Operational alignment condition status.
    """
    INVALID = "INVALID"  # No valid tracking estimate available
    VALID = "VALID"      # Valid target tracked, but outside alignment tolerance
    ALIGNED = "ALIGNED"  # Valid target tracked and inside alignment tolerance


class ErrorSource(str, Enum):
    """
    Source of the target coordinates used for alignment error calculation.
    """
    FILTERED = "FILTERED"    # From Kalman filtered position (TRACKING state)
    PREDICTED = "PREDICTED"  # From Kalman forward motion prediction (PREDICTING state)
    NONE = "NONE"            # No target available (UNINITIALIZED or LOST state)


class AlignmentConfig(BaseModel):
    """
    Runtime configuration for Error Calculation & Alignment evaluation.
    """
    enabled: bool = Field(
        default=True,
        description="Whether the error calculation engine is active"
    )
    pixel_tolerance: float = Field(
        default=5.0,
        ge=0.1,
        le=200.0,
        description="Pixel alignment lock tolerance radius around optical center (px)"
    )
    angular_tolerance_deg: float = Field(
        default=0.25,
        ge=0.001,
        le=30.0,
        description="Angular alignment lock tolerance threshold (degrees)"
    )
    use_angular_alignment: bool = Field(
        default=True,
        description="Whether alignment condition is evaluated in angular degrees (True) or pixels (False)"
    )
    use_radial_alignment: bool = Field(
        default=True,
        description="Whether alignment requires radial magnitude <= tolerance (True) or component-wise |ex|<=tol & |ey|<=tol (False)"
    )
    use_prediction_when_tracking_missing: bool = Field(
        default=True,
        description="Whether to use lead predicted position when detector measurement is missing (PREDICTING state)"
    )

    model_config = ConfigDict(validate_assignment=True)


class AlignmentError(BaseModel):
    """
    Stable alignment error contract consumed by downstream Pan-Tilt/PID Controllers and UI.
    
    Coordinate Sign Conventions:
      ex, angular_error_x: Positive = target is to the RIGHT of optical center
                           Negative = target is to the LEFT of optical center
      ey, angular_error_y: Positive = target is BELOW optical center (+Y is downward in pixel coordinates)
                           Negative = target is ABOVE optical center
    """
    timestamp: float = Field(
        default=0.0,
        ge=0.0,
        description="Simulation timestamp in seconds"
    )
    valid: bool = Field(
        default=False,
        description="True if error calculation is mathematically valid and based on a reliable track"
    )
    status: ErrorStatus = Field(
        default=ErrorStatus.INVALID,
        description="Alignment status (INVALID, VALID, ALIGNED)"
    )
    source: ErrorSource = Field(
        default=ErrorSource.NONE,
        description="Target coordinate source (FILTERED, PREDICTED, NONE)"
    )
    target_x: Optional[float] = Field(
        default=None,
        description="Selected target horizontal focal-plane position (px)"
    )
    target_y: Optional[float] = Field(
        default=None,
        description="Selected target vertical focal-plane position (px)"
    )
    center_x: float = Field(
        default=320.0,
        description="Optical axis boresight horizontal center cx (px)"
    )
    center_y: float = Field(
        default=240.0,
        description="Optical axis boresight vertical center cy (px)"
    )
    pixel_error_x: Optional[float] = Field(
        default=None,
        description="Horizontal pixel error: ex = target_x - center_x (px)"
    )
    pixel_error_y: Optional[float] = Field(
        default=None,
        description="Vertical pixel error: ey = target_y - center_y (px)"
    )
    pixel_error_magnitude: Optional[float] = Field(
        default=None,
        description="Radial Euclidean pixel error: sqrt(ex^2 + ey^2) (px)"
    )
    normalized_error_x: Optional[float] = Field(
        default=None,
        description="Normalized horizontal error: ex / (width / 2) [-1, 1]"
    )
    normalized_error_y: Optional[float] = Field(
        default=None,
        description="Normalized vertical error: ey / (height / 2) [-1, 1]"
    )
    normalized_error_magnitude: Optional[float] = Field(
        default=None,
        description="Normalized radial error: sqrt(norm_ex^2 + norm_ey^2)"
    )
    angular_error_x_deg: Optional[float] = Field(
        default=None,
        description="Horizontal boresight pointing error in degrees: atan2(ex, fx) (deg)"
    )
    angular_error_y_deg: Optional[float] = Field(
        default=None,
        description="Vertical boresight pointing error in degrees: atan2(ey, fy) (deg)"
    )
    angular_error_magnitude_deg: Optional[float] = Field(
        default=None,
        description="Radial angular error magnitude in degrees: sqrt(ang_x^2 + ang_y^2) (deg)"
    )
    true_angular_separation_deg: Optional[float] = Field(
        default=None,
        description="Exact 3D conical angle off optical axis: atan2(sqrt((ex/fx)^2 + (ey/fy)^2), 1.0) (deg)"
    )
    error_direction_deg: Optional[float] = Field(
        default=None,
        description="Error vector direction angle: atan2(ey, ex) in [-180, 180] degrees"
    )
    delta_error_x: Optional[float] = Field(
        default=None,
        description="Change in horizontal error from previous frame: dex = ex_k - ex_{k-1} (px)"
    )
    delta_error_y: Optional[float] = Field(
        default=None,
        description="Change in vertical error from previous frame: dey = ey_k - ey_{k-1} (px)"
    )
    error_rate_x: Optional[float] = Field(
        default=None,
        description="Time derivative of horizontal error: dex / dt (px/s)"
    )
    error_rate_y: Optional[float] = Field(
        default=None,
        description="Time derivative of vertical error: dey / dt (px/s)"
    )
    aligned: bool = Field(
        default=False,
        description="True if target is within alignment lock tolerance"
    )
    radially_aligned: bool = Field(
        default=False,
        description="True if radial error magnitude is within alignment lock tolerance"
    )
    tracking_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence of the underlying tracking result"
    )
    image_width: int = Field(
        default=640,
        description="Active camera image width (px)"
    )
    image_height: int = Field(
        default=480,
        description="Active camera image height (px)"
    )
    horizontal_fov_deg: float = Field(
        default=30.0,
        description="Camera horizontal field-of-view (deg)"
    )
    vertical_fov_deg: float = Field(
        default=22.5,
        description="Camera vertical field-of-view (deg)"
    )
    pixel_tolerance: float = Field(
        default=5.0,
        description="Active pixel lock tolerance (px)"
    )
    angular_tolerance_deg: float = Field(
        default=0.25,
        description="Active angular lock tolerance (deg)"
    )
    message: str = Field(
        default="",
        description="Status description or diagnostic narrative"
    )


class ErrorStatusInfo(BaseModel):
    """
    Lifecycle status, active configuration, and alignment metrics summary.
    """
    initialized: bool = Field(description="Whether error engine is initialized")
    status: ErrorStatus = Field(description="Current alignment status")
    config: AlignmentConfig = Field(description="Active alignment configuration")
    total_calculations: int = Field(default=0, ge=0, description="Total error calculations executed")
    aligned_frames_count: int = Field(default=0, ge=0, description="Total frames in ALIGNED state")
    current_pixel_error_magnitude: Optional[float] = Field(default=None, description="Latest pixel error magnitude")
    current_angular_error_magnitude_deg: Optional[float] = Field(default=None, description="Latest angular error magnitude")
    current_aligned: bool = Field(default=False, description="Whether currently aligned")
    current_timestamp: float = Field(default=0.0, description="Current simulation timestamp")


class ErrorTelemetry(BaseModel):
    """
    Real-time telemetry packet for HUD displays, crosshairs, and diagnostic monitors.
    """
    timestamp: float = Field(description="Simulation timestamp in seconds")
    valid: bool = Field(description="Error validity flag")
    status: str = Field(description="Error status string (INVALID, VALID, ALIGNED)")
    source: str = Field(description="Target coordinate source (FILTERED, PREDICTED, NONE)")
    target_x: Optional[float] = Field(default=None, description="Target X (px)")
    target_y: Optional[float] = Field(default=None, description="Target Y (px)")
    center_x: float = Field(description="Optical center X (px)")
    center_y: float = Field(description="Optical center Y (px)")
    pixel_error_x: Optional[float] = Field(default=None, description="Pixel error X (px)")
    pixel_error_y: Optional[float] = Field(default=None, description="Pixel error Y (px)")
    pixel_error_magnitude: Optional[float] = Field(default=None, description="Pixel error magnitude (px)")
    angular_error_x_deg: Optional[float] = Field(default=None, description="Angular error X (deg)")
    angular_error_y_deg: Optional[float] = Field(default=None, description="Angular error Y (deg)")
    angular_error_magnitude_deg: Optional[float] = Field(default=None, description="Angular error magnitude (deg)")
    error_direction_deg: Optional[float] = Field(default=None, description="Error direction (deg)")
    error_rate_x: Optional[float] = Field(default=None, description="Error rate X (px/s)")
    error_rate_y: Optional[float] = Field(default=None, description="Error rate Y (px/s)")
    aligned: bool = Field(description="Alignment lock flag")
    radially_aligned: bool = Field(description="Radial alignment lock flag")
    tracking_confidence: float = Field(description="Tracking confidence")
    pixel_tolerance: float = Field(description="Active pixel tolerance")
    angular_tolerance_deg: float = Field(description="Active angular tolerance")
    status_text: str = Field(description="Human-readable alignment status banner")
