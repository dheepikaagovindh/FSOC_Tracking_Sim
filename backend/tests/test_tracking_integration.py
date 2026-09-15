"""
Full 5-Stage Simulation Pipeline Integration Test (World -> Camera -> Disturbance -> Detection -> Tracking).
Team PHARO — SIH26169
"""

import math
import pytest

from app.world.service import world_service
from app.camera.service import camera_service
from app.disturbance.service import disturbance_service
from app.detection.service import detection_service
from app.tracking.service import tracking_service
from app.tracking.models import TrackingStatus


def test_full_pipeline_multi_frame_tracking():
    """
    Execute 30 frames of end-to-end simulation across all 5 modules:
    World -> Camera -> Disturbance -> Detection -> Tracking
    """
    # 1. Reset all services to default scenario
    world_service.reset_world()
    camera_service.reset_camera()
    disturbance_service.reset()
    detection_service.reset()
    tracking_service.reset()

    dt = 1.0 / 30.0  # 30 FPS
    total_frames = 30
    tracking_results = []

    for frame_idx in range(total_frames):
        t = frame_idx * dt

        # Stage 1: World platform state
        w_state = world_service.step_world(dt=dt)
        assert w_state is not None

        # Stage 2: Virtual Camera projection and rendering
        cam_frame = camera_service.capture_frame()
        assert cam_frame is not None
        assert cam_frame.width == 640
        assert cam_frame.height == 480

        # Stage 3: Disturbance & Noise simulation
        dist_frame = disturbance_service.process_frame()
        assert dist_frame is not None

        # Stage 4: Beacon Detection & Centroiding (NO ground-truth assistance)
        det_result = detection_service.process_frame()
        assert det_result is not None

        # Stage 5: Beacon Tracking & Motion Prediction
        track_result = tracking_service.process_detection(det_result, timestamp=t)
        assert track_result is not None

        tracking_results.append((det_result, track_result))

        # Assert no NaNs or Infs anywhere in tracking outputs
        if track_result.position_x is not None:
            assert math.isfinite(track_result.position_x)
        if track_result.position_y is not None:
            assert math.isfinite(track_result.position_y)
        if track_result.velocity_x is not None:
            assert math.isfinite(track_result.velocity_x)
        if track_result.velocity_y is not None:
            assert math.isfinite(track_result.velocity_y)
        if track_result.predicted_x is not None:
            assert math.isfinite(track_result.predicted_x)
        if track_result.predicted_y is not None:
            assert math.isfinite(track_result.predicted_y)

    # Check that tracking has initialized and operated
    final_det, final_track = tracking_results[-1]
    assert final_track.initialized is True
    assert final_track.status in [TrackingStatus.TRACKING, TrackingStatus.PREDICTING]
    assert final_track.confidence >= 0.0

    # Verify telemetry packet is consistent
    telemetry = tracking_service.get_telemetry()
    assert telemetry.timestamp == pytest.approx((total_frames - 1) * dt)
    assert telemetry.status in ["TRACKING", "PREDICTING"]
