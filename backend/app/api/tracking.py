"""
Beacon Tracking & Motion Prediction API Endpoints.
Team PHARO — SIH26169
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Response, status

from ..tracking.models import (
    TrackingConfig,
    TrackingResult,
    TrackingStatusInfo,
    TrackingTelemetry,
)
from ..tracking.service import tracking_service
from ..detection.models import DetectionResult
from ..scenario.models import ScenarioConfig

router = APIRouter(prefix="/tracking", tags=["Beacon Tracking"])


@router.post("/initialize", response_model=TrackingStatusInfo, summary="Initialize Beacon Tracker")
def initialize_tracking(scenario: Optional[ScenarioConfig] = None):
    """
    Initialize or reconfigure the Kalman filter state from active scenario or provided config.
    """
    try:
        return tracking_service.initialize_from_scenario(scenario)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initialize tracker: {str(e)}",
        )


@router.post("/reset", response_model=TrackingResult, summary="Reset Tracker State")
def reset_tracking():
    """
    Clear all internal state, covariance, and history, resetting tracker to UNINITIALIZED.
    """
    try:
        return tracking_service.reset()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/status", response_model=TrackingStatusInfo, summary="Get Tracker Status")
def get_tracking_status():
    """
    Retrieve tracker lifecycle status, active configuration, and performance statistics.
    """
    try:
        return tracking_service.get_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/update", response_model=TrackingResult, summary="Execute Tracking Step")
def update_tracking(detection: Optional[DetectionResult] = None):
    """
    Run one predict & update tracking step using the provided or latest DetectionResult.
    """
    try:
        return tracking_service.process_detection(detection)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tracking update failed: {str(e)}",
        )


@router.get("/result", response_model=TrackingResult, summary="Get Latest Tracking Result")
def get_tracking_result():
    """
    Retrieve latest TrackingResult packet containing filtered positions, velocities, and predictions.
    """
    try:
        return tracking_service.get_latest_result()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/config", response_model=TrackingStatusInfo, summary="Update Tracker Configuration")
def update_tracking_config(config: TrackingConfig):
    """
    Update active Kalman filter parameters (process noise, measurement noise, max missed frames) dynamically.
    """
    try:
        return tracking_service.set_config(config)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tracking configuration: {str(e)}",
        )


@router.get("/telemetry", response_model=TrackingTelemetry, summary="Get Tracking Telemetry")
def get_tracking_telemetry():
    """
    Retrieve real-time tracking telemetry packet for HUD displays and diagnostics.
    """
    try:
        return tracking_service.get_telemetry()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/overlay", summary="Get Tracking HUD Overlay Image (PNG)")
def get_tracking_overlay():
    """
    Retrieve disturbed camera observation with multi-layer tracking HUD overlay as PNG.
    """
    try:
        png_bytes = tracking_service.get_overlay_image_png()
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/annotated-image", summary="Get Annotated Tracking Image (PNG Alias)")
def get_annotated_image():
    """Alias for /tracking/overlay for backwards compatibility."""
    return get_tracking_overlay()
