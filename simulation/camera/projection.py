"""
Optical Projection Functions (Simulation Engine Layer).
Team PHARO — SIH26169
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.camera.projection import (
    calculate_intrinsics,
    world_to_camera_frame,
    project_to_pixel,
    calculate_camera_angles,
    check_visibility,
)

__all__ = [
    "calculate_intrinsics",
    "world_to_camera_frame",
    "project_to_pixel",
    "calculate_camera_angles",
    "check_visibility",
]
