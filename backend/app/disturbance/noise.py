"""
Sensor Noise Simulation for FSOC Optical Receiver.
Team PHARO — SIH26169

Simulates electronic read noise, thermal dark current noise, and optical shot noise.
"""

from __future__ import annotations
from typing import Tuple
import numpy as np

from .models import NoiseMetadata


def compute_noise_sigma(magnitude: float) -> float:
    """
    Map noise magnitude parameter to effective 8-bit Gaussian standard deviation sigma.
    
    Convention:
      - If magnitude <= 1.0: Treated as normalized sensor full-scale fraction (e.g. 0.05 -> 12.75).
      - If magnitude > 1.0: Treated as direct 8-bit sigma (e.g. 15.0 -> 15.0).
    """
    if magnitude <= 0.0:
        return 0.0
    if magnitude <= 1.0:
        return float(magnitude) * 255.0
    return float(magnitude)


def apply_sensor_noise(
    image: np.ndarray,
    magnitude: float,
    enabled: bool = True,
    seed: int = 42,
    frame_index: int = 0,
) -> Tuple[np.ndarray, NoiseMetadata]:
    """
    Apply zero-mean additive Gaussian sensor noise to an optical sensor image.
    
    Equations:
      I_disturbed = clip(I + N(0, sigma^2), 0, 255)
      
    Guarantees:
      - Deterministic with fixed (seed, frame_index).
      - Output dtype is strictly np.uint8.
      - Image dimensions are strictly preserved.
      - Output values remain strictly bounded in [0, 255].
    """
    if not enabled or magnitude <= 0.0:
        return image.copy(), NoiseMetadata(
            enabled=enabled,
            magnitude=magnitude,
            sigma=0.0,
            applied=False,
        )

    sigma = compute_noise_sigma(magnitude)
    if sigma <= 0.0:
        return image.copy(), NoiseMetadata(
            enabled=enabled,
            magnitude=magnitude,
            sigma=0.0,
            applied=False,
        )

    # Derive deterministic frame-specific seed
    frame_seed = (int(seed) * 1000003 + int(frame_index) * 997 + 17) & 0xFFFFFFFF
    rng = np.random.default_rng(frame_seed)

    noise = rng.normal(loc=0.0, scale=sigma, size=image.shape)
    disturbed = np.clip(image.astype(np.float64) + noise, 0.0, 255.0).astype(np.uint8)

    return disturbed, NoiseMetadata(
        enabled=True,
        magnitude=magnitude,
        sigma=sigma,
        applied=True,
    )
