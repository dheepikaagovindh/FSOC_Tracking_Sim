"""
Virtual Camera & Optical Image Generation Module (Standalone Simulation Package).
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
from app.camera.projection import (
    calculate_intrinsics,
    world_to_camera_frame,
    project_to_pixel,
    calculate_camera_angles,
    check_visibility,
)
from app.camera.renderer import (
    render_camera_frame,
    compute_spot_parameters,
    encode_image_to_png,
)
from app.camera.camera import VirtualCamera

__all__ = [
    "CameraIntrinsics",
    "CameraPose",
    "ProjectedPoint",
    "CameraAngles",
    "CameraVisibility",
    "CameraFrame",
    "CameraStatus",
    "VisibilityReason",
    "calculate_intrinsics",
    "world_to_camera_frame",
    "project_to_pixel",
    "calculate_camera_angles",
    "check_visibility",
    "render_camera_frame",
    "compute_spot_parameters",
    "encode_image_to_png",
    "VirtualCamera",
]
