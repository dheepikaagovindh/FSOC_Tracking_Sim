"""
Unit Tests for OpenCV Beacon Detector Engine.
Team PHARO — SIH26169
"""

import math
import cv2
import numpy as np
import pytest

from app.detection.models import DetectionConfig, DetectionResult, BoundingBox
from app.detection.opencv_detector import OpenCVBeaconDetector
from app.detection.preprocessing import preprocess_image, validate_image_input


def create_spot_image(
    width: int = 640,
    height: int = 480,
    u: float = 320.0,
    v: float = 240.0,
    radius: float = 4.0,
    peak_intensity: float = 255.0,
) -> np.ndarray:
    """Helper to render synthetic Gaussian beacon spot on black background."""
    img = np.zeros((height, width), dtype=np.uint8)
    y_coords, x_coords = np.ogrid[0:height, 0:width]
    dist_sq = (x_coords - u) ** 2 + (y_coords - v) ** 2
    sigma = max(1.0, radius / 2.0)
    spot = peak_intensity * np.exp(-0.5 * dist_sq / (sigma ** 2))
    return np.clip(spot, 0, 255).astype(np.uint8)


def test_detector_initialization():
    detector = OpenCVBeaconDetector()
    assert detector.config.method == "opencv"
    assert detector.config.threshold == 40


def test_clean_center_beacon_detection():
    image = create_spot_image(u=320.0, v=240.0, radius=5.0, peak_intensity=255.0)
    detector = OpenCVBeaconDetector()
    result = detector.detect(image)

    assert result.detected is True
    assert result.center_x is not None and abs(result.center_x - 320.0) < 1.0
    assert result.center_y is not None and abs(result.center_y - 240.0) < 1.0
    assert result.u == result.center_x
    assert result.v == result.center_y
    assert result.confidence >= 0.70
    assert result.bbox is not None
    assert result.bbox.width >= 3
    assert result.bbox.height >= 3
    assert result.candidate_count >= 1
    assert result.method == "opencv"
    assert result.processing_time_ms >= 0.0


def test_off_center_beacon_detection():
    image = create_spot_image(u=400.0, v=300.0, radius=4.0, peak_intensity=240.0)
    detector = OpenCVBeaconDetector()
    result = detector.detect(image)

    assert result.detected is True
    assert result.center_x is not None and abs(result.center_x - 400.0) < 1.0
    assert result.center_y is not None and abs(result.center_y - 300.0) < 1.0
    assert result.bbox.x <= 400 <= result.bbox.x + result.bbox.width
    assert result.bbox.y <= 300 <= result.bbox.y + result.bbox.height


def test_subpixel_coordinate_accuracy():
    image = create_spot_image(u=150.35, v=200.75, radius=4.5, peak_intensity=250.0)
    detector = OpenCVBeaconDetector()
    result = detector.detect(image)

    assert result.detected is True
    assert abs(result.center_x - 150.35) < 0.20
    assert abs(result.center_y - 200.75) < 0.20


def test_bounding_box_accuracy():
    image = create_spot_image(u=320.0, v=240.0, radius=6.0, peak_intensity=255.0)
    detector = OpenCVBeaconDetector()
    result = detector.detect(image)

    assert result.detected is True
    bbox = result.bbox
    assert isinstance(bbox, BoundingBox)
    assert bbox.x < 320 < bbox.x + bbox.width
    assert bbox.y < 240 < bbox.y + bbox.height
    assert 4 <= bbox.width <= 30
    assert 4 <= bbox.height <= 30


def test_confidence_range():
    image = create_spot_image(u=320.0, v=240.0, radius=4.0, peak_intensity=255.0)
    detector = OpenCVBeaconDetector()
    result = detector.detect(image)
    assert 0.0 <= result.confidence <= 1.0


def test_no_beacon_blank_image():
    blank = np.zeros((480, 640), dtype=np.uint8)
    detector = OpenCVBeaconDetector()
    result = detector.detect(blank)

    assert result.detected is False
    assert result.center_x is None
    assert result.center_y is None
    assert result.bbox is None
    assert result.confidence == 0.0
    assert result.candidate_count == 0


def test_noisy_image_detection():
    clean = create_spot_image(u=320.0, v=240.0, radius=5.0, peak_intensity=255.0)
    np.random.seed(42)
    noise = np.random.normal(loc=15.0, scale=8.0, size=(480, 640)).clip(0, 255).astype(np.uint8)
    noisy = np.clip(clean.astype(np.int32) + noise, 0, 255).astype(np.uint8)

    detector = OpenCVBeaconDetector()
    result = detector.detect(noisy)

    assert result.detected is True
    assert abs(result.center_x - 320.0) < 1.0
    assert abs(result.center_y - 240.0) < 1.0
    assert 0.0 <= result.confidence <= 1.0


def test_blurred_image_detection():
    clean = create_spot_image(u=320.0, v=240.0, radius=3.0, peak_intensity=255.0)
    blurred = cv2.GaussianBlur(clean, (15, 15), 3.0)

    detector = OpenCVBeaconDetector()
    result = detector.detect(blurred)

    assert result.detected is True
    assert abs(result.center_x - 320.0) < 1.0
    assert abs(result.center_y - 240.0) < 1.0


def test_multiple_bright_objects_selection():
    img = np.zeros((480, 640), dtype=np.uint8)
    # Bright primary beacon at (320, 240)
    img = np.maximum(img, create_spot_image(u=320.0, v=240.0, radius=5.0, peak_intensity=255.0))
    # Dimmer secondary spot at (100, 100)
    img = np.maximum(img, create_spot_image(u=100.0, v=100.0, radius=3.0, peak_intensity=80.0))
    # Dimmer third spot at (500, 400)
    img = np.maximum(img, create_spot_image(u=500.0, v=400.0, radius=2.0, peak_intensity=70.0))

    cfg = DetectionConfig(include_candidates=True)
    detector = OpenCVBeaconDetector(cfg)
    result = detector.detect(img)

    assert result.detected is True
    # Should choose the brightest / highest PNR beacon at (320, 240)
    assert abs(result.center_x - 320.0) < 1.0
    assert abs(result.center_y - 240.0) < 1.0
    assert result.candidate_count >= 2
    assert result.candidates is not None
    assert len(result.candidates) >= 2


def test_candidate_filtering_min_area():
    # 1 single bright pixel
    img = np.zeros((480, 640), dtype=np.uint8)
    img[240, 320] = 255

    cfg = DetectionConfig(min_area=5.0)
    detector = OpenCVBeaconDetector(cfg)
    result = detector.detect(img)
    # 1 pixel area = 1.0 < min_area=5.0 -> filtered out
    assert result.detected is False


def test_candidate_filtering_max_area():
    # Large bright block 200x200
    img = np.zeros((480, 640), dtype=np.uint8)
    img[100:300, 100:300] = 255

    cfg = DetectionConfig(max_area=1000.0)
    detector = OpenCVBeaconDetector(cfg)
    result = detector.detect(img)
    # Area = 40000 > max_area=1000 -> filtered out
    assert result.detected is False


def test_candidate_filtering_min_brightness():
    # Very dim spot peak=40
    img = create_spot_image(u=320.0, v=240.0, radius=4.0, peak_intensity=40.0)

    cfg = DetectionConfig(min_brightness=100.0)
    detector = OpenCVBeaconDetector(cfg)
    result = detector.detect(img)
    assert result.detected is False


def test_candidate_filtering_aspect_ratio():
    # Very thin horizontal line: 100x2
    img = np.zeros((480, 640), dtype=np.uint8)
    img[240:242, 200:300] = 255

    cfg = DetectionConfig(max_aspect_ratio=3.0)
    detector = OpenCVBeaconDetector(cfg)
    result = detector.detect(img)
    # Aspect ratio = 100/2 = 50 > max_aspect_ratio=3 -> filtered out
    assert result.detected is False


def test_fixed_threshold_vs_otsu_vs_adaptive():
    img = create_spot_image(u=320.0, v=240.0, radius=4.0, peak_intensity=255.0)

    for mode in [{"use_otsu": True}, {"use_adaptive": True}, {"use_adaptive": False, "use_otsu": False, "threshold": 50}]:
        cfg = DetectionConfig(**mode)
        detector = OpenCVBeaconDetector(cfg)
        res = detector.detect(img)
        assert res.detected is True
        assert abs(res.center_x - 320.0) < 1.0


def test_invalid_config_validation():
    with pytest.raises(ValueError):
        DetectionConfig(min_area=100.0, max_area=50.0)

    with pytest.raises(ValueError):
        DetectionConfig(blur_kernel=4)  # Even number not allowed


def test_zero_area_or_empty_image_handling():
    detector = OpenCVBeaconDetector()
    res1 = detector.detect(None)
    assert res1.detected is False

    res2 = detector.detect(np.zeros((0, 0), dtype=np.uint8))
    assert res2.detected is False


def test_processing_time_recorded():
    img = create_spot_image(u=320.0, v=240.0, radius=4.0, peak_intensity=255.0)
    detector = OpenCVBeaconDetector()
    res = detector.detect(img)
    assert res.processing_time_ms >= 0.0


def test_deterministic_detection():
    img = create_spot_image(u=320.0, v=240.0, radius=4.0, peak_intensity=255.0)
    detector = OpenCVBeaconDetector()
    res1 = detector.detect(img)
    res2 = detector.detect(img)
    assert res1.detected == res2.detected
    assert res1.center_x == res2.center_x
    assert res1.center_y == res2.center_y
    assert res1.confidence == res2.confidence
