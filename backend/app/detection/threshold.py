"""
Adaptive Background Noise Estimation and Dynamic Thresholding.
Team PHARO — SIH26169

Provides robust background statistics (mu_bg, sigma_bg), dynamic k-sigma thresholding,
and localized Region of Interest (ROI) extraction without external computer vision dependencies.
"""

from __future__ import annotations
import math
from typing import Optional, Tuple
import numpy as np


def estimate_background_noise(image: np.ndarray) -> Tuple[float, float]:
    """
    Robustly estimate the sensor background noise mean (mu_bg) and standard deviation (sigma_bg).
    
    Uses Median and Median Absolute Deviation (MAD), which are highly resistant to outlier
    bright pixels produced by the optical beacon spot.
    
    For a Gaussian distribution:
      sigma = 1.4826 * MAD(I)
      where MAD(I) = median(|I - median(I)|)
      
    Returns:
      (mu_bg, sigma_bg) as floats.
    """
    if image is None or image.size == 0:
        return 0.0, 1.0

    img_float = image.astype(np.float64)
    med = float(np.median(img_float))
    mad = float(np.median(np.abs(img_float - med)))
    sigma_mad = 1.4826 * mad

    if sigma_mad >= 0.8:
        return med, sigma_mad

    # In clean / low-noise images, MAD is often 0 because >50% pixels are exactly 0.
    # Fallback to trimmed sample statistics on the lower 95th percentile.
    p95 = float(np.percentile(img_float, 95))
    bg_mask = img_float <= max(p95, 1.0)
    bg_pixels = img_float[bg_mask]

    if bg_pixels.size > 0:
        mu_sample = float(np.mean(bg_pixels))
        sigma_sample = float(np.std(bg_pixels))
        # Ensure minimum positive sigma floor for stable PNR divisions
        sigma_effective = max(sigma_sample, 0.5)
        return mu_sample, sigma_effective

    return med, max(sigma_mad, 0.5)


def compute_adaptive_threshold(
    image: np.ndarray,
    k_sigma: float = 3.5,
) -> Tuple[float, float, float]:
    """
    Calculate dynamic intensity segmentation threshold based on background noise statistics.
    
    Formula:
      T = mu_bg + k_sigma * sigma_bg
      
    Returns:
      (threshold, mu_bg, sigma_bg)
    """
    mu_bg, sigma_bg = estimate_background_noise(image)
    threshold = mu_bg + k_sigma * sigma_bg
    # Enforce threshold is strictly above background mean
    threshold = max(threshold, mu_bg + 1.0, 3.0)
    return float(threshold), mu_bg, sigma_bg


def find_candidate_peak(
    image: np.ndarray,
    threshold: float,
    min_pnr: float,
    mu_bg: float,
    sigma_bg: float,
) -> Optional[Tuple[int, int, float, float]]:
    """
    Locate the primary candidate optical spot peak in the sensor image.
    
    Returns:
      (peak_x, peak_y, peak_val, pnr) if candidate satisfies detection criteria,
      else None.
    """
    if image is None or image.size == 0:
        return None

    # Global argmax
    flat_idx = int(np.argmax(image))
    peak_y, peak_x = divmod(flat_idx, image.shape[1])
    peak_val = float(image[peak_y, peak_x])

    sigma_safe = max(sigma_bg, 1e-4)
    pnr = (peak_val - mu_bg) / sigma_safe

    if peak_val >= threshold and pnr >= min_pnr:
        return peak_x, peak_y, peak_val, pnr

    return None


def extract_roi(
    image: np.ndarray,
    center_x: int,
    center_y: int,
    radius: int = 15,
) -> Tuple[np.ndarray, int, int, int, int]:
    """
    Extract a localized (2R+1) x (2R+1) Region of Interest (ROI) around candidate center coordinates.
    
    Clamps bounds safely to image boundaries.
    
    Returns:
      (roi_array, x_min, y_min, x_max, y_max)
    """
    height, width = image.shape
    x_min = max(0, center_x - radius)
    x_max = min(width - 1, center_x + radius)
    y_min = max(0, center_y - radius)
    y_max = min(height - 1, center_y + radius)

    roi = image[y_min : y_max + 1, x_min : x_max + 1]
    return roi, x_min, y_min, x_max, y_max
