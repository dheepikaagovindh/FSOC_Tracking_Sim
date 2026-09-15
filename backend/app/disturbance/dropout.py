"""
Beacon Deep Fades & Atmospheric Dropout Simulation.
Team PHARO — SIH26169

Simulates atmospheric scintillation deep fades, beam blockage, and transient signal dropouts
without invoking any detector algorithm (using simulation ground-truth metadata).
"""

from __future__ import annotations
import math
from typing import Optional, Tuple
import numpy as np

from ..camera.models import CameraFrame
from .models import DropoutMetadata


class DropoutTracker:
    """
    Deterministic state tracker for burst duration and frame drop events.
    """

    def __init__(self):
        self._active: bool = False
        self._end_time: float = 0.0
        self._last_frame_index: int = -1

    def reset(self) -> None:
        """Reset dropout event state."""
        self._active = False
        self._end_time = 0.0
        self._last_frame_index = -1

    def update(
        self,
        timestamp: float,
        probability: float,
        duration: float,
        seed: int,
        frame_index: int,
        beacon_visible: bool,
    ) -> Tuple[bool, float]:
        """
        Evaluate instantaneous dropout state for the current frame.
        
        Guarantees:
          - probability = 0.0 -> never active.
          - probability = 1.0 -> always active when beacon is visible.
          - duration > 0.0 -> persists until timestamp >= trigger_time + duration.
          - 100% deterministic for identical (seed, frame_index, timestamp).
        """
        # Check if existing dropout has expired
        if self._active and timestamp >= self._end_time:
            self._active = False

        if not self._active and probability <= 0.0:
            return False, 0.0

        if not self._active and probability >= 1.0:
            self._active = beacon_visible
            effective_duration = max(1e-4, float(duration))
            self._end_time = timestamp + effective_duration
            rem = max(0.0, self._end_time - timestamp)
            return self._active, rem

        # Check for new trigger only once per distinct frame index if not already active
        if not self._active and beacon_visible and frame_index != self._last_frame_index:
            self._last_frame_index = frame_index
            # Derive deterministic pseudo-random roll
            roll_seed = (int(seed) * 5000011 + int(frame_index) * 123457 + 31) & 0xFFFFFFFF
            rng = np.random.default_rng(roll_seed)
            roll = float(rng.random())

            if roll < probability:
                self._active = True
                # If duration <= 0, drop lasts for instantaneous frame (e.g. 1/30s)
                effective_duration = max(1e-4, float(duration))
                self._end_time = timestamp + effective_duration

        remaining = max(0.0, self._end_time - timestamp) if self._active else 0.0
        return self._active, remaining


def apply_beacon_dropout(
    image: np.ndarray,
    tracker: DropoutTracker,
    camera_frame: Optional[CameraFrame],
    probability: float,
    duration: float,
    timestamp: float,
    seed: int = 42,
    frame_index: int = 0,
    enabled: bool = True,
) -> Tuple[np.ndarray, DropoutMetadata]:
    """
    Apply localized beacon spot occlusion / suppression if a dropout event is active.
    
    Parameters:
      image: Input 2D uint8 NumPy grayscale sensor image.
      tracker: DropoutTracker instance maintaining state over time.
      camera_frame: Camera frame metadata containing ground-truth projected beacon (u, v).
      probability: Dropout probability in [0, 1].
      duration: Dropout burst duration in seconds.
      timestamp: Simulation timestamp in seconds.
      seed: Random seed for reproducibility.
      frame_index: Discrete simulation frame counter.
      enabled: Boolean flag to enable/disable dropout.
      
    Guarantees:
      - Uses simulation ground-truth metadata, NO computer vision detector.
      - Dimensions and uint8 dtype preserved.
    """
    if not enabled:
        return image.copy(), DropoutMetadata(
            enabled=False,
            probability=max(0.0, min(1.0, probability)),
            duration=max(0.0, duration),
            active=False,
            remaining_duration=0.0,
            applied=False,
        )

    prob_clamped = max(0.0, min(1.0, probability))
    dur_clamped = max(0.0, duration)

    beacon_visible = camera_frame.visible if camera_frame is not None else True
    is_active, remaining = tracker.update(
        timestamp=timestamp,
        probability=prob_clamped,
        duration=dur_clamped,
        seed=seed,
        frame_index=frame_index,
        beacon_visible=beacon_visible,
    )

    if not is_active:
        return image.copy(), DropoutMetadata(
            enabled=True,
            probability=prob_clamped,
            duration=dur_clamped,
            active=False,
            remaining_duration=0.0,
            applied=False,
        )

    # Occlude/suppress the beacon spot from the sensor frame
    disturbed_image = image.copy()
    applied = False

    if camera_frame is not None and camera_frame.visible:
        u = camera_frame.projection.u
        v = camera_frame.projection.v
        spot_r = getattr(camera_frame, "spot_radius", 3.0)
        occlusion_radius = max(6.0, spot_r * 2.5)

        height, width = disturbed_image.shape
        r_int = int(math.ceil(occlusion_radius))
        u_min = max(0, int(math.floor(u - r_int)))
        u_max = min(width - 1, int(math.ceil(u + r_int)))
        v_min = max(0, int(math.floor(v - r_int)))
        v_max = min(height - 1, int(math.ceil(v + r_int)))

        if u_min <= u_max and v_min <= v_max:
            y_coords, x_coords = np.ogrid[v_min:v_max + 1, u_min:u_max + 1]
            dist_sq = (x_coords - u) ** 2 + (y_coords - v) ** 2
            mask = dist_sq <= (occlusion_radius ** 2)
            patch = disturbed_image[v_min:v_max + 1, u_min:u_max + 1]
            # Zero out the spot region (sensor background)
            patch[mask] = 0
            disturbed_image[v_min:v_max + 1, u_min:u_max + 1] = patch
            applied = True
    else:
        applied = False

    return disturbed_image, DropoutMetadata(
        enabled=True,
        probability=prob_clamped,
        duration=dur_clamped,
        active=True,
        remaining_duration=remaining,
        applied=applied,
    )
