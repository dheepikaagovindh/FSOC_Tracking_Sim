"""
Virtual Camera & Optical Image Generation Module.
Team PHARO — SIH26169
"""

from .models import (
    CameraIntrinsics,
    CameraPose,
    ProjectedPoint,
    CameraAngles,
    CameraVisibility,
    CameraFrame,
    CameraStatus,
    VisibilityReason,
)
from .projection import (
    calculate_intrinsics,
    world_to_camera_frame,
    project_to_pixel,
    calculate_camera_angles,
    check_visibility,
)
from .renderer import (
    render_camera_frame,
    compute_spot_parameters,
    encode_image_to_png,
)
from .camera import VirtualCamera

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
