"""
Synthetic Image Renderer (Simulation Engine Layer).
Team PHARO — SIH26169
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.camera.renderer import (
    render_camera_frame,
    compute_spot_parameters,
    encode_image_to_png,
)

__all__ = [
    "render_camera_frame",
    "compute_spot_parameters",
    "encode_image_to_png",
]
