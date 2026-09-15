"""
Disturbance Processor Engine.
Team PHARO — SIH26169

Coordinates the multi-stage environmental and sensor disturbance pipeline:
Clean Image -> Vibration/Jitter -> Optical Blur -> Sensor Noise -> Beacon Dropout -> Disturbed Image.
"""

from __future__ import annotations
from typing import Optional, Tuple
import numpy as np

from ..scenario.models import DisturbanceConfig
from ..camera.models import CameraFrame
from .models import (
    DisturbanceMetadata,
    NoiseMetadata,
    BlurMetadata,
    VibrationMetadata,
    DropoutMetadata,
)
from .noise import apply_sensor_noise
from .blur import apply_image_blur
from .vibration import apply_image_vibration
from .dropout import DropoutTracker, apply_beacon_dropout


class DisturbanceProcessor:
    """
    Central disturbance processing engine applying configurable optical and sensor imperfections.
    """

    def __init__(self):
        self._dropout_tracker = DropoutTracker()

    def reset(self) -> None:
        """Reset internal temporal and stochastic state."""
        self._dropout_tracker.reset()

    @staticmethod
    def resolve_effective_config(config: DisturbanceConfig) -> DisturbanceConfig:
        """
        Merge severity preset defaults with any explicitly configured parameters.
        """
        sev = config.severity.lower().strip()
        if sev == "off":
            return DisturbanceConfig(
                severity="off",
                vibration_enabled=False,
                vibration_magnitude=0.0,
                noise_enabled=False,
                noise_magnitude=0.0,
                blur_enabled=False,
                blur_strength=0.0,
                dropout_enabled=False,
                dropout_probability=0.0,
                dropout_duration=0.0,
            )

        # Base templates for named presets
        preset_defaults = {
            "low": {
                "vibration_enabled": True,
                "vibration_magnitude": 1.0,
                "noise_enabled": True,
                "noise_magnitude": 0.05,
                "blur_enabled": True,
                "blur_strength": 1.0,
                "dropout_enabled": True,
                "dropout_probability": 0.05,
                "dropout_duration": 0.2,
            },
            "medium": {
                "vibration_enabled": True,
                "vibration_magnitude": 3.0,
                "noise_enabled": True,
                "noise_magnitude": 0.12,
                "blur_enabled": True,
                "blur_strength": 2.0,
                "dropout_enabled": True,
                "dropout_probability": 0.15,
                "dropout_duration": 0.4,
            },
            "high": {
                "vibration_enabled": True,
                "vibration_magnitude": 6.0,
                "noise_enabled": True,
                "noise_magnitude": 0.25,
                "blur_enabled": True,
                "blur_strength": 3.5,
                "dropout_enabled": True,
                "dropout_probability": 0.30,
                "dropout_duration": 0.6,
            },
        }

        defaults = preset_defaults.get(sev, preset_defaults["medium"])

        vibration_en = config.vibration_enabled or defaults["vibration_enabled"]
        vibration_mag = config.vibration_magnitude if config.vibration_magnitude > 0 else defaults["vibration_magnitude"]

        noise_en = config.noise_enabled or defaults["noise_enabled"]
        noise_mag = config.noise_magnitude if config.noise_magnitude > 0 else defaults["noise_magnitude"]

        blur_en = config.blur_enabled or defaults["blur_enabled"]
        blur_str = config.blur_strength if config.blur_strength > 0 else defaults["blur_strength"]

        dropout_en = config.dropout_enabled or defaults["dropout_enabled"]
        dropout_prob = config.dropout_probability if config.dropout_probability > 0 else defaults["dropout_probability"]
        dropout_dur = config.dropout_duration if config.dropout_duration > 0 else defaults["dropout_duration"]

        return DisturbanceConfig(
            severity=sev,
            vibration_enabled=vibration_en,
            vibration_magnitude=vibration_mag,
            noise_enabled=noise_en,
            noise_magnitude=noise_mag,
            blur_enabled=blur_en,
            blur_strength=blur_str,
            dropout_enabled=dropout_en,
            dropout_probability=dropout_prob,
            dropout_duration=dropout_dur,
        )

    def process(
        self,
        clean_image: np.ndarray,
        config: DisturbanceConfig,
        timestamp: float,
        fps: float = 30.0,
        seed: int = 42,
        camera_frame: Optional[CameraFrame] = None,
    ) -> Tuple[np.ndarray, DisturbanceMetadata]:
        """
        Execute full disturbance processing pipeline on a clean optical camera frame.
        
        Pipeline:
          1. Vibration / Image Jitter
          2. Optical Blur
          3. Sensor Noise
          4. Beacon Dropout
          
        Guarantees:
          - Output shape and uint8 dtype match clean_image.
          - Deterministic results for identical (clean_image, config, timestamp, seed).
        """
        frame_index = int(round(max(0.0, timestamp) * max(1.0, fps)))
        sev = config.severity.lower().strip()

        # Fast path for OFF severity with all effects disabled
        if sev == "off" and not (config.vibration_enabled or config.noise_enabled or config.blur_enabled or config.dropout_enabled):
            meta = DisturbanceMetadata(
                severity="off",
                noise=NoiseMetadata(enabled=False, magnitude=0.0, sigma=0.0, applied=False),
                blur=BlurMetadata(enabled=False, strength=0.0, kernel_size=1, applied=False),
                vibration=VibrationMetadata(enabled=False, magnitude=0.0, offset_x=0.0, offset_y=0.0, applied=False),
                dropout=DropoutMetadata(enabled=False, probability=0.0, duration=0.0, active=False, remaining_duration=0.0, applied=False),
                random_seed=seed,
                frame_index=frame_index,
                applied_effects_count=0,
            )
            return clean_image.copy(), meta

        eff_config = self.resolve_effective_config(config)

        current_img = clean_image.copy()
        applied_count = 0

        # 1. Image Vibration / Jitter
        current_img, vib_meta = apply_image_vibration(
            image=current_img,
            magnitude=eff_config.vibration_magnitude,
            timestamp=timestamp,
            enabled=eff_config.vibration_enabled,
        )
        if vib_meta.applied:
            applied_count += 1

        # 2. Optical Blur
        current_img, blur_meta = apply_image_blur(
            image=current_img,
            blur_strength=eff_config.blur_strength,
            enabled=eff_config.blur_enabled,
        )
        if blur_meta.applied:
            applied_count += 1

        # 3. Sensor Noise
        current_img, noise_meta = apply_sensor_noise(
            image=current_img,
            magnitude=eff_config.noise_magnitude,
            enabled=eff_config.noise_enabled,
            seed=seed,
            frame_index=frame_index,
        )
        if noise_meta.applied:
            applied_count += 1

        # 4. Beacon Dropout
        current_img, drop_meta = apply_beacon_dropout(
            image=current_img,
            tracker=self._dropout_tracker,
            camera_frame=camera_frame,
            probability=eff_config.dropout_probability,
            duration=eff_config.dropout_duration,
            timestamp=timestamp,
            seed=seed,
            frame_index=frame_index,
            enabled=eff_config.dropout_enabled,
        )
        if drop_meta.applied:
            applied_count += 1

        meta = DisturbanceMetadata(
            severity=eff_config.severity,
            noise=noise_meta,
            blur=blur_meta,
            vibration=vib_meta,
            dropout=drop_meta,
            random_seed=seed,
            frame_index=frame_index,
            applied_effects_count=applied_count,
        )

        return current_img, meta
