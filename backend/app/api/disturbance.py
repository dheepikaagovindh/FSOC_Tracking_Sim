"""
Disturbance & Noise Simulation API Endpoints.
Team PHARO — SIH26169
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Response, status

from ..disturbance.models import (
    DisturbanceFrame,
    DisturbanceStatus,
    DisturbanceTelemetry,
)
from ..disturbance.service import disturbance_service
from ..scenario.models import ScenarioConfig, DisturbanceConfig

router = APIRouter(prefix="/disturbance", tags=["Disturbance & Noise Simulation"])


@router.post("/initialize", response_model=DisturbanceStatus, summary="Initialize Disturbance Engine")
def initialize_disturbance(scenario: Optional[ScenarioConfig] = None):
    """
    Initialize or re-configure disturbance simulation from active or provided ScenarioConfig.
    """
    try:
        return disturbance_service.initialize_from_scenario(scenario)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initialize disturbance engine: {str(e)}",
        )


@router.post("/reset", response_model=DisturbanceFrame, summary="Reset Disturbance State")
def reset_disturbance():
    """Reset disturbance temporal tracker and stochastic sequence to t=0."""
    try:
        return disturbance_service.reset()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/config", response_model=DisturbanceStatus, summary="Update Disturbance Parameters")
def update_disturbance_config(config: DisturbanceConfig):
    """Update active disturbance configuration parameters in real time."""
    try:
        return disturbance_service.set_config(config)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid disturbance configuration: {str(e)}",
        )


@router.post("/process", response_model=DisturbanceFrame, summary="Process Current Frame")
def process_frame():
    """Synchronize with latest clean camera frame and execute disturbance pipeline."""
    try:
        return disturbance_service.process_frame()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/frame", response_model=DisturbanceFrame, summary="Get Disturbed Frame Metadata")
def get_disturbance_frame():
    """Retrieve metadata of the latest disturbed optical observation frame."""
    try:
        return disturbance_service.get_latest_frame()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/image", summary="Get Disturbed Optical Sensor Image (PNG)")
def get_disturbed_image():
    """Retrieve the latest rendered disturbed synthetic sensor image as a PNG binary stream."""
    try:
        png_bytes = disturbance_service.get_latest_image_png()
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


@router.get("/status", response_model=DisturbanceStatus, summary="Get Disturbance Status")
def get_disturbance_status():
    """Retrieve disturbance module lifecycle, active severity, and configuration overview."""
    return disturbance_service.get_status()


@router.get("/telemetry", response_model=DisturbanceTelemetry, summary="Get Disturbance Telemetry")
def get_disturbance_telemetry():
    """Retrieve real-time disturbance telemetry diagnostics."""
    try:
        return disturbance_service.get_telemetry()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
