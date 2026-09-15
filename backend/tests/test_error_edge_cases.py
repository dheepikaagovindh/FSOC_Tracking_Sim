"""
Unit Tests for Error Calculation Edge Cases, Variable Geometries, and Robustness.
Team PHARO — SIH26169
"""

import math
import pytest

from app.error.models import AlignmentConfig, ErrorStatus, ErrorSource
from app.error.calculator import ErrorCalculator


def test_nan_and_inf_target_coordinates():
    """Verify NaN and Inf coordinates are rejected as INVALID without throwing."""
    cfg = AlignmentConfig()

    res_nan = ErrorCalculator.compute_error(
        target_x=float("nan"), target_y=240.0, source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=30.0, vfov_deg=22.5, config=cfg,
    )
    assert res_nan.valid is False
    assert res_nan.status == ErrorStatus.INVALID

    res_inf = ErrorCalculator.compute_error(
        target_x=320.0, target_y=float("inf"), source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=30.0, vfov_deg=22.5, config=cfg,
    )
    assert res_inf.valid is False
    assert res_inf.status == ErrorStatus.INVALID


def test_variable_camera_resolution():
    """Verify optical center and normalized errors adapt dynamically to different resolutions."""
    cfg = AlignmentConfig()
    
    # 1280x720 (HD)
    res_hd = ErrorCalculator.compute_error(
        target_x=640.0, target_y=360.0, source=ErrorSource.FILTERED,
        width=1280, height=720, hfov_deg=45.0, vfov_deg=28.0, config=cfg,
    )
    assert res_hd.center_x == 640.0
    assert res_hd.center_y == 360.0
    assert res_hd.pixel_error_x == 0.0
    assert res_hd.pixel_error_y == 0.0
    assert res_hd.aligned is True

    # Offset of +64px on 1280 width => normalized error = 64 / 640 = +0.10
    res_offset = ErrorCalculator.compute_error(
        target_x=704.0, target_y=360.0, source=ErrorSource.FILTERED,
        width=1280, height=720, hfov_deg=45.0, vfov_deg=28.0, config=cfg,
    )
    assert res_offset.pixel_error_x == 64.0
    assert pytest.approx(res_offset.normalized_error_x, abs=0.001) == 0.10


def test_variable_camera_fov_scaling():
    """Verify angular error changes inversely with focal length when FOV changes."""
    cfg = AlignmentConfig()
    # 50px offset on narrow 10° FOV vs wide 60° FOV
    res_narrow = ErrorCalculator.compute_error(
        target_x=370.0, target_y=240.0, source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=10.0, vfov_deg=7.5, config=cfg,
    )
    res_wide = ErrorCalculator.compute_error(
        target_x=370.0, target_y=240.0, source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=60.0, vfov_deg=45.0, config=cfg,
    )

    # On a wider FOV, a 50px offset subtends a LARGER angle
    assert res_wide.angular_error_x_deg > res_narrow.angular_error_x_deg


def test_out_of_bounds_target_coordinates():
    """Verify beacon flying outside camera focal plane is calculated without clamping."""
    cfg = AlignmentConfig()
    res_oob = ErrorCalculator.compute_error(
        target_x=800.0, target_y=600.0, source=ErrorSource.PREDICTED,
        width=640, height=480, hfov_deg=30.0, vfov_deg=22.5, config=cfg,
    )

    assert res_oob.valid is True
    assert res_oob.target_x == 800.0
    assert res_oob.target_y == 600.0
    assert res_oob.pixel_error_x == 800.0 - 320.0
    assert res_oob.pixel_error_y == 600.0 - 240.0
    assert res_oob.normalized_error_x > 1.0


def test_zero_dt_error_rate_safety():
    """Verify identical timestamps (dt=0) do not cause ZeroDivisionError."""
    cfg = AlignmentConfig()
    prev_err = (10.0, 5.0, 1.0)

    res = ErrorCalculator.compute_error(
        target_x=340.0, target_y=250.0, source=ErrorSource.FILTERED,
        width=640, height=480, hfov_deg=30.0, vfov_deg=22.5, config=cfg,
        timestamp=1.0,  # Same timestamp => dt = 0
        prev_error=prev_err,
    )

    assert res.valid is True
    assert res.error_rate_x is None
    assert res.error_rate_y is None
