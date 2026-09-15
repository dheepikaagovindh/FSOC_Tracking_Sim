"""
Synthetic Camera Frame Renderer and Optical Image Synthesis.
Team PHARO — SIH26169

Provides lightweight, vectorized generation of synthetic optical sensor frames.
"""

from __future__ import annotations
import io
import math
from typing import Optional, Tuple
import numpy as np
from PIL import Image

from .models import ProjectedPoint, CameraVisibility


def compute_spot_parameters(brightness: float, size: float) -> Tuple[int, float]:
    """
    Map BeaconConfig brightness and size to 8-bit image intensity and pixel radius.
    
    Conventions:
      - Brightness: If <= 1.0, scaled to [0, 255]. If > 1.0, clamped to [0, 255].
      - Size: Interpreted as diameter in pixels. Radius = max(1.0, size / 2.0).
    """
    if brightness <= 1.0:
        intensity = int(round(max(0.0, min(1.0, brightness)) * 255.0))
    else:
        intensity = int(round(max(0.0, min(255.0, brightness))))
    
    # Ensure minimum visible intensity if brightness is strictly positive
    if brightness > 0.0 and intensity == 0:
        intensity = 1

    radius = max(1.0, float(size) / 2.0)
    return intensity, radius


def render_camera_frame(
    width: int,
    height: int,
    projection: ProjectedPoint,
    visibility: CameraVisibility,
    brightness: float = 1.0,
    size: float = 5.0,
) -> np.ndarray:
    """
    Render an 8-bit grayscale optical sensor image containing the synthetic beacon spot.
    
    Parameters:
      width: Sensor width in pixels
      height: Sensor height in pixels
      projection: Projected (u, v) pixel coordinates
      visibility: Visibility classification (visible, in_front, inside FOV)
      brightness: Normalized or absolute beacon intensity
      size: Beacon spot diameter in pixels
      
    Returns:
      NumPy 2D array of shape (height, width) with dtype uint8.
    """
    # Create black background sensor image
    image = np.zeros((height, width), dtype=np.uint8)

    # Render beacon spot only if visible in front of camera and inside sensor bounds
    if not visibility.visible:
        return image

    intensity, radius = compute_spot_parameters(brightness, size)
    u = projection.u
    v = projection.v

    # Compute bounding patch around spot to maximize rendering speed
    r_int = int(math.ceil(radius))
    u_min = max(0, int(math.floor(u - r_int)))
    u_max = min(width - 1, int(math.ceil(u + r_int)))
    v_min = max(0, int(math.floor(v - r_int)))
    v_max = min(height - 1, int(math.ceil(v + r_int)))

    if u_min > u_max or v_min > v_max:
        return image

    # Vectorized distance calculation within bounding box
    y_coords, x_coords = np.ogrid[v_min:v_max + 1, u_min:u_max + 1]
    dist_sq = (x_coords - u) ** 2 + (y_coords - v) ** 2
    mask = dist_sq <= (radius ** 2)

    # Apply spot intensity
    patch = image[v_min:v_max + 1, u_min:u_max + 1]
    patch[mask] = intensity
    image[v_min:v_max + 1, u_min:u_max + 1] = patch

    return image


def encode_image_to_png(image_array: np.ndarray) -> bytes:
    """
    Encode a 2D uint8 NumPy grayscale image array to standard PNG bytes.
    """
    pil_img = Image.fromarray(image_array, mode="L")
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
