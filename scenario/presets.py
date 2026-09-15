"""
Scenario Presets (Root Alias).
Team PHARO — SIH26169
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.scenario.presets import (
    get_preset,
    list_available_presets,
    get_easy_acquisition_preset,
    get_moving_beacon_preset,
    get_platform_drift_preset,
    get_high_vibration_preset,
    get_beacon_dropout_preset,
    get_full_stress_test_preset,
    get_custom_preset,
    PRESET_FACTORIES,
)

__all__ = [
    "get_preset",
    "list_available_presets",
    "get_easy_acquisition_preset",
    "get_moving_beacon_preset",
    "get_platform_drift_preset",
    "get_high_vibration_preset",
    "get_beacon_dropout_preset",
    "get_full_stress_test_preset",
    "get_custom_preset",
    "PRESET_FACTORIES",
]
