"""
Kinematics & Motion Profiles Engine (Simulation Engine Layer).
Team PHARO — SIH26169
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.world.motion import (
    MotionProfile,
    StaticMotionProfile,
    DriftMotionProfile,
    SwayMotionProfile,
    OrbitMotionProfile,
    MotionEngine,
)

__all__ = [
    "MotionProfile",
    "StaticMotionProfile",
    "DriftMotionProfile",
    "SwayMotionProfile",
    "OrbitMotionProfile",
    "MotionEngine",
]
