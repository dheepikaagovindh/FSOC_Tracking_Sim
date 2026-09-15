"""
Image-Plane Vibration & Micro-Jitter Simulation.
Team PHARO — SIH26169

Simulates high-frequency UAV rotor vibrations, airborne aerodynamic flutter, and gimbal base excitation
as continuous, deterministic image-plane translation offsets.
"""

from __future__ import annotations
import math
from typing import Tuple
import numpy as np
from PIL import Image

from .models import VibrationMetadata


def calculate_vibration_offset(
    magnitude: float,
    timestamp: float,
    freq_x: float = 5.0,
    freq_y: float = 7.0,
    phase_x: float = 0.0,
    phase_y: float = math.pi / 4.0,
) -> Tuple[float, float]:
    """
    Calculate deterministic harmonic image-plane displacement (dx, dy) in pixels.
    
    Equations:
      dx(t) = A_x * sin(2 * pi * f_x * t + phi_x)
      dy(t) = A_y * sin(2 * pi * f_y * t + phi_y)
      
    where:
      A_x = magnitude
      A_y = magnitude * 0.8
    """
    if magnitude <= 0.0 or math.isnan(magnitude):
        return 0.0, 0.0

    ax = float(magnitude)
    ay = float(magnitude) * 0.8

    dx = ax * math.sin(2.0 * math.pi * freq_x * timestamp + phase_x)
    dy = ay * math.sin(2.0 * math.pi * freq_y * timestamp + phase_y)

    return dx, dy


def apply_image_vibration(
    image: np.ndarray,
    magnitude: float,
    timestamp: float,
    enabled: bool = True,
) -> Tuple[np.ndarray, VibrationMetadata]:
    """
    Apply sub-pixel 2D translation to simulate image-plane platform jitter.
    
    Parameters:
      image: Input 2D uint8 NumPy grayscale image array.
      magnitude: Vibration peak amplitude in pixels.
      timestamp: Simulation timestamp in seconds.
      enabled: Boolean flag to enable/disable vibration.
      
    Border Policy:
      Black fill (`fillcolor=0`) for pixels shifted into the sensor frame from outside.
      Strictly NO wrapping around opposite image edges.
      
    Guarantees:
      - Dimensions (H, W) strictly preserved.
      - Output dtype strictly np.uint8.
      - Deterministic output for identical (magnitude, timestamp).
    """
    if not enabled or magnitude <= 0.0:
        return image.copy(), VibrationMetadata(
            enabled=enabled,
            magnitude=max(0.0, magnitude if not math.isnan(magnitude) else 0.0),
            offset_x=0.0,
            offset_y=0.0,
            applied=False,
        )

    dx, dy = calculate_vibration_offset(magnitude, timestamp)
    if abs(dx) < 1e-4 and abs(dy) < 1e-4:
        return image.copy(), VibrationMetadata(
            enabled=True,
            magnitude=magnitude,
            offset_x=0.0,
            offset_y=0.0,
            applied=False,
        )

    height, width = image.shape
    pil_img = Image.fromarray(image, mode="L")

    # PIL Affine transform takes matrix for inverse coordinate mapping:
    # [a, b, c, d, e, f] where x_src = a*x + b*y + c, y_src = d*x + e*y + f
    # To shift image by (+dx, +dy), x_src = x - dx, y_src = y - dy:
    affine_matrix = (1.0, 0.0, -dx, 0.0, 1.0, -dy)
    shifted_pil = pil_img.transform(
        (width, height),
        Image.AFFINE,
        affine_matrix,
        resample=Image.BILINEAR,
        fillcolor=0,
    )
    shifted_arr = np.array(shifted_pil, dtype=np.uint8)

    return shifted_arr, VibrationMetadata(
        enabled=True,
        magnitude=magnitude,
        offset_x=dx,
        offset_y=dy,
        applied=True,
    )
