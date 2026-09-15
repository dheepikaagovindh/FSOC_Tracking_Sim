"""
Domain Models and Data Structures for Virtual World & Platform Simulation.
Team PHARO — SIH26169
"""

from __future__ import annotations
import math
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class Vector3D(BaseModel):
    """
    3D Cartesian Vector in World Coordinate Frame.
    Convention:
      X = Horizontal axis (left/right)
      Y = Vertical axis (up/down)
      Z = Depth / Forward axis (optical range)
      Origin: (0, 0, 0)
    """
    x: float = Field(default=0.0, description="X coordinate in meters")
    y: float = Field(default=0.0, description="Y coordinate in meters")
    z: float = Field(default=0.0, description="Z coordinate in meters")

    model_config = ConfigDict(frozen=False)

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def distance_to(self, other: Vector3D) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def __add__(self, other: Vector3D) -> Vector3D:
        return Vector3D(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other: Vector3D) -> Vector3D:
        return Vector3D(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def __mul__(self, scalar: float) -> Vector3D:
        return Vector3D(x=self.x * scalar, y=self.y * scalar, z=self.z * scalar)

    def __truediv__(self, scalar: float) -> Vector3D:
        if scalar == 0:
            return Vector3D(x=0.0, y=0.0, z=0.0)
        return Vector3D(x=self.x / scalar, y=self.y / scalar, z=self.z / scalar)


class PlatformDefinition(BaseModel):
    """Definition and initial kinematic parameters for a terminal platform."""
    id: str = Field(description="Unique platform identifier (e.g. 'camera', 'beacon')")
    name: str = Field(description="Human-readable platform name")
    initial_position: Vector3D = Field(default_factory=Vector3D, description="Position at t=0")
    velocity: Vector3D = Field(default_factory=Vector3D, description="Linear velocity (m/s)")
    motion_profile: str = Field(default="static", description="Motion profile ('static', 'drift', 'sway', 'orbit')")
    amplitude: float = Field(default=0.0, description="Oscillation or orbit radius/amplitude (m)", ge=0.0)
    frequency: float = Field(default=0.0, description="Oscillation or orbit frequency (Hz)", ge=0.0)
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional custom motion parameters")


class PlatformState(BaseModel):
    """Instantaneous kinematic state of a platform at simulation timestamp."""
    platform_id: str = Field(description="Platform identifier ('camera' or 'beacon')")
    name: str = Field(description="Platform name")
    timestamp: float = Field(description="Simulation timestamp in seconds", ge=0.0)
    position: Vector3D = Field(description="Current 3D Cartesian coordinates (m)")
    velocity: Vector3D = Field(description="Current 3D linear velocity vector (m/s)")
    motion_profile: str = Field(description="Active motion profile")


class RelativeGeometry(BaseModel):
    """
    Ground-truth relative geometry between Camera Platform (Receiver)
    and Beacon Platform (Transmitter).
    """
    relative_position: Vector3D = Field(description="Beacon position relative to camera: Pb - Pc")
    range: float = Field(description="Euclidean distance in meters: sqrt(dx^2 + dy^2 + dz^2)", ge=0.0)
    azimuth_deg: float = Field(description="Ground-truth azimuth / bearing: atan2(dx, dz) in degrees")
    elevation_deg: float = Field(description="Ground-truth elevation: atan2(dy, sqrt(dx^2 + dz^2)) in degrees")


class WorldState(BaseModel):
    """Complete ground-truth state snapshot of the Virtual World at timestamp."""
    timestamp: float = Field(description="Current simulation time in seconds", ge=0.0)
    camera_platform: PlatformState = Field(description="Receiver camera platform state")
    beacon_platform: PlatformState = Field(description="Transmitter beacon platform state")
    relative_geometry: RelativeGeometry = Field(description="Ground-truth relative geometry")


class WorldStatus(BaseModel):
    """Simulation lifecycle status and runtime metadata."""
    initialized: bool = Field(description="True if world is initialized from scenario")
    current_time: float = Field(description="Simulation clock time in seconds", ge=0.0)
    duration: float = Field(description="Total configured duration in seconds", gt=0.0)
    fps: float = Field(description="Simulation frames per second", gt=0.0)
    dt: float = Field(description="Timestep delta in seconds", gt=0.0)
    scenario_name: str = Field(description="Active scenario configuration title")
    camera_platform: Optional[PlatformState] = None
    beacon_platform: Optional[PlatformState] = None
    relative_geometry: Optional[RelativeGeometry] = None
