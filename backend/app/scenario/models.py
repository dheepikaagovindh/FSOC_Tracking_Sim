"""
Typed Configuration Models for FSOC Coarse Alignment Simulation Scenarios.
Team PHARO — SIH26169
"""

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


# Supported Enums / Literals
MotionProfileType = Literal["static", "drift", "sway", "orbit"]
BeaconTrajectoryType = Literal["static", "linear", "circular", "custom"]
DisturbanceSeverityType = Literal["off", "low", "medium", "high"]


class CameraConfig(BaseModel):
    """Configuration for virtual optical receiver camera model."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "width": 640,
                "height": 480,
                "horizontal_fov_deg": 30.0,
                "vertical_fov_deg": 22.5,
                "initial_pan_deg": 0.0,
                "initial_tilt_deg": 0.0,
            }
        }
    )
    width: int = Field(default=640, description="Sensor width in pixels", ge=64, le=7680)
    height: int = Field(default=480, description="Sensor height in pixels", ge=64, le=4320)
    horizontal_fov_deg: float = Field(default=30.0, description="Horizontal Field of View in degrees", gt=0.0, lt=180.0)
    vertical_fov_deg: float = Field(default=22.5, description="Vertical Field of View in degrees", gt=0.0, lt=180.0)
    initial_pan_deg: float = Field(default=0.0, description="Initial camera gimbal pan offset in degrees", ge=-180.0, le=180.0)
    initial_tilt_deg: float = Field(default=0.0, description="Initial camera gimbal tilt offset in degrees", ge=-90.0, le=90.0)



class PlatformConfig(BaseModel):
    """Kinematic configuration for a platform (optical terminal base)."""
    motion_profile: str = Field(default="static", description="Platform motion profile ('static', 'drift', 'sway', 'orbit')")
    initial_position_x: float = Field(default=0.0, description="Initial X coordinate in world frame (meters)")
    initial_position_y: float = Field(default=0.0, description="Initial Y coordinate in world frame (meters)")
    initial_position_z: float = Field(default=0.0, description="Initial Z coordinate in world frame (meters)")
    velocity_x: float = Field(default=0.0, description="Linear velocity X (m/s)")
    velocity_y: float = Field(default=0.0, description="Linear velocity Y (m/s)")
    velocity_z: float = Field(default=0.0, description="Linear velocity Z (m/s)")
    amplitude: float = Field(default=0.0, description="Oscillation/orbit amplitude (meters or degrees)", ge=0.0)
    frequency: float = Field(default=0.0, description="Oscillation/orbit frequency (Hz)", ge=0.0)

    @field_validator("motion_profile")
    @classmethod
    def validate_profile(cls, v: str) -> str:
        valid_profiles = {"static", "drift", "sway", "orbit"}
        val = v.lower().strip()
        if val not in valid_profiles:
            raise ValueError(f"Invalid motion profile '{v}'. Must be one of: {sorted(list(valid_profiles))}")
        return val


class BeaconConfig(BaseModel):
    """Optical transmitter beacon emission & trajectory configuration."""
    brightness: float = Field(default=1.0, description="Beacon normalized intensity / optical power", gt=0.0, le=100.0)
    size: float = Field(default=5.0, description="Beacon spot effective diameter (pixels/mm)", gt=0.0, le=500.0)
    trajectory: str = Field(default="static", description="Beacon relative trajectory ('static', 'linear', 'circular', 'custom')")
    trajectory_parameters: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary trajectory parameterization dictionary")

    @field_validator("trajectory")
    @classmethod
    def validate_trajectory(cls, v: str) -> str:
        valid_trajectories = {"static", "linear", "circular", "custom"}
        val = v.lower().strip()
        if val not in valid_trajectories:
            raise ValueError(f"Invalid beacon trajectory '{v}'. Must be one of: {sorted(list(valid_trajectories))}")
        return val


class DisturbanceConfig(BaseModel):
    """Environmental and mechanical disturbance injection configuration."""
    severity: str = Field(default="off", description="Master disturbance preset ('off', 'low', 'medium', 'high')")
    vibration_enabled: bool = Field(default=False, description="Enable platform micro-vibration dynamics")
    vibration_magnitude: float = Field(default=0.0, description="RMS vibration magnitude (pixels/deg)", ge=0.0)
    noise_enabled: bool = Field(default=False, description="Enable optical/sensor Gaussian noise")
    noise_magnitude: float = Field(default=0.0, description="Gaussian noise standard deviation", ge=0.0)
    blur_enabled: bool = Field(default=False, description="Enable optical atmospheric/motion blur")
    blur_strength: float = Field(default=0.0, description="Blur kernel size/sigma", ge=0.0)
    dropout_enabled: bool = Field(default=False, description="Enable scintillation / line-of-sight dropouts")
    dropout_probability: float = Field(default=0.0, description="Probability of beacon dropout per frame", ge=0.0, le=1.0)
    dropout_duration: float = Field(default=0.0, description="Mean dropout burst duration in seconds", ge=0.0)

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        valid_severities = {"off", "low", "medium", "high"}
        val = v.lower().strip()
        if val not in valid_severities:
            raise ValueError(f"Invalid disturbance severity '{v}'. Must be one of: {sorted(list(valid_severities))}")
        return val


class SimulationConfig(BaseModel):
    """Simulation execution and data logging configuration."""
    duration: float = Field(default=30.0, description="Total simulation duration in seconds", gt=0.0, le=3600.0)
    fps: float = Field(default=30.0, description="Simulation frames per second", gt=0.0, le=240.0)
    random_seed: int = Field(default=42, description="Random seed for reproducibility", ge=0)
    record_telemetry: bool = Field(default=True, description="Record time-series telemetry data")
    record_frames: bool = Field(default=False, description="Record raw synthetic video frames")


class ScenarioConfig(BaseModel):
    """
    Root Simulation Scenario Configuration Model for FSOC Coarse Alignment Simulator.
    Single Source of Truth across API, UI, and Future Simulation Engine.
    """
    scenario_name: str = Field(default="Easy Acquisition", description="Human-readable scenario title")
    description: Optional[str] = Field(default="Baseline coarse alignment scenario with clear conditions", description="Detailed description")
    camera: CameraConfig = Field(default_factory=CameraConfig, description="Optical receiver camera configuration")
    camera_platform: PlatformConfig = Field(default_factory=PlatformConfig, description="Receiver platform motion kinematics")
    beacon_platform: PlatformConfig = Field(
        default_factory=lambda: PlatformConfig(initial_position_z=1000.0),
        description="Beacon transmitter platform kinematics"
    )
    beacon: BeaconConfig = Field(default_factory=BeaconConfig, description="Transmitter optical beacon configuration")
    disturbances: DisturbanceConfig = Field(default_factory=DisturbanceConfig, description="Environmental disturbances")
    simulation: SimulationConfig = Field(default_factory=SimulationConfig, description="Simulation execution settings")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_name": "Easy Acquisition",
                "description": "Stationary transmitter and receiver with zero disturbance",
                "camera": {
                    "width": 640,
                    "height": 480,
                    "horizontal_fov_deg": 30.0,
                    "vertical_fov_deg": 22.5,
                    "initial_pan_deg": 0.0,
                    "initial_tilt_deg": 0.0,
                },
                "camera_platform": {
                    "motion_profile": "static",
                    "initial_position_x": 0.0,
                    "initial_position_y": 0.0,
                    "initial_position_z": 0.0,
                    "velocity_x": 0.0,
                    "velocity_y": 0.0,
                    "velocity_z": 0.0,
                    "amplitude": 0.0,
                    "frequency": 0.0,
                },
                "beacon_platform": {
                    "motion_profile": "static",
                    "initial_position_x": 0.0,
                    "initial_position_y": 0.0,
                    "initial_position_z": 1000.0,
                    "velocity_x": 0.0,
                    "velocity_y": 0.0,
                    "velocity_z": 0.0,
                    "amplitude": 0.0,
                    "frequency": 0.0,
                },
                "beacon": {
                    "brightness": 1.0,
                    "size": 5.0,
                    "trajectory": "static",
                    "trajectory_parameters": {},
                },
                "disturbances": {
                    "severity": "off",
                    "vibration_enabled": False,
                    "vibration_magnitude": 0.0,
                    "noise_enabled": False,
                    "noise_magnitude": 0.0,
                    "blur_enabled": False,
                    "blur_strength": 0.0,
                    "dropout_enabled": False,
                    "dropout_probability": 0.0,
                    "dropout_duration": 0.0,
                },
                "simulation": {
                    "duration": 30.0,
                    "fps": 30.0,
                    "random_seed": 42,
                    "record_telemetry": True,
                    "record_frames": False,
                },
            }
        }
    )

