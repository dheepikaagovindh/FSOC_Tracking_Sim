"""
OpenCV Classical Beacon Detection & Centroiding Engine.
Team PHARO — SIH26169

Implements standard classical computer-vision optical beacon extraction:
Grayscale Preprocessing -> Dynamic/Otsu/Fixed Thresholding -> Morphological Cleanup ->
Contour/Blob Extraction -> Candidate Filtering & Scoring -> Sub-Pixel Centroiding.

STRICT BOUNDARY: Operates strictly on image pixels without access to ground truth.
"""

from __future__ import annotations
import math
import time
from typing import List, Optional, Tuple
import cv2
import numpy as np

from .base import BaseDetector
from .models import (
    DetectionConfig,
    DetectionResult,
    BoundingBox,
    CandidateInfo,
)
from .preprocessing import preprocess_image, validate_image_input


class OpenCVBeaconDetector(BaseDetector):
    """
    Classical OpenCV beacon spot detector and sub-pixel centroid estimator.
    """

    def __init__(self, config: Optional[DetectionConfig] = None):
        super().__init__(config=config or DetectionConfig())

    def detect(
        self,
        image: np.ndarray,
        timestamp: Optional[float] = None,
        config: Optional[DetectionConfig] = None,
    ) -> DetectionResult:
        """
        Execute classical OpenCV beacon detection pipeline on input image.
        """
        t_start = time.perf_counter()
        ts = timestamp if timestamp is not None else 0.0
        active_config = config or self._config

        # 1. Input Validation
        valid, err_msg = validate_image_input(image)
        if not valid:
            t_exec = (time.perf_counter() - t_start) * 1000.0
            return DetectionResult(
                detected=False,
                center_x=None,
                center_y=None,
                bbox=None,
                confidence=0.0,
                candidate_count=0,
                method="opencv",
                timestamp=ts,
                processing_time_ms=round(t_exec, 3),
                message=f"Invalid image input: {err_msg}",
            )

        # 2. Preprocessing
        try:
            gray = preprocess_image(image, blur_kernel=active_config.blur_kernel)
        except Exception as e:
            t_exec = (time.perf_counter() - t_start) * 1000.0
            return DetectionResult(
                detected=False,
                center_x=None,
                center_y=None,
                bbox=None,
                confidence=0.0,
                candidate_count=0,
                method="opencv",
                timestamp=ts,
                processing_time_ms=round(t_exec, 3),
                message=f"Preprocessing error: {str(e)}",
            )

        # 3. Background Statistics Estimation
        img_float = gray.astype(np.float64)
        mu_bg = float(np.median(img_float))
        mad = float(np.median(np.abs(img_float - mu_bg)))
        sigma_bg = max(1.4826 * mad, 0.5)

        # 4. Thresholding
        if active_config.use_otsu:
            thresh_val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif active_config.use_adaptive:
            adaptive_t = mu_bg + active_config.k_sigma * sigma_bg
            eff_thresh = max(adaptive_t, float(active_config.threshold), 3.0)
            thresh_val, binary = cv2.threshold(gray, int(eff_thresh), 255, cv2.THRESH_BINARY)
        else:
            thresh_val = float(active_config.threshold)
            _, binary = cv2.threshold(gray, int(thresh_val), 255, cv2.THRESH_BINARY)

        # 5. Morphological Cleanup
        if active_config.morphology_enabled:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # 6. Contour / Connected Components Extraction
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        valid_candidates: List[CandidateInfo] = []

        for idx, c in enumerate(contours):
            # Contour area
            area = float(cv2.contourArea(c))
            x, y, w, h = cv2.boundingRect(c)

            # Reject isolated 1-2px noise spikes (real spots have diameter >= 3px)
            if w < 3 or h < 3:
                continue

            if area < 1.0:
                area = float(w * h)

            # Aspect ratio
            aspect_ratio = float(w) / max(1.0, float(h))

            # Crop candidate patch from raw grayscale
            patch = gray[y : y + h, x : x + w]
            if patch.size == 0:
                continue

            mean_intensity = float(np.mean(patch))
            max_intensity = float(np.max(patch))

            # Contrast above background
            contrast = max_intensity - mu_bg
            pnr = contrast / max(sigma_bg, 1e-4)
            if contrast < 25.0 or pnr < 2.5:
                continue

            # Geometric / Intensity-Weighted Centroid
            M = cv2.moments(c)
            if M["m00"] > 1e-4:
                cx_geom = float(M["m10"] / M["m00"])
                cy_geom = float(M["m01"] / M["m00"])
            else:
                cx_geom = float(x + (w - 1) / 2.0)
                cy_geom = float(y + (h - 1) / 2.0)

            # Intensity-weighted sub-pixel refinement on local patch
            patch_weights = np.maximum(0.0, patch.astype(np.float64) - thresh_val)
            sum_weights = float(np.sum(patch_weights))
            if sum_weights > 1e-4:
                grid_y, grid_x = np.mgrid[0:h, 0:w]
                cx = float(x + np.sum(grid_x * patch_weights) / sum_weights)
                cy = float(y + np.sum(grid_y * patch_weights) / sum_weights)
            else:
                cx = cx_geom
                cy = cy_geom

            # 7. Candidate Filtering
            if area < active_config.min_area or area > active_config.max_area:
                continue
            if max_intensity < active_config.min_brightness:
                continue
            if aspect_ratio < active_config.min_aspect_ratio or aspect_ratio > active_config.max_aspect_ratio:
                continue

            # Shape Circularity / Compactness: 4*pi*area / perimeter^2
            perimeter = float(cv2.arcLength(c, True))
            if perimeter > 0:
                circularity = float(min(1.0, max(0.0, 4.0 * math.pi * area / (perimeter * perimeter))))
            else:
                circularity = 0.5

            # Candidate Scoring (NO GROUND TRUTH USED)
            norm_brightness = min(1.0, max(0.0, (max_intensity - mu_bg) / 200.0))
            pnr_norm = min(1.0, max(0.0, pnr / 10.0))
            score = 0.40 * norm_brightness + 0.35 * pnr_norm + 0.25 * circularity

            candidate_info = CandidateInfo(
                candidate_id=idx,
                bbox=BoundingBox(x=x, y=y, width=w, height=h),
                area=round(area, 2),
                center_x=round(cx, 3),
                center_y=round(cy, 3),
                mean_intensity=round(mean_intensity, 2),
                max_intensity=round(max_intensity, 2),
                aspect_ratio=round(aspect_ratio, 2),
                circularity=round(circularity, 3),
                score=round(score, 4),
            )
            valid_candidates.append(candidate_info)

        # 8. Evaluation & Selection
        if len(valid_candidates) == 0:
            t_exec = (time.perf_counter() - t_start) * 1000.0
            return DetectionResult(
                detected=False,
                center_x=None,
                center_y=None,
                bbox=None,
                confidence=0.0,
                candidate_count=0,
                method="opencv",
                timestamp=ts,
                processing_time_ms=round(t_exec, 3),
                message="No valid beacon candidate satisfied threshold and filtering criteria",
            )

        # Rank candidates by score descending
        valid_candidates.sort(key=lambda c: c.score, reverse=True)
        best_candidate = valid_candidates[0]

        # 9. Confidence Score Calculation (Heuristic [0.0, 1.0])
        best_pnr = (best_candidate.max_intensity - mu_bg) / max(sigma_bg, 1e-4)
        pnr_term = 1.0 / (1.0 + math.exp(-0.8 * (best_pnr - 4.5)))
        contrast_term = min(1.0, max(0.0, (best_candidate.max_intensity - mu_bg) / 128.0))
        shape_term = best_candidate.circularity

        confidence = 0.60 * pnr_term + 0.25 * contrast_term + 0.15 * shape_term
        confidence = float(min(1.0, max(0.0, round(confidence, 3))))

        t_exec = (time.perf_counter() - t_start) * 1000.0

        if confidence < active_config.min_confidence:
            return DetectionResult(
                detected=False,
                center_x=None,
                center_y=None,
                bbox=None,
                confidence=confidence,
                candidate_count=len(valid_candidates),
                candidates=valid_candidates if active_config.include_candidates else None,
                method="opencv",
                timestamp=ts,
                processing_time_ms=round(t_exec, 3),
                message=f"Candidate confidence ({confidence:.2f}) below minimum threshold ({active_config.min_confidence:.2f})",
            )

        return DetectionResult(
            detected=True,
            center_x=best_candidate.center_x,
            center_y=best_candidate.center_y,
            u=best_candidate.center_x,
            v=best_candidate.center_y,
            confidence=confidence,
            bbox=best_candidate.bbox,
            candidate_count=len(valid_candidates),
            selected_candidate=0,
            candidates=valid_candidates if active_config.include_candidates else None,
            method="opencv",
            timestamp=ts,
            processing_time_ms=round(t_exec, 3),
            message="Beacon successfully detected via OpenCV contour analysis",
        )
