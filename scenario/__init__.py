"""
Root Scenario Module Entrypoint.
Team PHARO — SIH26169
"""

import os
import sys

# Ensure backend/app is importable
backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.scenario.models import (
    ScenarioConfig,
    CameraConfig,
    PlatformConfig,
    BeaconConfig,
    DisturbanceConfig,
    SimulationConfig,
)
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
)
from app.scenario.validator import ScenarioValidator, ValidationResult
from app.scenario.factory import ScenarioFactory
from app.scenario.service import ScenarioService, scenario_service

__all__ = [
    "ScenarioConfig",
    "CameraConfig",
    "PlatformConfig",
    "BeaconConfig",
    "DisturbanceConfig",
    "SimulationConfig",
    "get_preset",
    "list_available_presets",
    "get_easy_acquisition_preset",
    "get_moving_beacon_preset",
    "get_platform_drift_preset",
    "get_high_vibration_preset",
    "get_beacon_dropout_preset",
    "get_full_stress_test_preset",
    "get_custom_preset",
    "ScenarioValidator",
    "ValidationResult",
    "ScenarioFactory",
    "ScenarioService",
    "scenario_service",
]
