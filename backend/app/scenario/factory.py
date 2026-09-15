"""
Scenario Initialization Factory.
Team PHARO — SIH26169

Translates a validated ScenarioConfig into clean initialization parameters
and runtime boundary objects for future simulation modules (World, Camera, Disturbances, etc.)
without implementing downstream tracking or physics algorithms prematurely.
"""

from typing import Any, Dict
from .models import ScenarioConfig


class ScenarioFactory:
    """
    Factory translating high-level ScenarioConfig into structured module initialization contracts.
    """

    @classmethod
    def build_simulation_context(cls, config: ScenarioConfig) -> Dict[str, Any]:
        """
        Generate initialized parameter dictionaries for downstream simulation modules.
        This provides a standardized integration contract when Module 2+ are connected.
        """
        return {
            "scenario_metadata": {
                "name": config.scenario_name,
                "description": config.description,
            },
            "world_initialization": {
                "camera_platform": {
                    "motion_profile": config.camera_platform.motion_profile,
                    "initial_position": (
                        config.camera_platform.initial_position_x,
                        config.camera_platform.initial_position_y,
                        config.camera_platform.initial_position_z,
                    ),
                    "velocity": (
                        config.camera_platform.velocity_x,
                        config.camera_platform.velocity_y,
                        config.camera_platform.velocity_z,
                    ),
                    "amplitude": config.camera_platform.amplitude,
                    "frequency": config.camera_platform.frequency,
                },
                "beacon_platform": {
                    "motion_profile": config.beacon_platform.motion_profile,
                    "initial_position": (
                        config.beacon_platform.initial_position_x,
                        config.beacon_platform.initial_position_y,
                        config.beacon_platform.initial_position_z,
                    ),
                    "velocity": (
                        config.beacon_platform.velocity_x,
                        config.beacon_platform.velocity_y,
                        config.beacon_platform.velocity_z,
                    ),
                    "amplitude": config.beacon_platform.amplitude,
                    "frequency": config.beacon_platform.frequency,
                },
                "beacon_emitter": {
                    "brightness": config.beacon.brightness,
                    "size": config.beacon.size,
                    "trajectory": config.beacon.trajectory,
                    "trajectory_parameters": config.beacon.trajectory_parameters,
                },
            },
            "camera_initialization": {
                "resolution": (config.camera.width, config.camera.height),
                "horizontal_fov_deg": config.camera.horizontal_fov_deg,
                "vertical_fov_deg": config.camera.vertical_fov_deg,
                "initial_pan_deg": config.camera.initial_pan_deg,
                "initial_tilt_deg": config.camera.initial_tilt_deg,
            },
            "disturbance_initialization": {
                "severity": config.disturbances.severity,
                "vibration": {
                    "enabled": config.disturbances.vibration_enabled,
                    "magnitude": config.disturbances.vibration_magnitude,
                },
                "sensor_noise": {
                    "enabled": config.disturbances.noise_enabled,
                    "magnitude": config.disturbances.noise_magnitude,
                },
                "optical_blur": {
                    "enabled": config.disturbances.blur_enabled,
                    "strength": config.disturbances.blur_strength,
                },
                "beacon_dropout": {
                    "enabled": config.disturbances.dropout_enabled,
                    "probability": config.disturbances.dropout_probability,
                    "duration": config.disturbances.dropout_duration,
                },
            },
            "simulation_runtime": {
                "duration_seconds": config.simulation.duration,
                "target_fps": config.simulation.fps,
                "dt": 1.0 / config.simulation.fps if config.simulation.fps > 0 else 0.0333,
                "total_frames": int(config.simulation.duration * config.simulation.fps),
                "random_seed": config.simulation.random_seed,
                "record_telemetry": config.simulation.record_telemetry,
                "record_frames": config.simulation.record_frames,
            },
            "status": "INITIALIZED_READY",
        }
