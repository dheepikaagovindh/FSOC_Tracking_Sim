"""
Beacon Detection Simulation Package (Standalone Layer).
Team PHARO — SIH26169
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.detection.models import (
    BoundingBox,
    CandidateInfo,
    DetectionConfig,
    DetectionResult,
    DetectionStatus,
    DetectionTelemetry,
)
from app.detection.base import BaseDetector
from app.detection.opencv_detector import OpenCVBeaconDetector
from app.detection.mock_detector import MockBeaconDetector
from app.detection.preprocessing import (
    validate_image_input,
    to_grayscale,
    apply_blur,
    preprocess_image,
)
from app.detection.service import DetectionService, detection_service

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
