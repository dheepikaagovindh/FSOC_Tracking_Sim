"""
Platform Abstraction for Optical Terminals.
Team PHARO — SIH26169
"""

from __future__ import annotations
from typing import Any, Dict
from .models import PlatformDefinition, PlatformState, Vector3D
from .motion import MotionEngine


class Platform:
    """
    Represents an individual optical terminal base platform (Receiver or Transmitter).
    Provides instantaneous state evaluation given simulation timestamp t.
    """

    def __init__(self, definition: PlatformDefinition):
        self.definition = definition

    @property
    def id(self) -> str:
        return self.definition.id

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def motion_profile(self) -> str:
        return self.definition.motion_profile

    def get_state(self, t: float) -> PlatformState:
        """Calculate and return full PlatformState at simulation time t."""
        pos, vel = MotionEngine.calculate_state(self.definition, t)
        return PlatformState(
            platform_id=self.definition.id,
            name=self.definition.name,
            timestamp=t,
            position=pos,
            velocity=vel,
            motion_profile=self.definition.motion_profile,
        )

    def get_position(self, t: float) -> Vector3D:
        """Calculate and return only position Vector3D at simulation time t."""
        pos, _ = MotionEngine.calculate_state(self.definition, t)
        return pos

    def get_velocity(self, t: float) -> Vector3D:
        """Calculate and return only velocity Vector3D at simulation time t."""
        _, vel = MotionEngine.calculate_state(self.definition, t)
        return vel
