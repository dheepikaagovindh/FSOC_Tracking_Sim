"""
Virtual World Simulation Domain Models (Simulation Engine Layer).
Team PHARO — SIH26169
"""

import os
import sys

# Support direct imports within FSOC_Tracking_Sim
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.world.models import (
    Vector3D,
    PlatformDefinition,
    PlatformState,
    RelativeGeometry,
    WorldState,
    WorldStatus,
)

__all__ = [
    "Vector3D",
    "PlatformDefinition",
    "PlatformState",
    "RelativeGeometry",
    "WorldState",
    "WorldStatus",
]
