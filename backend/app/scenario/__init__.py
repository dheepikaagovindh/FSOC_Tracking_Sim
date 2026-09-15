"""
Scenario Configuration Module.
Team PHARO — SIH26169
"""

from .models import (
    ScenarioConfig,
    CameraConfig,
    PlatformConfig,
    BeaconConfig,
    DisturbanceConfig,
    SimulationConfig,
)
from .presets import (
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
from .validator import ScenarioValidator, ValidationResult
from .service import ScenarioService, scenario_service
from .factory import ScenarioFactory

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
    "ScenarioService",
    "scenario_service",
    "ScenarioFactory",
]
