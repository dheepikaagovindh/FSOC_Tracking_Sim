"""
Centroiding and Sub-Pixel Spot Localization Algorithms.
Team PHARO — SIH26169

Implements:
1. Intensity-Weighted Center of Mass (CoM).
2. Localized Windowed CoM.
3. 2D Gaussian Sub-Pixel Peak Fitting.
4. Bounding Box extraction.
"""

from __future__ import annotations
import math
from typing import Optional, Tuple
import numpy as np

from .models import BoundingBox


def intensity_weighted_centroid(
    roi: np.ndarray,
    threshold: float,
) -> Tuple[float, float, float]:
    """
    Compute the intensity-weighted Center of Mass (CoM) on a localized Region of Interest (ROI).
    
    Equations:
      W(y, x) = max(0.0, I(y, x) - threshold)
      S = sum(W(y, x))
      x_hat = sum(x * W(y, x)) / S
      y_hat = sum(y * W(y, x)) / S
      
    Returns:
      (x_rel, y_rel, integrated_flux) relative to top-left of ROI array (0-indexed).
    """
    if roi is None or roi.size == 0:
        return 0.0, 0.0, 0.0

    roi_float = roi.astype(np.float64)
    weights = np.maximum(0.0, roi_float - threshold)
    total_flux = float(np.sum(weights))

    if total_flux <= 1e-6:
        # Fallback to argmax peak within ROI
        flat_idx = int(np.argmax(roi))
        py, px = divmod(flat_idx, roi.shape[1])
        return float(px), float(py), 0.0

    h, w = roi.shape
    y_coords, x_coords = np.mgrid[0:h, 0:w]

    x_rel = float(np.sum(x_coords * weights) / total_flux)
    y_rel = float(np.sum(y_coords * weights) / total_flux)

    return x_rel, y_rel, total_flux


def gaussian_subpixel_refinement(
    roi: np.ndarray,
    peak_x: int,
    peak_y: int,
) -> Tuple[float, float]:
    """
    Sub-pixel peak localization using 2D Log-Gaussian / Parabolic 3-point estimator.
    
    Given 3 consecutive 1D samples [I_-1, I_0, I_+1] where I_0 is the local maximum:
      delta = 0.5 * (ln(I_+1) - ln(I_-1)) / (2 * ln(I_0) - ln(I_+1) - ln(I_-1))
      
    Returns:
      (x_subpixel, y_subpixel) relative to top-left of ROI array.
    """
    h, w = roi.shape
    roi_float = roi.astype(np.float64)

    # Horizontal subpixel delta
    dx = 0.0
    if 0 < peak_x < w - 1:
        v_m1 = max(1.0, float(roi_float[peak_y, peak_x - 1]))
        v_0 = max(1.0, float(roi_float[peak_y, peak_x]))
        v_p1 = max(1.0, float(roi_float[peak_y, peak_x + 1]))

        if v_0 >= v_m1 and v_0 >= v_p1:
            l_m1 = math.log(v_m1)
            l_0 = math.log(v_0)
            l_p1 = math.log(v_p1)
            denom = 2.0 * (2.0 * l_0 - l_m1 - l_p1)
            if abs(denom) > 1e-5:
                dx = (l_p1 - l_m1) / denom
                dx = max(-0.5, min(0.5, dx))

    # Vertical subpixel delta
    dy = 0.0
    if 0 < peak_y < h - 1:
        v_m1 = max(1.0, float(roi_float[peak_y - 1, peak_x]))
        v_0 = max(1.0, float(roi_float[peak_y, peak_x]))
        v_p1 = max(1.0, float(roi_float[peak_y + 1, peak_x]))

        if v_0 >= v_m1 and v_0 >= v_p1:
            l_m1 = math.log(v_m1)
            l_0 = math.log(v_0)
            l_p1 = math.log(v_p1)
            denom = 2.0 * (2.0 * l_0 - l_m1 - l_p1)
            if abs(denom) > 1e-5:
                dy = (l_p1 - l_m1) / denom
                dy = max(-0.5, min(0.5, dy))

    return float(peak_x + dx), float(peak_y + dy)


def calculate_bounding_box(
    roi: np.ndarray,
    threshold: float,
    origin_x: int,
    origin_y: int,
    fallback_radius: int = 4,
) -> BoundingBox:
    """
    Compute the bounding box of pixels exceeding threshold within the ROI, mapped back to full image coordinates.
    """
    h, w = roi.shape
    above_thresh = roi >= threshold
    y_indices, x_indices = np.where(above_thresh)

    if len(x_indices) > 0:
        local_x_min = int(np.min(x_indices))
        local_x_max = int(np.max(x_indices))
        local_y_min = int(np.min(y_indices))
        local_y_max = int(np.max(y_indices))
    else:
        # Fallback to center of ROI
        cx = w // 2
        cy = h // 2
        local_x_min = max(0, cx - fallback_radius)
        local_x_max = min(w - 1, cx + fallback_radius)
        local_y_min = max(0, cy - fallback_radius)
        local_y_max = min(h - 1, cy + fallback_radius)

    # Pad minimum 2px width/height for aesthetic bounding box visualization
    if local_x_max - local_x_min < 2:
        local_x_min = max(0, local_x_min - 1)
        local_x_max = min(w - 1, local_x_max + 1)
    if local_y_max - local_y_min < 2:
        local_y_min = max(0, local_y_min - 1)
        local_y_max = min(h - 1, local_y_max + 1)

    abs_x_min = origin_x + local_x_min
    abs_x_max = origin_x + local_x_max
    abs_y_min = origin_y + local_y_min
    abs_y_max = origin_y + local_y_max

    box_w = abs_x_max - abs_x_min + 1
    box_h = abs_y_max - abs_y_min + 1
    center_x = abs_x_min + (box_w - 1) / 2.0
    center_y = abs_y_min + (box_h - 1) / 2.0

    return BoundingBox(
        x_min=abs_x_min,
        y_min=abs_y_min,
        x_max=abs_x_max,
        y_max=abs_y_max,
        width=box_w,
        height=box_h,
        center_x=center_x,
        center_y=center_y,
    )
