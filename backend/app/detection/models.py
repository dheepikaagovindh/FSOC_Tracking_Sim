"""
Domain Models and Data Structures for Beacon Detection.
Team PHARO — SIH26169
"""

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


class BoundingBox(BaseModel):
    """
    Axis-aligned 2D bounding box enclosing a detected beacon candidate.
    Coordinates match camera sensor: origin (0, 0) is top-left.
    """
    x: int = Field(description="Top-left horizontal pixel coordinate (x / u_min)")
    y: int = Field(description="Top-left vertical pixel coordinate (y / v_min)")
    width: int = Field(description="Bounding box width in pixels", ge=1)
    height: int = Field(description="Bounding box height in pixels", ge=1)

    @property
    def x_min(self) -> int:
        return self.x

    @property
    def y_min(self) -> int:
        return self.y

    @property
    def x_max(self) -> int:
        return self.x + self.width - 1

    @property
    def y_max(self) -> int:
        return self.y + self.height - 1

    @property
    def center_x(self) -> float:
        return self.x + (self.width - 1) / 2.0

    @property
    def center_y(self) -> float:
        return self.y + (self.height - 1) / 2.0


class CandidateInfo(BaseModel):
    """
    Diagnostic representation of an extracted beacon candidate contour/blob.
    """
    candidate_id: int = Field(description="Candidate index in frame")
    bbox: BoundingBox = Field(description="Candidate bounding box")
    area: float = Field(description="Contour / pixel area in pixels squared")
    center_x: float = Field(description="Centroid horizontal coordinate (u)")
    center_y: float = Field(description="Centroid vertical coordinate (v)")
    mean_intensity: float = Field(description="Mean 8-bit pixel intensity within candidate region")
    max_intensity: float = Field(description="Maximum 8-bit pixel intensity within candidate region")
    aspect_ratio: float = Field(description="Aspect ratio (width / height)")
    circularity: float = Field(default=0.0, description="Shape compactness / circularity 4*pi*area / perimeter^2")
    score: float = Field(description="Candidate ranking heuristic score")


class DetectionConfig(BaseModel):
    """
    Configuration parameters for Beacon Detection algorithms.
    """
    method: Literal["opencv", "mock", "yolo"] = Field(
        default="opencv",
        description="Active detection algorithm: 'opencv' (classical baseline), 'mock' (test stub), or 'yolo' (future AI)"
    )
    threshold: int = Field(
        default=40,
        ge=0,
        le=255,
        description="Brightness intensity threshold [0, 255] for binarization"
    )
    use_otsu: bool = Field(
        default=False,
        description="Whether to use Otsu automatic binarization thresholding"
    )
    use_adaptive: bool = Field(
        default=True,
        description="Whether to use statistical background noise adaptive thresholding"
    )
    k_sigma: float = Field(
        default=3.5,
        ge=0.5,
        le=15.0,
        description="Adaptive threshold multiplier: Threshold = mu_bg + k_sigma * sigma_bg"
    )
    min_area: float = Field(
        default=3.0,
        ge=0.0,
        description="Minimum candidate contour area in pixels"
    )
    max_area: float = Field(
        default=5000.0,
        ge=1.0,
        description="Maximum candidate contour area in pixels"
    )
    min_brightness: float = Field(
        default=25.0,
        ge=0.0,
        le=255.0,
        description="Minimum peak pixel brightness required for candidate acceptance"
    )
    min_confidence: float = Field(
        default=0.40,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold [0, 1] to declare a positive detection"
    )
    min_aspect_ratio: float = Field(
        default=0.20,
        ge=0.05,
        le=1.0,
        description="Minimum acceptable aspect ratio (width / height)"
    )
    max_aspect_ratio: float = Field(
        default=5.0,
        ge=1.0,
        le=20.0,
        description="Maximum acceptable aspect ratio (width / height)"
    )
    blur_kernel: int = Field(
        default=3,
        ge=0,
        le=31,
        description="Gaussian blur preprocessing kernel diameter (must be odd, 0 = disabled)"
    )
    morphology_enabled: bool = Field(
        default=True,
        description="Whether morphological closing/cleanup is enabled"
    )
    include_candidates: bool = Field(
        default=False,
        description="Whether to include full candidate diagnostic list in API result"
    )

    model_config = ConfigDict(validate_assignment=True)

    @model_validator(mode="after")
    def validate_constraints(self) -> DetectionConfig:
        if self.max_area <= self.min_area:
            raise ValueError(f"max_area ({self.max_area}) must be strictly greater than min_area ({self.min_area})")
        if self.blur_kernel > 0 and self.blur_kernel % 2 == 0:
            raise ValueError(f"blur_kernel ({self.blur_kernel}) must be an odd integer (e.g. 3, 5, 7) or 0 to disable")
        return self


class DetectionResult(BaseModel):
    """
    Stable detection output contract. Consumed by downstream Kalman Tracker and UI.
    """
    detected: bool = Field(description="True if optical beacon was successfully identified and localized")
    center_x: Optional[float] = Field(default=None, description="Detected horizontal image coordinate u (pixels)")
    center_y: Optional[float] = Field(default=None, description="Detected vertical image coordinate v (pixels)")
    u: Optional[float] = Field(default=None, description="Alias for center_x matching camera focal plane coordinates")
    v: Optional[float] = Field(default=None, description="Alias for center_y matching camera focal plane coordinates")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Normalized detection confidence score [0.0, 1.0]")
    bbox: Optional[BoundingBox] = Field(default=None, description="Bounding box enclosing the detected beacon spot")
    candidate_count: int = Field(default=0, ge=0, description="Total number of valid candidates identified in frame")
    selected_candidate: Optional[int] = Field(default=None, description="Index of selected top-ranked candidate")
    candidates: Optional[List[CandidateInfo]] = Field(default=None, description="Optional diagnostic list of all candidate blobs")
    method: str = Field(default="opencv", description="Detector algorithm that produced this result")
    timestamp: float = Field(default=0.0, ge=0.0, description="Simulation timestamp in seconds")
    processing_time_ms: float = Field(default=0.0, ge=0.0, description="Detector execution latency in milliseconds")
    message: str = Field(default="", description="Diagnostic status or rejection reason")

    @model_validator(mode="after")
    def sync_coordinates(self) -> DetectionResult:
        if self.detected:
            if self.center_x is not None and self.u is None:
                self.u = self.center_x
            elif self.u is not None and self.center_x is None:
                self.center_x = self.u
            if self.center_y is not None and self.v is None:
                self.v = self.center_y
            elif self.v is not None and self.center_y is None:
                self.center_y = self.v
        return self


class DetectionStatus(BaseModel):
    """
    Lifecycle status, active configuration, and cumulative statistics of the detection service.
    """
    initialized: bool = Field(description="Whether detection engine is initialized")
    method: str = Field(description="Active detection method ('opencv', 'mock', 'yolo')")
    config: DetectionConfig = Field(description="Active detection configuration parameters")
    total_frames_processed: int = Field(default=0, description="Total frames processed since initialization", ge=0)
    successful_detections: int = Field(default=0, description="Total positive detections", ge=0)
    detection_rate_pct: float = Field(default=0.0, description="Detection success percentage (0-100%)", ge=0.0, le=100.0)
    latest_detected: bool = Field(default=False, description="Whether beacon was detected in latest frame")
    current_timestamp: float = Field(default=0.0, description="Current simulation timestamp in seconds")


class DetectionTelemetry(BaseModel):
    """
    Real-time telemetry packet for HUD displays and diagnostic monitors.
    """
    timestamp: float = Field(description="Simulation timestamp in seconds")
    detected: bool = Field(description="Detection flag")
    center_x: Optional[float] = Field(default=None, description="Horizontal center (px)")
    center_y: Optional[float] = Field(default=None, description="Vertical center (px)")
    confidence: float = Field(description="Confidence score [0, 1]")
    candidate_count: int = Field(description="Count of candidate blobs")
    processing_time_ms: float = Field(description="Execution latency (ms)")
    method: str = Field(description="Detector method name")
    bbox_width: Optional[int] = Field(default=None, description="Detected box width (px)")
    bbox_height: Optional[int] = Field(default=None, description="Detected box height (px)")
    status_text: str = Field(description="Human-readable status banner")
