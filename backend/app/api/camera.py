"""
Virtual Camera & Optical Image Generation API Endpoints.
Team PHARO — SIH26169
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field

from ..camera.models import (
    CameraFrame,
    CameraStatus,
    CameraPose,
    CameraIntrinsics,
)
from ..camera.service import camera_service
from ..scenario.models import ScenarioConfig

router = APIRouter(prefix="/camera", tags=["Virtual Camera & Optical Rendering"])


class PanTiltRequest(BaseModel):
    pan_deg: Optional[float] = Field(default=None, description="Gimbal pan angle in degrees")
    tilt_deg: Optional[float] = Field(default=None, description="Gimbal tilt angle in degrees")


@router.post("/initialize", response_model=CameraStatus, summary="Initialize Virtual Camera")
def initialize_camera(scenario: Optional[ScenarioConfig] = None):
    """
    Initialize or re-initialize optical parameters and sync camera with active scenario/world state.
    """
    try:
        return camera_service.initialize_camera(scenario)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initialize camera: {str(e)}",
        )


@router.post("/reset", response_model=CameraFrame, summary="Reset Camera Orientation")
def reset_camera():
    """Reset camera gimbal pan and tilt orientation to initial configured angles."""
    try:
        return camera_service.reset_camera()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/pose", response_model=CameraPose, summary="Set Gimbal Pan/Tilt Orientation")
def set_camera_pose(request: PanTiltRequest):
    """Update camera gimbal pan/tilt orientation directly."""
    try:
        return camera_service.set_pose(pan_deg=request.pan_deg, tilt_deg=request.tilt_deg)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/capture", response_model=CameraFrame, summary="Capture Synthetic Frame")
def capture_frame():
    """Synchronize with world state and capture/render a fresh optical sensor frame."""
    try:
        return camera_service.capture_frame()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/frame", response_model=CameraFrame, summary="Get Latest Frame Metadata")
def get_camera_frame():
    """Retrieve metadata of the latest captured optical frame (pixel projection, apparent angles, visibility)."""
    try:
        return camera_service.get_latest_frame()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/image", summary="Get Rendered Optical Sensor Image (PNG)")
def get_camera_image():
    """Retrieve the latest rendered synthetic optical sensor image as a PNG binary stream."""
    try:
        png_bytes = camera_service.get_latest_image_png()
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


@router.get("/intrinsics", response_model=CameraIntrinsics, summary="Get Optical Intrinsics")
def get_camera_intrinsics():
    """Retrieve derived optical intrinsic matrix parameters (fx, fy, cx, cy, FOVs)."""
    try:
        return camera_service.get_status().intrinsics
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/status", response_model=CameraStatus, summary="Get Camera Status")
def get_camera_status():
    """Retrieve camera initialization status, optical configuration, and current orientation."""
    return camera_service.get_status()


@router.get("/telemetry", summary="Get Optical Tracking Telemetry")
def get_camera_telemetry():
    """Retrieve comprehensive optical tracking telemetry packet."""
    try:
        return camera_service.get_telemetry()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
