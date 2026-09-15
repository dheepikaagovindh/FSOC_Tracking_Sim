"""
Boresight Alignment & Error Calculation API Endpoints.
Team PHARO — SIH26169
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Response, status

from ..error.models import (
    AlignmentConfig,
    AlignmentError,
    ErrorStatusInfo,
    ErrorTelemetry,
)
from ..error.service import alignment_service
from ..tracking.models import TrackingResult
from ..scenario.models import ScenarioConfig

router = APIRouter(prefix="/error", tags=["Boresight Alignment & Error"])


@router.post("/initialize", response_model=ErrorStatusInfo, summary="Initialize Error Calculation Engine")
def initialize_error(scenario: Optional[ScenarioConfig] = None):
    """
    Initialize or reconfigure the error calculation engine from active scenario or provided config.
    """
    try:
        return alignment_service.initialize_from_scenario(scenario)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initialize alignment engine: {str(e)}",
        )


@router.post("/reset", response_model=AlignmentError, summary="Reset Error Calculation State")
def reset_error():
    """
    Clear all internal error history, rate tracking, and reset status to INVALID.
    """
    try:
        return alignment_service.reset()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/status", response_model=ErrorStatusInfo, summary="Get Alignment Engine Status")
def get_error_status():
    """
    Retrieve alignment engine status, active tolerances, and lock statistics.
    """
    try:
        return alignment_service.get_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/calculate", response_model=AlignmentError, summary="Calculate Alignment Error")
def calculate_error(tracking: Optional[TrackingResult] = None):
    """
    Calculate optical boresight pixel, normalized, and angular errors from the provided or latest TrackingResult.
    """
    try:
        return alignment_service.process_tracking(tracking)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculation failed: {str(e)}",
        )


@router.get("/result", response_model=AlignmentError, summary="Get Latest Alignment Error Result")
def get_error_result():
    """
    Retrieve the latest computed AlignmentError containing pixel and angular offsets.
    """
    try:
        return alignment_service.get_latest_result()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/config", response_model=ErrorStatusInfo, summary="Update Alignment Tolerances")
def update_error_config(config: AlignmentConfig):
    """
    Update active alignment lock tolerances (pixel and angular) and evaluation modes dynamically.
    """
    try:
        return alignment_service.set_config(config)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid alignment configuration: {str(e)}",
        )


@router.get("/telemetry", response_model=ErrorTelemetry, summary="Get Alignment Telemetry")
def get_error_telemetry():
    """
    Retrieve real-time alignment telemetry packet for HUD displays and diagnostic gauges.
    """
    try:
        return alignment_service.get_telemetry()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/overlay", summary="Get Alignment HUD Overlay Image (PNG)")
def get_error_overlay():
    """
    Retrieve camera observation with boresight crosshairs, alignment tolerance reticle, and error vector PNG.
    """
    try:
        png_bytes = alignment_service.get_overlay_image_png()
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


@router.get("/annotated-image", summary="Get Annotated Alignment Image (PNG Alias)")
def get_annotated_image():
    """Alias for /error/overlay for backwards compatibility."""
    return get_error_overlay()
