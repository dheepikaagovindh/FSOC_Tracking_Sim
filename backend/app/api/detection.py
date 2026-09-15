"""
Beacon Detection API Endpoints.
Team PHARO — SIH26169
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Response, status

from ..detection.models import (
    DetectionConfig,
    DetectionResult,
    DetectionStatus,
    DetectionTelemetry,
)
from ..detection.service import detection_service
from ..scenario.models import ScenarioConfig

router = APIRouter(prefix="/detection", tags=["Beacon Detection"])


@router.post("/initialize", response_model=DetectionStatus, summary="Initialize Beacon Detector")
def initialize_detection(scenario: Optional[ScenarioConfig] = None):
    """
    Initialize detection engine from active or provided ScenarioConfig.
    """
    try:
        return detection_service.initialize_from_scenario(scenario)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initialize detection engine: {str(e)}",
        )


@router.post("/reset", response_model=DetectionResult, summary="Reset Detection State")
def reset_detection():
    """Reset detection counters, clear state, and re-detect on current frame."""
    try:
        return detection_service.reset()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/status", response_model=DetectionStatus, summary="Get Detector Status")
def get_detection_status():
    """Retrieve detection module lifecycle, active method, config, and cumulative stats."""
    return detection_service.get_status()


@router.post("/detect", response_model=DetectionResult, summary="Execute Beacon Detection")
def execute_detection():
    """Run detection and centroid localization on the latest disturbed camera image."""
    try:
        return detection_service.process_frame()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/result", response_model=DetectionResult, summary="Get Latest Detection Result")
def get_detection_result():
    """Retrieve latest DetectionResult packet containing center (u, v), confidence, bbox, and latency."""
    try:
        return detection_service.get_latest_result()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/config", response_model=DetectionStatus, summary="Update Detector Configuration")
def update_detection_config(config: DetectionConfig):
    """Update active detection algorithm parameters, thresholds, and filters in real time."""
    try:
        return detection_service.set_config(config)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid detection configuration: {str(e)}",
        )


@router.get("/telemetry", response_model=DetectionTelemetry, summary="Get Detection Telemetry")
def get_detection_telemetry():
    """Retrieve real-time detection telemetry packet for HUD displays and monitoring."""
    try:
        return detection_service.get_telemetry()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/overlay", summary="Get Detection Overlay Image (PNG)")
def get_detection_overlay():
    """Retrieve disturbed camera observation with detected bounding box, center, and confidence overlay as PNG."""
    try:
        png_bytes = detection_service.get_overlay_image_png()
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/annotated-image", summary="Get Annotated Detection Image (PNG Alias)")
def get_annotated_image():
    """Alias for /detection/overlay for backwards compatibility."""
    return get_detection_overlay()
