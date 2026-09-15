"""
Unit Tests for AlignmentService Layer, Tracking State Handling, Telemetry, and Overlays.
Team PHARO — SIH26169
"""

import pytest
from app.tracking.models import TrackingResult, TrackingStatus
from app.error.models import AlignmentConfig, ErrorStatus, ErrorSource
from app.error.service import AlignmentService


@pytest.fixture
def clean_error_service():
    service = AlignmentService()
    service.reset()
    return service


def test_service_initial_state(clean_error_service):
    """Verify service starts in INVALID state after reset."""
    status = clean_error_service.get_status()
    assert status.status == ErrorStatus.INVALID
    assert status.total_calculations == 0
    assert status.aligned_frames_count == 0


def test_service_process_filtered_tracking(clean_error_service):
    """Verify normal TRACKING result produces FILTERED alignment error."""
    track = TrackingResult(
        timestamp=1.0,
        initialized=True,
        tracking=True,
        status=TrackingStatus.TRACKING,
        position_x=340.0,
        position_y=230.0,
        confidence=0.92,
    )
    res = clean_error_service.process_tracking(track)

    assert res.valid is True
    assert res.source == ErrorSource.FILTERED
    assert res.status in [ErrorStatus.VALID, ErrorStatus.ALIGNED]
    assert res.pixel_error_x == 20.0
    assert res.pixel_error_y == -10.0
    assert res.tracking_confidence == 0.92


def test_service_process_predicting_coasting(clean_error_service):
    """Verify PREDICTING state uses lead predicted position and marks source as PREDICTED."""
    track = TrackingResult(
        timestamp=2.0,
        initialized=True,
        tracking=True,
        status=TrackingStatus.PREDICTING,
        position_x=None,
        position_y=None,
        predicted_x=360.0,
        predicted_y=250.0,
        prediction_valid=True,
        confidence=0.60,
    )
    res = clean_error_service.process_tracking(track)

    assert res.valid is True
    assert res.source == ErrorSource.PREDICTED
    assert res.pixel_error_x == 40.0
    assert res.pixel_error_y == 10.0


def test_service_process_lost_tracking(clean_error_service):
    """Verify LOST tracking result produces INVALID error with source NONE."""
    track = TrackingResult(
        timestamp=3.0,
        initialized=True,
        tracking=False,
        status=TrackingStatus.LOST,
        position_x=None,
        position_y=None,
        predicted_x=None,
        predicted_y=None,
        prediction_valid=False,
        confidence=0.0,
    )
    res = clean_error_service.process_tracking(track)

    assert res.valid is False
    assert res.status == ErrorStatus.INVALID
    assert res.source == ErrorSource.NONE
    assert res.pixel_error_x is None


def test_service_telemetry_and_overlay(clean_error_service):
    """Verify telemetry packet and PNG overlay rendering."""
    track = TrackingResult(
        timestamp=1.5,
        initialized=True,
        tracking=True,
        status=TrackingStatus.TRACKING,
        position_x=322.0,
        position_y=241.0,
        confidence=0.95,
    )
    clean_error_service.process_tracking(track)

    telemetry = clean_error_service.get_telemetry()
    assert telemetry.valid is True
    assert telemetry.center_x == 320.0
    assert telemetry.center_y == 240.0
    assert telemetry.pixel_error_x == 2.0
    assert telemetry.pixel_error_y == 1.0
    assert "ALIGNED" in telemetry.status_text or "ERROR" in telemetry.status_text

    overlay_png = clean_error_service.get_overlay_image_png()
    assert isinstance(overlay_png, bytes)
    assert len(overlay_png) > 100
    assert overlay_png[:8] == b"\x89PNG\r\n\x1a\n"
