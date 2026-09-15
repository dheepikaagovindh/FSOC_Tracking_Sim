"""
Virtual Camera Models (Simulation Engine Layer).
Team PHARO — SIH26169
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.camera.models import (
    CameraIntrinsics,
    CameraPose,
    ProjectedPoint,
    CameraAngles,
    CameraVisibility,
    CameraFrame,
    CameraStatus,
    VisibilityReason,
)

__all__ = [
    "CameraIntrinsics",
    "CameraPose",
    "ProjectedPoint",
    "CameraAngles",
    "CameraVisibility",
    "CameraFrame",
    "CameraStatus",
    "VisibilityReason",
]
