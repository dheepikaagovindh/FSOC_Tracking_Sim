"""
Motion Profile Calculations & Kinematics Engine.
Team PHARO — SIH26169

Pure functional deterministic evaluation of platform positions and analytical velocities.
"""

from __future__ import annotations
import math
from typing import Tuple
from .models import PlatformDefinition, Vector3D


class MotionProfile:
    """Base interface for platform kinematic motion calculations."""

    @classmethod
    def calculate(cls, definition: PlatformDefinition, t: float) -> Tuple[Vector3D, Vector3D]:
        """
        Calculate position and velocity at simulation time t.
        Returns: (position: Vector3D, velocity: Vector3D)
        """
        raise NotImplementedError


class StaticMotionProfile(MotionProfile):
    """
    STATIC Profile:
      P(t) = P0
      V(t) = (0, 0, 0)
    """
    @classmethod
    def calculate(cls, definition: PlatformDefinition, t: float) -> Tuple[Vector3D, Vector3D]:
        pos = Vector3D(
            x=definition.initial_position.x,
            y=definition.initial_position.y,
            z=definition.initial_position.z,
        )
        vel = Vector3D(x=0.0, y=0.0, z=0.0)
        return pos, vel


class DriftMotionProfile(MotionProfile):
    """
    DRIFT Profile (Constant Linear Velocity):
      P(t) = P0 + V0 * t
      V(t) = V0
    """
    @classmethod
    def calculate(cls, definition: PlatformDefinition, t: float) -> Tuple[Vector3D, Vector3D]:
        vx = definition.velocity.x
        vy = definition.velocity.y
        vz = definition.velocity.z

        pos = Vector3D(
            x=definition.initial_position.x + vx * t,
            y=definition.initial_position.y + vy * t,
            z=definition.initial_position.z + vz * t,
        )
        vel = Vector3D(x=vx, y=vy, z=vz)
        return pos, vel


class SwayMotionProfile(MotionProfile):
    """
    SWAY Profile (Sinusoidal Harmonic Oscillation):
      x(t) = x0 + Ax * sin(2*pi*f*t + phi_x)
      y(t) = y0 + Ay * sin(2*pi*f*t + phi_y)
      z(t) = z0 + Az * sin(2*pi*f*t + phi_z)

    Analytical Velocities:
      vx(t) = Ax * 2*pi*f * cos(2*pi*f*t + phi_x)
      vy(t) = Ay * 2*pi*f * cos(2*pi*f*t + phi_y)
      vz(t) = Az * 2*pi*f * cos(2*pi*f*t + phi_z)
    """
    @classmethod
    def calculate(cls, definition: PlatformDefinition, t: float) -> Tuple[Vector3D, Vector3D]:
        f = definition.frequency
        if f <= 0.0 or definition.amplitude <= 0.0:
            return (
                Vector3D(
                    x=definition.initial_position.x,
                    y=definition.initial_position.y,
                    z=definition.initial_position.z,
                ),
                Vector3D(x=0.0, y=0.0, z=0.0),
            )

        omega = 2.0 * math.pi * f

        # Check for independent axis amplitudes in parameters, or fallback to default distribution
        params = definition.parameters or {}
        ax = float(params.get("amplitude_x", definition.amplitude))
        ay = float(params.get("amplitude_y", 0.0))
        az = float(params.get("amplitude_z", 0.0))

        phi_x = float(params.get("phase_x", 0.0))
        phi_y = float(params.get("phase_y", 0.0))
        phi_z = float(params.get("phase_z", 0.0))

        # Position calculation
        px = definition.initial_position.x + ax * math.sin(omega * t + phi_x)
        py = definition.initial_position.y + ay * math.sin(omega * t + phi_y)
        pz = definition.initial_position.z + az * math.sin(omega * t + phi_z)

        # Analytical velocity calculation
        vx = ax * omega * math.cos(omega * t + phi_x)
        vy = ay * omega * math.cos(omega * t + phi_y)
        vz = az * omega * math.cos(omega * t + phi_z)

        return Vector3D(x=px, y=py, z=pz), Vector3D(x=vx, y=vy, z=vz)


class OrbitMotionProfile(MotionProfile):
    """
    ORBIT Profile (Circular / Elliptical Motion in X-Z plane):
      x(t) = cx + R * cos(2*pi*f*t + phi)
      z(t) = cz + R * sin(2*pi*f*t + phi)
      y(t) = cy

    Analytical Velocities:
      vx(t) = -R * 2*pi*f * sin(2*pi*f*t + phi)
      vz(t) =  R * 2*pi*f * cos(2*pi*f*t + phi)
      vy(t) = 0
    """
    @classmethod
    def calculate(cls, definition: PlatformDefinition, t: float) -> Tuple[Vector3D, Vector3D]:
        f = definition.frequency
        r = definition.amplitude

        if f <= 0.0 or r <= 0.0:
            return (
                Vector3D(
                    x=definition.initial_position.x,
                    y=definition.initial_position.y,
                    z=definition.initial_position.z,
                ),
                Vector3D(x=0.0, y=0.0, z=0.0),
            )

        omega = 2.0 * math.pi * f
        params = definition.parameters or {}
        phi = float(params.get("phase", 0.0))

        cx = definition.initial_position.x
        cy = definition.initial_position.y
        cz = definition.initial_position.z

        # Position
        px = cx + r * math.cos(omega * t + phi)
        py = cy
        pz = cz + r * math.sin(omega * t + phi)

        # Analytical Velocity
        vx = -r * omega * math.sin(omega * t + phi)
        vy = 0.0
        vz = r * omega * math.cos(omega * t + phi)

        return Vector3D(x=px, y=py, z=pz), Vector3D(x=vx, y=vy, z=vz)


class MotionEngine:
    """Dispatcher and evaluator for platform kinematic calculations."""

    _PROFILES = {
        "static": StaticMotionProfile,
        "drift": DriftMotionProfile,
        "sway": SwayMotionProfile,
        "orbit": OrbitMotionProfile,
    }

    @classmethod
    def calculate_state(cls, definition: PlatformDefinition, t: float) -> Tuple[Vector3D, Vector3D]:
        profile_key = definition.motion_profile.strip().lower()
        profile_cls = cls._PROFILES.get(profile_key, StaticMotionProfile)
        return profile_cls.calculate(definition, t)
