"""
Signal Quality, Noise, and Detection Confidence Metrics.
Team PHARO — SIH26169

Computes:
- Peak-to-Noise Ratio (PNR)
- Signal-to-Noise Ratio (SNR) in dB
- Integrated optical spot flux
- Composite detection confidence score (0.0 to 1.0)
"""

from __future__ import annotations
import math
import numpy as np

from .models import SignalMetrics


def calculate_signal_metrics(
    image: np.ndarray,
    roi: np.ndarray,
    peak_val: float,
    mu_bg: float,
    sigma_bg: float,
    threshold: float,
    flux: float,
    detected: bool,
) -> SignalMetrics:
    """
    Calculate optical signal quality metrics from sensor image and ROI.
    """
    sigma_safe = max(sigma_bg, 1e-4)
    pnr = max(0.0, (peak_val - mu_bg) / sigma_safe)

    # Estimate noise power over equivalent spot area (e.g. ROI area or spot area)
    roi_area = float(roi.size) if roi is not None and roi.size > 0 else 25.0
    noise_power = max(roi_area * (sigma_safe ** 2), 1e-3)
    signal_energy = max(flux, 1e-3)

    if detected and flux > 0.0:
        snr_ratio = signal_energy / noise_power
        snr_db = 10.0 * math.log10(max(snr_ratio, 1e-6))
    else:
        snr_db = -20.0

    # Detection confidence score c in [0.0, 1.0]
    if detected and pnr > 0.5:
        # Sigmoidal response to PNR
        pnr_term = 1.0 / (1.0 + math.exp(-0.7 * (pnr - 3.0)))
        # Contrast factor
        contrast_term = min(1.0, max(0.0, (peak_val - mu_bg) / 128.0))
        # Flux factor
        flux_term = 1.0 / (1.0 + math.exp(-0.05 * (flux - 5.0)))

        confidence = 0.60 * pnr_term + 0.25 * contrast_term + 0.15 * flux_term
        confidence = float(min(1.0, max(0.0, round(confidence, 4))))
    else:
        confidence = 0.0

    return SignalMetrics(
        peak_intensity=round(float(peak_val), 2),
        background_mean=round(float(mu_bg), 2),
        background_std=round(float(sigma_bg), 2),
        threshold=round(float(threshold), 2),
        pnr=round(float(pnr), 2),
        snr_db=round(float(snr_db), 2),
        flux=round(float(flux), 2),
        confidence=confidence,
    )
