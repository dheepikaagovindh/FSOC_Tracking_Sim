"""
Scenario Configuration Service Layer.
Team PHARO — SIH26169

Encapsulates business operations for simulation scenarios:
Loading, Validating, Mutating, and Transitioning to Simulation Initialization.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from .models import ScenarioConfig
from .presets import get_preset, list_available_presets, get_easy_acquisition_preset
from .validator import ScenarioValidator, ValidationResult
from ..core.state import simulator_state, SimulatorLifecycle


class ScenarioService:
    """Service handling scenario lifecycle, presets, and validation."""

    def __init__(self):
        self._state = simulator_state

    def get_active_scenario(self) -> ScenarioConfig:
        """Fetch currently active scenario configuration."""
        return self._state.get_scenario()

    def update_scenario(self, scenario: Union[ScenarioConfig, Dict[str, Any]]) -> Tuple[Optional[ScenarioConfig], ValidationResult]:
        """Validate and apply a new scenario configuration."""
        if isinstance(scenario, dict):
            config, val_result = ScenarioValidator.validate_dict(scenario)
            if not val_result.is_valid or config is None:
                return None, val_result
        else:
            config = scenario
            val_result = ScenarioValidator.validate(config)
            if not val_result.is_valid:
                return None, val_result

        # Store in state
        self._state.set_scenario(config)
        return config, val_result

    def load_preset(self, preset_name: str) -> Tuple[ScenarioConfig, ValidationResult]:
        """Load a predefined scenario preset into the active state."""
        preset_config = get_preset(preset_name)
        val_result = self._state.set_scenario(preset_config)
        return preset_config, val_result

    def reset_scenario(self) -> ScenarioConfig:
        """Reset scenario back to baseline Easy Acquisition preset."""
        return self._state.reset_to_default()

    def list_presets(self) -> List[Dict[str, str]]:
        """List all available presets with metadata."""
        return list_available_presets()

    def validate_scenario(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate scenario without mutating active state."""
        _, val_result = ScenarioValidator.validate_dict(data)
        return val_result

    def get_simulator_status(self) -> Dict[str, Any]:
        """Get simulation status and metadata."""
        return self._state.get_status()


# Singleton service instance
scenario_service = ScenarioService()
