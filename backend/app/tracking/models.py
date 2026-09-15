"""
Data Models and Schemas for Beacon Tracking & Motion Prediction.
Team PHARO — SIH26169
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


class TrackingStatus(str, Enum):
    """
    Operational lifecycle states of the beacon tracking system.
    """
    UNINITIALIZED = "UNINITIALIZED"
    TRACKING = "TRACKING"
    PREDICTING = "PREDICTING"
    LOST = "LOST"


class TrackingConfig(BaseModel):
    """
    Runtime configuration parameters for the 2D Kalman Filter Beacon Tracker.
    """
    enabled: bool = Field(
        default=True,
        description="Whether the Kalman tracking engine is active"
    )
    process_noise: float = Field(
        default=10.0,
        ge=0.0,
        le=1000.0,
        description="Continuous process noise spectral density q (acceleration variance)"
    )
    measurement_noise: float = Field(
        default=4.0,
        ge=0.01,
        le=500.0,
        description="Detector measurement noise variance r (pixel variance sigma_z^2)"
    )
    initial_position_uncertainty: float = Field(
        default=100.0,
        ge=0.1,
        le=10000.0,
        description="Initial position variance for state covariance P (pixels^2)"
    )
    initial_velocity_uncertainty: float = Field(
        default=400.0,
        ge=0.1,
        le=100000.0,
        description="Initial velocity variance for state covariance P (pixels^2/s^2)"
    )
    max_missed_frames: int = Field(
        default=10,
        ge=1,
        le=120,
        description="Maximum consecutive missed detections before declaring track lost"
    )
    min_detection_confidence: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Minimum detector confidence required to accept a measurement update"
    )
    prediction_enabled: bool = Field(
        default=True,
        description="Whether motion state extrapolation / lead prediction is enabled"
    )
    prediction_lead_time: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Future lead time tau (seconds) for forward trajectory extrapolation"
    )
    adaptive_measurement_noise: bool = Field(
        default=True,
        description="Whether measurement noise R scales inversely with detector confidence"
    )
    max_dt: float = Field(
        default=1.0,
        ge=0.001,
        le=10.0,
        description="Maximum allowed dt step in seconds before falling back to nominal dt"
    )
    min_dt: float = Field(
        default=1e-4,
        ge=1e-6,
        description="Minimum allowed dt step to prevent singular matrix operations"
    )

    model_config = ConfigDict(validate_assignment=True)


class TrackingResult(BaseModel):
    """
    Stable tracking output contract consumed by downstream Alignment/PID controllers and UI.
    
    CRITICAL: Contains solely filter estimates and measurement telemetry.
    No ground-truth platform coordinates are exposed or utilized here.
    """
    timestamp: float = Field(
        default=0.0,
        ge=0.0,
        description="Simulation timestamp in seconds"
    )
    initialized: bool = Field(
        default=False,
        description="Whether the tracker has been initialized with at least one valid measurement"
    )
    tracking: bool = Field(
        default=False,
        description="True if currently tracking or actively coasting in PREDICTING state"
    )
    status: TrackingStatus = Field(
        default=TrackingStatus.UNINITIALIZED,
        description="Current tracking state (UNINITIALIZED, TRACKING, PREDICTING, LOST)"
    )
    position_x: Optional[float] = Field(
        default=None,
        description="Filtered horizontal beacon position on focal plane px (pixels)"
    )
    position_y: Optional[float] = Field(
        default=None,
        description="Filtered vertical beacon position on focal plane py (pixels)"
    )
    velocity_x: Optional[float] = Field(
        default=None,
        description="Estimated horizontal beacon velocity vx (pixels/second)"
    )
    velocity_y: Optional[float] = Field(
        default=None,
        description="Estimated vertical beacon velocity vy (pixels/second)"
    )
    predicted_x: Optional[float] = Field(
        default=None,
        description="Lead-predicted horizontal position (pixels) for latency compensation"
    )
    predicted_y: Optional[float] = Field(
        default=None,
        description="Lead-predicted vertical position (pixels) for latency compensation"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Tracking quality confidence score [0.0, 1.0]"
    )
    measurement_available: bool = Field(
        default=False,
        description="Whether a valid detector measurement was received in the current frame"
    )
    measurement_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Raw detector confidence of the current frame measurement"
    )
    consecutive_hits: int = Field(
        default=0,
        ge=0,
        description="Number of consecutive frames with successful detector updates"
    )
    consecutive_misses: int = Field(
        default=0,
        ge=0,
        description="Number of consecutive frames with missing or rejected measurements"
    )
    state_uncertainty_x: Optional[float] = Field(
        default=None,
        description="1-sigma standard deviation for horizontal position: sqrt(P[0,0])"
    )
    state_uncertainty_y: Optional[float] = Field(
        default=None,
        description="1-sigma standard deviation for vertical position: sqrt(P[1,1])"
    )
    velocity_uncertainty_x: Optional[float] = Field(
        default=None,
        description="1-sigma standard deviation for horizontal velocity: sqrt(P[2,2])"
    )
    velocity_uncertainty_y: Optional[float] = Field(
        default=None,
        description="1-sigma standard deviation for vertical velocity: sqrt(P[3,3])"
    )
    prediction_valid: bool = Field(
        default=False,
        description="Whether position estimates (filtered/predicted) are considered valid"
    )
    processing_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Execution latency of the tracking update step in milliseconds"
    )
    message: str = Field(
        default="",
        description="Diagnostic or state transition narrative"
    )


class TrackingStatusInfo(BaseModel):
    """
    Lifecycle status, active configuration, and cumulative performance statistics.
    """
    initialized: bool = Field(description="Whether tracker is initialized")
    status: TrackingStatus = Field(description="Current tracking state")
    config: TrackingConfig = Field(description="Active tracking configuration")
    total_updates: int = Field(default=0, ge=0, description="Total update steps executed")
    tracking_hits: int = Field(default=0, ge=0, description="Total measurement updates accepted")
    tracking_misses: int = Field(default=0, ge=0, description="Total missed / rejected frames")
    current_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Latest tracking confidence")
    current_timestamp: float = Field(default=0.0, ge=0.0, description="Current simulation timestamp in seconds")
    latest_position_x: Optional[float] = Field(default=None, description="Latest filtered position x")
    latest_position_y: Optional[float] = Field(default=None, description="Latest filtered position y")
    latest_velocity_x: Optional[float] = Field(default=None, description="Latest estimated velocity vx")
    latest_velocity_y: Optional[float] = Field(default=None, description="Latest estimated velocity vy")


class TrackingTelemetry(BaseModel):
    """
    Real-time telemetry packet for HUD displays and diagnostic visualizers.
    """
    timestamp: float = Field(description="Simulation timestamp in seconds")
    status: str = Field(description="Tracking status string")
    tracking: bool = Field(description="Whether tracking is active")
    measured_x: Optional[float] = Field(default=None, description="Raw detector horizontal center (px)")
    measured_y: Optional[float] = Field(default=None, description="Raw detector vertical center (px)")
    filtered_x: Optional[float] = Field(default=None, description="Kalman filtered horizontal position (px)")
    filtered_y: Optional[float] = Field(default=None, description="Kalman filtered vertical position (px)")
    predicted_x: Optional[float] = Field(default=None, description="Lead-predicted horizontal position (px)")
    predicted_y: Optional[float] = Field(default=None, description="Lead-predicted vertical position (px)")
    velocity_x: Optional[float] = Field(default=None, description="Estimated horizontal velocity (px/s)")
    velocity_y: Optional[float] = Field(default=None, description="Estimated vertical velocity (px/s)")
    speed: Optional[float] = Field(default=None, description="Estimated 2D pixel speed sqrt(vx^2 + vy^2) (px/s)")
    confidence: float = Field(description="Tracking confidence score [0, 1]")
    measurement_available: bool = Field(description="Whether detection was available in this frame")
    consecutive_hits: int = Field(description="Current hit streak")
    consecutive_misses: int = Field(description="Current miss streak")
    state_uncertainty_x: Optional[float] = Field(default=None, description="Horizontal uncertainty sigma_x (px)")
    state_uncertainty_y: Optional[float] = Field(default=None, description="Vertical uncertainty sigma_y (px)")
    processing_time_ms: float = Field(description="Execution latency (ms)")
    status_text: str = Field(description="Human-readable tracking banner")
