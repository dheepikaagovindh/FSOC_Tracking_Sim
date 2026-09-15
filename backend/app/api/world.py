"""
Virtual World Simulation API Endpoints.
Team PHARO — SIH26169
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..world.models import WorldState, WorldStatus, PlatformState, RelativeGeometry
from ..world.service import world_service
from ..scenario.models import ScenarioConfig

router = APIRouter(prefix="/world", tags=["Virtual World & Platform Simulation"])


class StepRequest(BaseModel):
    dt: Optional[float] = Field(default=None, description="Time step in seconds (defaults to 1/fps)", gt=0.0)


class TimeRequest(BaseModel):
    time: float = Field(description="Explicit simulation clock timestamp (seconds)", ge=0.0)


@router.post("/initialize", response_model=WorldState, summary="Initialize Virtual World")
def initialize_world(scenario: Optional[ScenarioConfig] = None):
    """
    Initialize the Virtual World using the provided ScenarioConfig
    or the currently active ScenarioConfig.
    """
    try:
        return world_service.initialize_world(scenario)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initialize world: {str(e)}",
        )


@router.post("/reset", response_model=WorldState, summary="Reset World Simulation")
def reset_world():
    """Reset the simulation clock to t=0 and recalculate initial platform states."""
    try:
        return world_service.reset_world()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/step", response_model=WorldState, summary="Step Simulation Clock")
def step_world(request: Optional[StepRequest] = None):
    """
    Advance simulation clock by dt (defaults to 1/FPS) and return updated ground-truth state.
    """
    try:
        step_dt = request.dt if request else None
        return world_service.step_world(step_dt)
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


@router.post("/time", response_model=WorldState, summary="Set Explicit Simulation Time")
def set_time(request: TimeRequest):
    """Set the simulation clock to an explicit timestamp."""
    try:
        return world_service.set_world_time(request.time)
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


@router.get("/state", response_model=WorldState, summary="Get Ground-Truth World State")
def get_world_state():
    """Retrieve complete instantaneous ground-truth world state snapshot."""
    try:
        return world_service.get_world_state()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/platform/{platform_id}", response_model=PlatformState, summary="Get Platform State")
def get_platform_state(platform_id: str):
    """Retrieve kinematic state for a specific platform ('camera' or 'beacon')."""
    try:
        return world_service.get_platform_state(platform_id)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/geometry", response_model=RelativeGeometry, summary="Get Relative Geometry")
def get_geometry():
    """Retrieve ground-truth relative geometry (range, azimuth, elevation) from Camera to Beacon."""
    try:
        return world_service.get_geometry()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/status", response_model=WorldStatus, summary="Get World Status & Metadata")
def get_world_status():
    """Retrieve world simulation initialization status, clock, and platform summaries."""
    return world_service.get_status()
