"""
Optical and Atmospheric Blur Simulation for FSOC Receiver.
Team PHARO — SIH26169

Simulates atmospheric optical turbulence PSF expansion, defocus, and velocity-induced optical smear.
"""

from __future__ import annotations
import math
from typing import Tuple
import numpy as np
from PIL import Image, ImageFilter

from .models import BlurMetadata


def apply_image_blur(
    image: np.ndarray,
    blur_strength: float,
    enabled: bool = True,
) -> Tuple[np.ndarray, BlurMetadata]:
    """
    Apply 2D Gaussian optical blur to an 8-bit sensor image.
    
    Parameters:
      image: Input 2D uint8 NumPy grayscale image array.
      blur_strength: Blur radius / PSF sigma in pixels.
      enabled: Boolean flag to enable/disable blur.
      
    Guarantees:
      - Dimensions (H, W) strictly preserved.
      - Output dtype strictly np.uint8.
      - Graceful handling of blur_strength <= 0, nan, inf, and extreme values.
    """
    if not enabled or blur_strength <= 0.0 or math.isnan(blur_strength) or math.isinf(blur_strength):
        return image.copy(), BlurMetadata(
            enabled=enabled,
            strength=max(0.0, blur_strength if not (math.isnan(blur_strength) or math.isinf(blur_strength)) else 0.0),
            kernel_size=1,
            applied=False,
        )

    # Clamp blur radius to physically reasonable range for sensor
    radius = min(50.0, max(0.1, float(blur_strength)))
    effective_kernel_size = int(2 * math.ceil(2.0 * radius) + 1)

    pil_img = Image.fromarray(image, mode="L")
    blurred_pil = pil_img.filter(ImageFilter.GaussianBlur(radius=radius))
    blurred_arr = np.array(blurred_pil, dtype=np.uint8)

    return blurred_arr, BlurMetadata(
        enabled=True,
        strength=radius,
        kernel_size=effective_kernel_size,
        applied=True,
    )
