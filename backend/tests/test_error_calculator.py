"""
Unit Tests for ErrorCalculator Optical Boresight Transformations and Alignment Metrics.
Team PHARO — SIH26169
"""

import math
import numpy as np
import pytest

from app.error.models import AlignmentConfig, ErrorStatus, ErrorSource
from app.error.calculator import ErrorCalculator


def test_centered_target():
    """Verify target at exact optical center produces zero pixel and angular errors and reports ALIGNED."""
    cfg = AlignmentConfig(angular_tolerance_deg=0.25, pixel_tolerance=5.0)
    res = ErrorCalculator.compute_error(
        target_x=320.0,
        target_y=240.0,
        source=ErrorSource.FILTERED,
        width=640,
        height=480,
        hfov_deg=30.0,
        vfov_deg=22.5,
        config=cfg,
        timestamp=1.0,
    )

    assert res.valid is True
    assert res.status == ErrorStatus.ALIGNED
    assert res.aligned is True
    assert res.radially_aligned is True
    assert res.pixel_error_x == 0.0
    assert res.pixel_error_y == 0.0
    assert res.pixel_error_magnitude == 0.0
    assert res.angular_error_x_deg == 0.0
    assert res.angular_error_y_deg == 0.0
    assert res.angular_error_magnitude_deg == 0.0
    assert res.normalized_error_x == 0.0
    assert res.normalized_error_y == 0.0


def test_four_quadrant_sign_conventions():
    """Verify standard quadrant sign conventions for pixel and angular errors."""
    cfg = AlignmentConfig()

    # 1. Target to the RIGHT of optical center
    r_right = ErrorCalculator.compute_error(
        target_x=350.0, target_y=240.0, source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=30.0, vfov_deg=22.5, config=cfg,
    )
    assert r_right.pixel_error_x == 30.0
    assert r_right.pixel_error_y == 0.0
    assert r_right.angular_error_x_deg > 0.0
    assert r_right.angular_error_y_deg == 0.0
    assert r_right.error_direction_deg == 0.0

    # 2. Target to the LEFT of optical center
    r_left = ErrorCalculator.compute_error(
        target_x=290.0, target_y=240.0, source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=30.0, vfov_deg=22.5, config=cfg,
    )
    assert r_left.pixel_error_x == -30.0
    assert r_left.pixel_error_y == 0.0
    assert r_left.angular_error_x_deg < 0.0
    assert r_left.angular_error_y_deg == 0.0
    assert abs(r_left.error_direction_deg) == 180.0

    # 3. Target BELOW optical center (+Y in pixel coordinates)
    r_below = ErrorCalculator.compute_error(
        target_x=320.0, target_y=260.0, source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=30.0, vfov_deg=22.5, config=cfg,
    )
    assert r_below.pixel_error_x == 0.0
    assert r_below.pixel_error_y == 20.0
    assert r_below.angular_error_x_deg == 0.0
    assert r_below.angular_error_y_deg > 0.0
    assert r_below.error_direction_deg == 90.0

    # 4. Target ABOVE optical center (-Y in pixel coordinates)
    r_above = ErrorCalculator.compute_error(
        target_x=320.0, target_y=220.0, source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=30.0, vfov_deg=22.5, config=cfg,
    )
    assert r_above.pixel_error_x == 0.0
    assert r_above.pixel_error_y == -20.0
    assert r_above.angular_error_x_deg == 0.0
    assert r_above.angular_error_y_deg < 0.0
    assert r_above.error_direction_deg == -90.0


def test_radial_and_normalized_errors():
    """Verify radial Euclidean error and normalized image coordinate scaling."""
    cfg = AlignmentConfig()
    res = ErrorCalculator.compute_error(
        target_x=350.0,
        target_y=220.0,
        source=ErrorSource.FILTERED,
        width=640,
        height=480,
        hfov_deg=30.0,
        vfov_deg=22.5,
        config=cfg,
    )

    # ex = 30, ey = -20 => mag = sqrt(900 + 400) = sqrt(1300) = 36.0555
    expected_mag = math.hypot(30.0, -20.0)
    assert pytest.approx(res.pixel_error_magnitude, abs=0.01) == expected_mag

    # normalized: 30 / 320 = 0.09375, -20 / 240 = -0.08333
    assert pytest.approx(res.normalized_error_x, abs=0.001) == 0.09375
    assert pytest.approx(res.normalized_error_y, abs=0.001) == -0.08333
    assert pytest.approx(res.normalized_error_magnitude, abs=0.001) == math.hypot(0.09375, -0.08333)


def test_pinhole_angular_conversion_accuracy():
    """Verify angular error calculation matches pinhole camera focal length geometry."""
    cfg = AlignmentConfig()
    width, height = 640, 480
    hfov_deg, vfov_deg = 30.0, 22.5

    fx, fy, cx, cy = ErrorCalculator.calculate_intrinsics(width, height, hfov_deg, vfov_deg)

    # Point at +30px offset
    res = ErrorCalculator.compute_error(
        target_x=cx + 30.0,
        target_y=cy - 20.0,
        source=ErrorSource.FILTERED,
        width=width,
        height=height,
        hfov_deg=hfov_deg,
        vfov_deg=vfov_deg,
        config=cfg,
    )

    expected_ang_x = math.degrees(math.atan2(30.0, fx))
    expected_ang_y = math.degrees(math.atan2(-20.0, fy))

    assert pytest.approx(res.angular_error_x_deg, abs=0.001) == expected_ang_x
    assert pytest.approx(res.angular_error_y_deg, abs=0.001) == expected_ang_y


def test_alignment_tolerance_thresholds():
    """Verify lock condition triggers inside tolerance and rejects outside tolerance."""
    cfg = AlignmentConfig(angular_tolerance_deg=0.50, use_angular_alignment=True)

    # Target yielding ~0.2° error => inside 0.5° tolerance => ALIGNED
    r_in = ErrorCalculator.compute_error(
        target_x=324.0, target_y=240.0, source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=30.0, vfov_deg=22.5, config=cfg,
    )
    assert r_in.status == ErrorStatus.ALIGNED
    assert r_in.aligned is True

    # Target yielding ~1.5° error => outside 0.5° tolerance => VALID
    r_out = ErrorCalculator.compute_error(
        target_x=360.0, target_y=240.0, source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=30.0, vfov_deg=22.5, config=cfg,
    )
    assert r_out.status == ErrorStatus.VALID
    assert r_out.aligned is False


def test_error_derivative_rates():
    """Verify calculation of delta error and time derivative rates."""
    cfg = AlignmentConfig()
    prev_err = (10.0, -5.0, 1.0)  # ex=10, ey=-5 at t=1.0s

    res = ErrorCalculator.compute_error(
        target_x=320.0 + 20.0,  # ex = 20
        target_y=240.0 - 15.0,  # ey = -15
        source=ErrorSource.FILTERED,
        width=640,
        height=480,
        hfov_deg=30.0,
        vfov_deg=22.5,
        config=cfg,
        timestamp=1.5,  # dt = 0.5s
        prev_error=prev_err,
    )

    # delta_x = 20 - 10 = 10px => rate_x = 10 / 0.5 = 20 px/s
    # delta_y = -15 - (-5) = -10px => rate_y = -10 / 0.5 = -20 px/s
    assert res.delta_error_x == 10.0
    assert res.delta_error_y == -10.0
    assert res.error_rate_x == 20.0
    assert res.error_rate_y == -20.0
