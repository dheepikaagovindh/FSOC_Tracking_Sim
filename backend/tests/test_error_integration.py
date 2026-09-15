"""
Full 6-Stage Simulation Pipeline Integration Test (World -> Camera -> Disturbance -> Detection -> Tracking -> Error).
Team PHARO — SIH26169
"""

import math
import pytest

from app.world.service import world_service
from app.camera.service import camera_service
from app.disturbance.service import disturbance_service
from app.detection.service import detection_service
from app.tracking.service import tracking_service
from app.error.service import alignment_service
from app.error.models import ErrorStatus


def test_full_6stage_pipeline_error_calculation():
    """
    Execute 30 frames of end-to-end simulation across all 6 modules:
    World -> Camera -> Disturbance -> Detection -> Tracking -> Error Calculation
    """
    # 1. Reset all services to default scenario
    world_service.reset_world()
    camera_service.reset_camera()
    disturbance_service.reset()
    detection_service.reset()
    tracking_service.reset()
    alignment_service.reset()

    dt = 1.0 / 30.0  # 30 FPS
    total_frames = 30
    error_results = []

    for frame_idx in range(total_frames):
        t = frame_idx * dt

        # Stage 1: World platform state
        w_state = world_service.step_world(dt=dt)
        assert w_state is not None

        # Stage 2: Virtual Camera projection and rendering
        cam_frame = camera_service.capture_frame()
        assert cam_frame is not None

        # Stage 3: Disturbance & Noise simulation
        dist_frame = disturbance_service.process_frame()
        assert dist_frame is not None

        # Stage 4: Beacon Detection & Centroiding
        det_result = detection_service.process_frame()
        assert det_result is not None

        # Stage 5: Beacon Tracking & Motion Prediction
        track_result = tracking_service.process_detection(det_result, timestamp=t)
        assert track_result is not None

        # Stage 6: Boresight Error Calculation & Alignment
        err_result = alignment_service.process_tracking(track_result)
        assert err_result is not None

        error_results.append(err_result)

        # Assert no NaNs or Infs anywhere in error outputs
        if err_result.pixel_error_x is not None:
            assert math.isfinite(err_result.pixel_error_x)
        if err_result.pixel_error_y is not None:
            assert math.isfinite(err_result.pixel_error_y)
        if err_result.angular_error_x_deg is not None:
            assert math.isfinite(err_result.angular_error_x_deg)
        if err_result.angular_error_y_deg is not None:
            assert math.isfinite(err_result.angular_error_y_deg)
        if err_result.angular_error_magnitude_deg is not None:
            assert math.isfinite(err_result.angular_error_magnitude_deg)

    # Check final pipeline state
    final_err = error_results[-1]
    assert final_err.valid is True
    assert final_err.status in [ErrorStatus.VALID, ErrorStatus.ALIGNED]
    assert final_err.center_x == 320.0
    assert final_err.center_y == 240.0

    # Verify telemetry packet is consistent
    telemetry = alignment_service.get_telemetry()
    assert telemetry.timestamp == pytest.approx((total_frames - 1) * dt)
    assert telemetry.valid is True
    assert "ALIGNED" in telemetry.status_text or "ERROR" in telemetry.status_text
