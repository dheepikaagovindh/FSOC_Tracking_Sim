"""
Disturbance & Noise Simulation Module.
Team PHARO — SIH26169
"""

from .models import (
    NoiseMetadata,
    BlurMetadata,
    VibrationMetadata,
    DropoutMetadata,
    DisturbanceMetadata,
    DisturbanceFrame,
    DisturbanceStatus,
    DisturbanceTelemetry,
)
from .noise import apply_sensor_noise, compute_noise_sigma
from .blur import apply_image_blur
from .vibration import apply_image_vibration, calculate_vibration_offset
from .dropout import DropoutTracker, apply_beacon_dropout
from .processor import DisturbanceProcessor
from .service import DisturbanceService, disturbance_service

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
    "DisturbanceService",
    "disturbance_service",
]
