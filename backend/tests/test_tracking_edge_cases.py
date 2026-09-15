"""
Unit Tests for Tracking Edge Cases, Corrupt Inputs, Variable dt, and Robustness.
Team PHARO — SIH26169
"""

import math
import numpy as np
import pytest

from app.detection.models import DetectionResult
from app.tracking.models import TrackingConfig, TrackingStatus
from app.tracking.service import TrackingService


@pytest.fixture
def edge_service():
    service = TrackingService()
    service.reset()
    return service


def test_malformed_nan_coordinates(edge_service):
    """Verify NaN coordinates in detection do not crash service and are safely rejected."""
    # Attempt init with NaN
    det_nan = DetectionResult(
        detected=True,
        center_x=float("nan"),
        center_y=240.0,
        confidence=0.9,
        timestamp=1.0,
    )
    res = edge_service.process_detection(det_nan)
    assert res.status == TrackingStatus.UNINITIALIZED
    assert res.initialized is False


def test_malformed_inf_coordinates(edge_service):
    """Verify Inf coordinates are rejected."""
    det_inf = DetectionResult(
        detected=True,
        center_x=320.0,
        center_y=float("inf"),
        confidence=0.9,
        timestamp=1.0,
    )
    res = edge_service.process_detection(det_inf)
    assert res.status == TrackingStatus.UNINITIALIZED


def test_low_confidence_rejection(edge_service):
    """Verify detections below min_detection_confidence are treated as misses."""
    cfg = TrackingConfig(min_detection_confidence=0.40)
    edge_service.set_config(cfg)

    # Initial valid detection
    edge_service.process_detection(
        DetectionResult(detected=True, center_x=320.0, center_y=240.0, confidence=0.85, timestamp=0.1)
    )

    # Low-confidence detection (0.15 < 0.40)
    res_low = edge_service.process_detection(
        DetectionResult(detected=True, center_x=330.0, center_y=245.0, confidence=0.15, timestamp=0.2)
    )
    assert res_low.status == TrackingStatus.PREDICTING
    assert res_low.consecutive_misses == 1


def test_non_monotonic_and_zero_dt(edge_service):
    """Verify non-monotonic or identical timestamps fallback to safe dt without crashing."""
    # Init at t=1.0
    edge_service.process_detection(
        DetectionResult(detected=True, center_x=300.0, center_y=200.0, confidence=0.9, timestamp=1.0)
    )

    # Same timestamp t=1.0 (dt=0)
    res_zero = edge_service.process_detection(
        DetectionResult(detected=True, center_x=301.0, center_y=200.0, confidence=0.9, timestamp=1.0)
    )
    assert res_zero.status == TrackingStatus.TRACKING
    assert math.isfinite(res_zero.position_x)

    # Backward timestamp t=0.5 (dt < 0)
    res_back = edge_service.process_detection(
        DetectionResult(detected=True, center_x=302.0, center_y=200.0, confidence=0.9, timestamp=0.5)
    )
    assert res_back.status == TrackingStatus.TRACKING
    assert math.isfinite(res_back.position_x)


def test_large_dt_step_clamping(edge_service):
    """Verify massive timestamp jumps are safely clamped to max_dt."""
    edge_service.process_detection(
        DetectionResult(detected=True, center_x=300.0, center_y=200.0, confidence=0.9, timestamp=1.0)
    )

    # Jump ahead by 100 seconds
    res_jump = edge_service.process_detection(
        DetectionResult(detected=True, center_x=310.0, center_y=205.0, confidence=0.9, timestamp=101.0)
    )
    assert res_jump.status == TrackingStatus.TRACKING
    assert math.isfinite(res_jump.position_x)
    assert math.isfinite(res_jump.velocity_x)


def test_out_of_bounds_target_tracking(edge_service):
    """Verify target moving outside camera image bounds [0, 640] x [0, 480] is tracked cleanly."""
    edge_service.process_detection(
        DetectionResult(detected=True, center_x=635.0, center_y=240.0, confidence=0.85, timestamp=1.0)
    )

    # Move outside focal plane
    res_oob = edge_service.process_detection(
        DetectionResult(detected=True, center_x=660.0, center_y=240.0, confidence=0.80, timestamp=1.1)
    )
    assert res_oob.status == TrackingStatus.TRACKING
    assert res_oob.position_x > 640.0
