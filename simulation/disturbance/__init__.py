"""
Disturbance & Noise Simulation Package (Standalone Simulation Layer).
Team PHARO — SIH26169
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.disturbance.models import (
    NoiseMetadata,
    BlurMetadata,
    VibrationMetadata,
    DropoutMetadata,
    DisturbanceMetadata,
    DisturbanceFrame,
    DisturbanceStatus,
    DisturbanceTelemetry,
)
from app.disturbance.noise import apply_sensor_noise, compute_noise_sigma
from app.disturbance.blur import apply_image_blur
from app.disturbance.vibration import apply_image_vibration, calculate_vibration_offset
from app.disturbance.dropout import DropoutTracker, apply_beacon_dropout
from app.disturbance.processor import DisturbanceProcessor

__all__ = [
    "NoiseMetadata",
    "BlurMetadata",
    "VibrationMetadata",
    "DropoutMetadata",
    "DisturbanceMetadata",
    "DisturbanceFrame",
    "DisturbanceStatus",
    "DisturbanceTelemetry",
    "apply_sensor_noise",
    "compute_noise_sigma",
    "apply_image_blur",
    "apply_image_vibration",
    "calculate_vibration_offset",
    "DropoutTracker",
    "apply_beacon_dropout",
    "DisturbanceProcessor",
]
