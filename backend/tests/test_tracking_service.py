"""
Unit Tests for TrackingService Layer, Coasting, State Lifecycle, and Telemetry.
Team PHARO — SIH26169
"""

import pytest
from app.detection.models import DetectionResult, BoundingBox
from app.tracking.models import TrackingConfig, TrackingStatus
from app.tracking.service import TrackingService


@pytest.fixture
def clean_service():
    service = TrackingService()
    service.reset()
    return service


def test_service_initial_state(clean_service):
    """Verify service starts in UNINITIALIZED state after reset."""
    status = clean_service.get_status()
    assert status.status == TrackingStatus.UNINITIALIZED
    assert status.tracking_hits == 0
    assert status.tracking_misses == 0


def test_service_first_detection(clean_service):
    """Verify first positive detection initializes tracking state."""
    det = DetectionResult(
        detected=True,
        center_x=320.0,
        center_y=240.0,
        confidence=0.90,
        timestamp=0.1,
    )
    res = clean_service.process_detection(det)

    assert res.status == TrackingStatus.TRACKING
    assert res.initialized is True
    assert res.tracking is True
    assert res.position_x is not None
    assert pytest.approx(res.position_x, abs=0.1) == 320.0
    assert pytest.approx(res.position_y, abs=0.1) == 240.0
    assert res.consecutive_hits == 1
    assert res.consecutive_misses == 0
    assert res.confidence > 0.4


def test_temporary_dropout_and_coasting(clean_service):
    """Verify tracker coasts in PREDICTING mode during temporary measurement dropout."""
    cfg = TrackingConfig(max_missed_frames=5)
    clean_service.set_config(cfg)

    # Frame 1: Hit
    clean_service.process_detection(
        DetectionResult(detected=True, center_x=100.0, center_y=100.0, confidence=0.85, timestamp=0.1)
    )
    # Frame 2: Hit
    res2 = clean_service.process_detection(
        DetectionResult(detected=True, center_x=105.0, center_y=100.0, confidence=0.85, timestamp=0.2)
    )
    assert res2.status == TrackingStatus.TRACKING
    assert res2.consecutive_hits == 2

    # Frame 3: Miss (Dropout)
    res3 = clean_service.process_detection(
        DetectionResult(detected=False, confidence=0.0, timestamp=0.3)
    )
    assert res3.status == TrackingStatus.PREDICTING
    assert res3.tracking is True
    assert res3.prediction_valid is True
    assert res3.consecutive_misses == 1
    assert res3.consecutive_hits == 0
    # Coasting should predict position along horizontal velocity
    assert res3.position_x is not None
    assert res3.position_x > 100.0

    # Frame 4: Miss (Dropout)
    res4 = clean_service.process_detection(
        DetectionResult(detected=False, confidence=0.0, timestamp=0.4)
    )
    assert res4.status == TrackingStatus.PREDICTING
    assert res4.consecutive_misses == 2
    # Confidence should decay
    assert res4.confidence < res3.confidence

    # Frame 5: Recovery (Detection returns)
    res5 = clean_service.process_detection(
        DetectionResult(detected=True, center_x=120.0, center_y=100.0, confidence=0.92, timestamp=0.5)
    )
    assert res5.status == TrackingStatus.TRACKING
    assert res5.consecutive_hits == 1
    assert res5.consecutive_misses == 0
    assert res5.confidence > res4.confidence


def test_prolonged_dropout_track_loss(clean_service):
    """Verify track transitions to LOST after exceeding max_missed_frames."""
    cfg = TrackingConfig(max_missed_frames=3)
    clean_service.set_config(cfg)

    # Initialize tracker
    clean_service.process_detection(
        DetectionResult(detected=True, center_x=300.0, center_y=200.0, confidence=0.8, timestamp=0.1)
    )

    # 3 Misses -> PREDICTING
    for i in range(1, 4):
        res = clean_service.process_detection(
            DetectionResult(detected=False, confidence=0.0, timestamp=0.1 + 0.1 * i)
        )
        assert res.status == TrackingStatus.PREDICTING
        assert res.tracking is True

    # 4th Miss -> LOST
    res_lost = clean_service.process_detection(
        DetectionResult(detected=False, confidence=0.0, timestamp=0.5)
    )
    assert res_lost.status == TrackingStatus.LOST
    assert res_lost.tracking is False
    assert res_lost.prediction_valid is False
    assert res_lost.confidence == 0.0


def test_recovery_from_lost_state(clean_service):
    """Verify tracker can re-acquire and initialize when a valid detection arrives after track loss."""
    cfg = TrackingConfig(max_missed_frames=2)
    clean_service.set_config(cfg)

    # Initialize, then drop out until LOST
    clean_service.process_detection(
        DetectionResult(detected=True, center_x=200.0, center_y=200.0, confidence=0.8, timestamp=0.1)
    )
    clean_service.process_detection(DetectionResult(detected=False, timestamp=0.2))
    clean_service.process_detection(DetectionResult(detected=False, timestamp=0.3))
    res_lost = clean_service.process_detection(DetectionResult(detected=False, timestamp=0.4))
    assert res_lost.status == TrackingStatus.LOST

    # New detection arrives
    res_recovered = clean_service.process_detection(
        DetectionResult(detected=True, center_x=450.0, center_y=350.0, confidence=0.88, timestamp=1.0)
    )
    assert res_recovered.status == TrackingStatus.TRACKING
    assert res_recovered.tracking is True
    assert pytest.approx(res_recovered.position_x, abs=0.5) == 450.0
    assert pytest.approx(res_recovered.position_y, abs=0.5) == 350.0


def test_service_telemetry_and_overlay(clean_service):
    """Verify telemetry generation and PNG overlay rendering."""
    det = DetectionResult(
        detected=True,
        center_x=325.0,
        center_y=245.0,
        bbox=BoundingBox(x=320, y=240, width=10, height=10),
        confidence=0.95,
        timestamp=1.0,
    )
    clean_service.process_detection(det)

    telemetry = clean_service.get_telemetry()
    assert telemetry.status == "TRACKING"
    assert telemetry.tracking is True
    assert telemetry.measured_x == 325.0
    assert telemetry.filtered_x is not None
    assert telemetry.confidence > 0.0
    assert "TRACKING" in telemetry.status_text

    overlay_png = clean_service.get_overlay_image_png()
    assert isinstance(overlay_png, bytes)
    assert len(overlay_png) > 100
    # PNG signature check
    assert overlay_png[:8] == b"\x89PNG\r\n\x1a\n"
