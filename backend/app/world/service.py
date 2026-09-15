"""
World Simulation Service Layer.
Team PHARO — SIH26169

Provides thread-safe singleton state and business service operations for the Virtual World simulation.
"""

from __future__ import annotations
import threading
from typing import Optional
from .world import World
from .models import WorldState, WorldStatus, PlatformState, RelativeGeometry
from ..scenario.models import ScenarioConfig
from ..scenario.service import scenario_service


class WorldService:
    """Singleton service orchestrating Virtual World simulation instances and API interactions."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(WorldService, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self._mutex = threading.RLock()
        # Initialize world with active scenario on boot
        active_scenario = scenario_service.get_active_scenario()
        self._world = World(active_scenario)

    def initialize_world(self, scenario: Optional[ScenarioConfig] = None) -> WorldState:
        """Initialize or re-initialize world state from ScenarioConfig."""
        with self._mutex:
            target_scenario = scenario or scenario_service.get_active_scenario()
            self._world.initialize_from_scenario(target_scenario)
            return self._world.get_state()

    def reset_world(self) -> WorldState:
        """Reset simulation clock to t=0 and re-evaluate initial state."""
        with self._mutex:
            return self._world.reset()

    def step_world(self, dt: Optional[float] = None) -> WorldState:
        """Advance simulation clock by dt."""
        with self._mutex:
            return self._world.update(dt)

    def set_world_time(self, t: float) -> WorldState:
        """Set explicit simulation clock time."""
        with self._mutex:
            return self._world.set_time(t)

    def get_world_state(self) -> WorldState:
        """Retrieve current ground-truth world state."""
        with self._mutex:
            return self._world.get_state()

    def get_platform_state(self, platform_id: str) -> PlatformState:
        """Retrieve state for a specific platform ('camera' or 'beacon')."""
        with self._mutex:
            return self._world.get_platform_state(platform_id)

    def get_geometry(self) -> RelativeGeometry:
        """Retrieve current ground-truth relative geometry."""
        with self._mutex:
            return self._world.get_relative_geometry()

    def get_status(self) -> WorldStatus:
        """Retrieve world simulation status and metadata."""
        with self._mutex:
            return self._world.get_status()


# Singleton service instance
world_service = WorldService()
