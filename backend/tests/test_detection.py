"""
Unit and Integration Tests for Beacon Detection Service and Preprocessing.
Team PHARO — SIH26169
"""

import numpy as np
import pytest

from app.detection.models import (
    BoundingBox,
    CandidateInfo,
    DetectionConfig,
    DetectionResult,
    DetectionStatus,
    DetectionTelemetry,
)
from app.detection.mock_detector import MockBeaconDetector
from app.detection.opencv_detector import OpenCVBeaconDetector
from app.detection.preprocessing import (
    validate_image_input,
    to_grayscale,
    apply_blur,
    preprocess_image,
)
from app.detection.service import detection_service
from app.world.service import world_service
from app.camera.service import camera_service
from app.disturbance.service import disturbance_service
from app.scenario.models import DisturbanceConfig


def test_mock_detector_positive():
    detector = MockBeaconDetector(mock_detected=True, mock_center_x=320.5, mock_center_y=239.5, mock_confidence=0.92)
    res = detector.detect(np.zeros((480, 640), dtype=np.uint8), timestamp=1.5)

    assert res.detected is True
    assert res.center_x == 320.5
    assert res.center_y == 239.5
    assert res.confidence == 0.92
    assert res.timestamp == 1.5
    assert res.method == "mock"


def test_mock_detector_negative():
    detector = MockBeaconDetector(mock_detected=False)
    res = detector.detect(np.zeros((480, 640), dtype=np.uint8))

    assert res.detected is False
    assert res.center_x is None
    assert res.center_y is None
    assert res.bbox is None
    assert res.confidence == 0.0


def test_preprocessing_validation():
    valid, msg = validate_image_input(np.zeros((100, 100), dtype=np.uint8))
    assert valid is True

    valid, msg = validate_image_input(None)
    assert valid is False

    valid, msg = validate_image_input(np.zeros((0, 0), dtype=np.uint8))
    assert valid is False


def test_preprocessing_to_grayscale():
    # 2D uint8
    img2d = np.full((50, 50), 128, dtype=np.uint8)
    assert to_grayscale(img2d).shape == (50, 50)

    # 3D RGB/BGR (50, 50, 3)
    img3d = np.full((50, 50, 3), 128, dtype=np.uint8)
    gray3d = to_grayscale(img3d)
    assert gray3d.shape == (50, 50)
    assert gray3d.dtype == np.uint8


def test_preprocessing_blur():
    img = np.zeros((50, 50), dtype=np.uint8)
    img[25, 25] = 255
    blurred = apply_blur(img, kernel_size=5)
    assert blurred.shape == (50, 50)
    assert blurred[25, 25] < 255  # Peak dispersed
    assert blurred[25, 26] > 0    # Spread to neighbors


def test_detection_models_validation():
    bbox = BoundingBox(x=10, y=20, width=30, height=40)
    assert bbox.x_min == 10
    assert bbox.y_min == 20
    assert bbox.x_max == 39
    assert bbox.y_max == 59
    assert bbox.center_x == 10 + 29 / 2.0
    assert bbox.center_y == 20 + 39 / 2.0

    res = DetectionResult(detected=True, center_x=100.0, center_y=150.0, confidence=0.85)
    assert res.u == 100.0
    assert res.v == 150.0


def test_detection_service_lifecycle():
    status = detection_service.initialize_from_scenario()
    assert status.initialized is True
    assert status.total_frames_processed >= 1

    res = detection_service.process_frame()
    assert isinstance(res, DetectionResult)

    tel = detection_service.get_telemetry()
    assert isinstance(tel, DetectionTelemetry)


def test_detection_service_with_camera_and_disturbance():
    # Reset world to initial state
    world_service.reset_world()
    camera_service.reset_camera()
    disturbance_service.reset()
    detection_service.reset()

    # Initial frame: beacon is in front of camera at center
    res = detection_service.process_frame()
    assert res.detected is True
    assert abs(res.center_x - 320.0) < 5.0
    assert abs(res.center_y - 240.0) < 5.0
    assert res.confidence >= 0.50


def test_detection_service_during_dropout():
    # Configure disturbance with 100% dropout probability
    dist_cfg = DisturbanceConfig(
        severity="medium",
        dropout_enabled=True,
        dropout_probability=1.0,
        dropout_duration=5.0,
        random_seed=42,
    )
    disturbance_service.set_config(dist_cfg)
    disturbance_service.reset()
    disturbance_service.process_frame()

    # Run detection on dropped-out frame
    res = detection_service.process_frame()
    assert res.detected is False
    assert res.center_x is None
    assert res.center_y is None


def test_detection_overlay_image_png():
    # Restore normal disturbance
    disturbance_service.set_config(DisturbanceConfig())
    disturbance_service.process_frame()
    detection_service.process_frame()

    png_bytes = detection_service.get_overlay_image_png()
    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 100
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")
