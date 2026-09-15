"""
Image Preprocessing for Beacon Detection.
Team PHARO — SIH26169

Provides input validation, format normalization, grayscale conversion,
and optional spatial smoothing. Does NOT simulate environmental disturbances.
"""

from __future__ import annotations
from typing import Optional, Tuple
import cv2
import numpy as np


def validate_image_input(image: np.ndarray) -> Tuple[bool, str]:
    """
    Validate input image format, dimension, and type safety.
    """
    if image is None:
        return False, "Input image is None"
    if not isinstance(image, np.ndarray):
        return False, f"Expected numpy.ndarray, got {type(image).__name__}"
    if image.size == 0:
        return False, "Image array has zero size"
    if image.ndim < 2 or image.ndim > 3:
        return False, f"Invalid image dimensions: {image.ndim}D (expected 2D or 3D)"
    return True, "Valid"


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convert 2D/3D sensor image to a 2D uint8 grayscale array.
    """
    if image.ndim == 2:
        if image.dtype == np.uint8:
            return image
        return np.clip(image, 0, 255).astype(np.uint8)

    if image.ndim == 3:
        channels = image.shape[2]
        if channels == 1:
            return image[:, :, 0].astype(np.uint8)
        if channels == 3:
            return cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGR2GRAY)
        if channels == 4:
            return cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGRA2GRAY)

    raise ValueError(f"Unsupported image shape for grayscale conversion: {image.shape}")


def apply_blur(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    Apply Gaussian spatial smoothing to reduce high-frequency salt-and-pepper noise.
    """
    if kernel_size <= 1:
        return image
    k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    return cv2.GaussianBlur(image, (k, k), 0)


def preprocess_image(image: np.ndarray, blur_kernel: int = 3) -> np.ndarray:
    """
    Complete standard preprocessing pipeline:
    1. Validation
    2. Grayscale Conversion
    3. Optional Gaussian Blur
    """
    valid, msg = validate_image_input(image)
    if not valid:
        raise ValueError(f"Image preprocessing validation error: {msg}")

    gray = to_grayscale(image)
    if blur_kernel > 1:
        gray = apply_blur(gray, blur_kernel)
    return gray
