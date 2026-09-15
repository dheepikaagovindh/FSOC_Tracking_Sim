"""
Simulator State Management.
Team PHARO — SIH26169

Thread-safe in-memory state tracking active scenario configuration and simulator lifecycle.
"""

from enum import Enum
import threading
import time
from typing import Any, Dict, Optional
from ..scenario.models import ScenarioConfig
from ..scenario.presets import get_easy_acquisition_preset
from ..scenario.validator import ValidationResult, ScenarioValidator


class SimulatorLifecycle(str, Enum):
    UNCONFIGURED = "UNCONFIGURED"
    CONFIGURED_READY = "SCENARIO_READY"
    SIMULATING = "SIMULATING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class SimulatorStateManager:
    """Singleton state manager for active scenario and simulation engine boundary."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SimulatorStateManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self._state_lock = threading.RLock()
        self._active_scenario: ScenarioConfig = get_easy_acquisition_preset()
        self._status: SimulatorLifecycle = SimulatorLifecycle.CONFIGURED_READY
        self._validation_result: ValidationResult = ScenarioValidator.validate(self._active_scenario)
        self._last_updated: float = time.time()
        self._execution_metadata: Dict[str, Any] = {
            "version": "0.1.0",
            "active_module": "Module 1 - Scenario Configuration",
            "pipeline_state": "READY_FOR_TRACKING_PIPELINE",
        }

    def get_scenario(self) -> ScenarioConfig:
        with self._state_lock:
            return self._active_scenario.model_copy(deep=True)

    def set_scenario(self, scenario: ScenarioConfig) -> ValidationResult:
        with self._state_lock:
            val_result = ScenarioValidator.validate(scenario)
            if val_result.is_valid:
                self._active_scenario = scenario.model_copy(deep=True)
                self._status = SimulatorLifecycle.CONFIGURED_READY
                self._validation_result = val_result
                self._last_updated = time.time()
            else:
                self._status = SimulatorLifecycle.ERROR
                self._validation_result = val_result
            return val_result

    def reset_to_default(self) -> ScenarioConfig:
        with self._state_lock:
            self._active_scenario = get_easy_acquisition_preset()
            self._validation_result = ScenarioValidator.validate(self._active_scenario)
            self._status = SimulatorLifecycle.CONFIGURED_READY
            self._last_updated = time.time()
            return self._active_scenario.model_copy(deep=True)

    def get_status(self) -> Dict[str, Any]:
        with self._state_lock:
            return {
                "status": self._status.value,
                "is_valid": self._validation_result.is_valid,
                "errors": self._validation_result.errors,
                "warnings": self._validation_result.warnings,
                "last_updated": self._last_updated,
                "scenario_name": self._active_scenario.scenario_name,
                "metadata": self._execution_metadata,
            }


# Singleton accessor
simulator_state = SimulatorStateManager()
