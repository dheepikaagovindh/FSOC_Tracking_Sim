"""
Beacon Detection Module (Module 5).
Team PHARO — SIH26169

Public exports for app.detection.
"""

from .models import (
    BoundingBox,
    CandidateInfo,
    DetectionConfig,
    DetectionResult,
    DetectionStatus,
    DetectionTelemetry,
)
from .base import BaseDetector
from .opencv_detector import OpenCVBeaconDetector
from .mock_detector import MockBeaconDetector
from .preprocessing import (
    validate_image_input,
    to_grayscale,
    apply_blur,
    preprocess_image,
)
from .service import DetectionService, detection_service

__all__ = [
    "BoundingBox",
    "CandidateInfo",
    "DetectionConfig",
    "DetectionResult",
    "DetectionStatus",
    "DetectionTelemetry",
    "BaseDetector",
    "OpenCVBeaconDetector",
    "MockBeaconDetector",
    "validate_image_input",
    "to_grayscale",
    "apply_blur",
    "preprocess_image",
    "DetectionService",
    "detection_service",
]
