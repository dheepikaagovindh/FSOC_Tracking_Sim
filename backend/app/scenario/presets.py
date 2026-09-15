"""
Predefined Scenario Presets for FSOC Coarse Alignment Simulation.
Team PHARO — SIH26169

Progressive Difficulty:
1. Easy Acquisition (Baseline)
2. Moving Beacon (Transmitter Kinematics)
3. Platform Drift (Terminal Drift & Sway)
4. High Vibration (Mechanical / Engine Jitter)
5. Beacon Dropout (Scintillation / Atmospheric Interruption)
6. Full Stress Test (All Disturbances Active)
7. Custom (User-defined)
"""

from typing import Dict, List
from .models import (
    ScenarioConfig,
    CameraConfig,
    PlatformConfig,
    BeaconConfig,
    DisturbanceConfig,
    SimulationConfig,
)


def get_easy_acquisition_preset() -> ScenarioConfig:
    """1. Easy Acquisition: Baseline stationary scenario with clear line of sight."""
    return ScenarioConfig(
        scenario_name="Easy Acquisition",
        description="Stationary receiver and transmitter terminals with zero disturbances. Ideal for initial algorithm calibration.",
        camera=CameraConfig(
            width=640,
            height=480,
            horizontal_fov_deg=30.0,
            vertical_fov_deg=22.5,
            initial_pan_deg=0.0,
            initial_tilt_deg=0.0,
        ),
        camera_platform=PlatformConfig(
            motion_profile="static",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=0.0,
            velocity_x=0.0,
            velocity_y=0.0,
            velocity_z=0.0,
            amplitude=0.0,
            frequency=0.0,
        ),
        beacon_platform=PlatformConfig(
            motion_profile="static",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=1000.0,
            velocity_x=0.0,
            velocity_y=0.0,
            velocity_z=0.0,
            amplitude=0.0,
            frequency=0.0,
        ),
        beacon=BeaconConfig(
            brightness=1.0,
            size=6.0,
            trajectory="static",
            trajectory_parameters={},
        ),
        disturbances=DisturbanceConfig(
            severity="off",
            vibration_enabled=False,
            vibration_magnitude=0.0,
            noise_enabled=False,
            noise_magnitude=0.0,
            blur_enabled=False,
            blur_strength=0.0,
            dropout_enabled=False,
            dropout_probability=0.0,
            dropout_duration=0.0,
        ),
        simulation=SimulationConfig(
            duration=30.0,
            fps=30.0,
            random_seed=42,
            record_telemetry=True,
            record_frames=False,
        ),
    )


def get_moving_beacon_preset() -> ScenarioConfig:
    """2. Moving Beacon: Transmitter platform moving linearly across field of view."""
    return ScenarioConfig(
        scenario_name="Moving Beacon",
        description="Beacon platform drifts linearly across the field of view with mild sensor noise. Tests velocity tracking.",
        camera=CameraConfig(
            width=640,
            height=480,
            horizontal_fov_deg=30.0,
            vertical_fov_deg=22.5,
            initial_pan_deg=0.0,
            initial_tilt_deg=0.0,
        ),
        camera_platform=PlatformConfig(
            motion_profile="static",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=0.0,
        ),
        beacon_platform=PlatformConfig(
            motion_profile="drift",
            initial_position_x=-15.0,
            initial_position_y=5.0,
            initial_position_z=1000.0,
            velocity_x=2.5,
            velocity_y=-0.5,
            velocity_z=0.0,
            amplitude=0.0,
            frequency=0.0,
        ),
        beacon=BeaconConfig(
            brightness=1.2,
            size=5.0,
            trajectory="linear",
            trajectory_parameters={"heading_deg": 15.0, "speed_mps": 2.5},
        ),
        disturbances=DisturbanceConfig(
            severity="low",
            vibration_enabled=False,
            vibration_magnitude=0.0,
            noise_enabled=True,
            noise_magnitude=0.05,
            blur_enabled=False,
            blur_strength=0.0,
            dropout_enabled=False,
            dropout_probability=0.0,
            dropout_duration=0.0,
        ),
        simulation=SimulationConfig(
            duration=30.0,
            fps=30.0,
            random_seed=42,
            record_telemetry=True,
            record_frames=False,
        ),
    )


def get_platform_drift_preset() -> ScenarioConfig:
    """3. Platform Drift: Both receiver and transmitter experience drift and sway dynamics."""
    return ScenarioConfig(
        scenario_name="Platform Drift",
        description="Receiver base drifts while beacon terminal sways sinusoidally. Tests continuous closed-loop compensation.",
        camera=CameraConfig(
            width=640,
            height=480,
            horizontal_fov_deg=30.0,
            vertical_fov_deg=22.5,
            initial_pan_deg=2.0,
            initial_tilt_deg=-1.5,
        ),
        camera_platform=PlatformConfig(
            motion_profile="drift",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=0.0,
            velocity_x=-0.8,
            velocity_y=1.2,
            velocity_z=0.0,
            amplitude=0.0,
            frequency=0.0,
        ),
        beacon_platform=PlatformConfig(
            motion_profile="sway",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=1200.0,
            velocity_x=0.0,
            velocity_y=0.0,
            velocity_z=0.0,
            amplitude=12.0,
            frequency=0.25,
        ),
        beacon=BeaconConfig(
            brightness=1.0,
            size=5.0,
            trajectory="static",
            trajectory_parameters={},
        ),
        disturbances=DisturbanceConfig(
            severity="low",
            vibration_enabled=True,
            vibration_magnitude=0.8,
            noise_enabled=True,
            noise_magnitude=0.08,
            blur_enabled=False,
            blur_strength=0.0,
            dropout_enabled=False,
            dropout_probability=0.0,
            dropout_duration=0.0,
        ),
        simulation=SimulationConfig(
            duration=45.0,
            fps=30.0,
            random_seed=101,
            record_telemetry=True,
            record_frames=False,
        ),
    )


def get_high_vibration_preset() -> ScenarioConfig:
    """4. High Vibration: Simulates high-frequency UAV/aircraft engine jitter."""
    return ScenarioConfig(
        scenario_name="High Vibration",
        description="Strong high-frequency micro-vibrations and optical blur simulating drone/aerospace platform turbulence.",
        camera=CameraConfig(
            width=640,
            height=480,
            horizontal_fov_deg=30.0,
            vertical_fov_deg=22.5,
            initial_pan_deg=0.0,
            initial_tilt_deg=0.0,
        ),
        camera_platform=PlatformConfig(
            motion_profile="sway",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=0.0,
            amplitude=3.0,
            frequency=2.5,
        ),
        beacon_platform=PlatformConfig(
            motion_profile="drift",
            initial_position_x=-5.0,
            initial_position_y=2.0,
            initial_position_z=1000.0,
            velocity_x=1.0,
            velocity_y=-0.5,
            velocity_z=0.0,
        ),
        beacon=BeaconConfig(
            brightness=0.9,
            size=4.5,
            trajectory="static",
            trajectory_parameters={},
        ),
        disturbances=DisturbanceConfig(
            severity="high",
            vibration_enabled=True,
            vibration_magnitude=4.5,
            noise_enabled=True,
            noise_magnitude=0.20,
            blur_enabled=True,
            blur_strength=2.8,
            dropout_enabled=False,
            dropout_probability=0.0,
            dropout_duration=0.0,
        ),
        simulation=SimulationConfig(
            duration=30.0,
            fps=30.0,
            random_seed=2024,
            record_telemetry=True,
            record_frames=False,
        ),
    )


def get_beacon_dropout_preset() -> ScenarioConfig:
    """5. Beacon Dropout: Atmospheric scintillation & cloud occlusion causing signal loss."""
    return ScenarioConfig(
        scenario_name="Beacon Dropout",
        description="Atmospheric deep fades and line-of-sight dropouts. Evaluates Kalman coasting and FSM re-acquisition logic.",
        camera=CameraConfig(
            width=640,
            height=480,
            horizontal_fov_deg=30.0,
            vertical_fov_deg=22.5,
            initial_pan_deg=0.0,
            initial_tilt_deg=0.0,
        ),
        camera_platform=PlatformConfig(
            motion_profile="drift",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=0.0,
            velocity_x=0.5,
            velocity_y=0.2,
        ),
        beacon_platform=PlatformConfig(
            motion_profile="sway",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=1500.0,
            amplitude=8.0,
            frequency=0.15,
        ),
        beacon=BeaconConfig(
            brightness=0.8,
            size=4.0,
            trajectory="linear",
            trajectory_parameters={"speed_mps": 1.5},
        ),
        disturbances=DisturbanceConfig(
            severity="medium",
            vibration_enabled=True,
            vibration_magnitude=1.5,
            noise_enabled=True,
            noise_magnitude=0.12,
            blur_enabled=True,
            blur_strength=1.5,
            dropout_enabled=True,
            dropout_probability=0.35,
            dropout_duration=0.6,
        ),
        simulation=SimulationConfig(
            duration=40.0,
            fps=30.0,
            random_seed=777,
            record_telemetry=True,
            record_frames=False,
        ),
    )


def get_full_stress_test_preset() -> ScenarioConfig:
    """6. Full Stress Test: Maximum disturbance combination with orbital platform kinematics."""
    return ScenarioConfig(
        scenario_name="Full Stress Test",
        description="Extreme mission environment: Orbital kinematics, severe vibration, high sensor noise, heavy blur, and frequent dropouts.",
        camera=CameraConfig(
            width=800,
            height=600,
            horizontal_fov_deg=35.0,
            vertical_fov_deg=26.25,
            initial_pan_deg=5.0,
            initial_tilt_deg=-3.0,
        ),
        camera_platform=PlatformConfig(
            motion_profile="orbit",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=0.0,
            amplitude=20.0,
            frequency=0.1,
        ),
        beacon_platform=PlatformConfig(
            motion_profile="sway",
            initial_position_x=10.0,
            initial_position_y=-10.0,
            initial_position_z=2000.0,
            amplitude=25.0,
            frequency=0.2,
        ),
        beacon=BeaconConfig(
            brightness=0.75,
            size=3.5,
            trajectory="circular",
            trajectory_parameters={"radius_m": 8.0, "angular_rate_rad_s": 0.3},
        ),
        disturbances=DisturbanceConfig(
            severity="high",
            vibration_enabled=True,
            vibration_magnitude=5.0,
            noise_enabled=True,
            noise_magnitude=0.25,
            blur_enabled=True,
            blur_strength=3.5,
            dropout_enabled=True,
            dropout_probability=0.45,
            dropout_duration=0.8,
        ),
        simulation=SimulationConfig(
            duration=60.0,
            fps=30.0,
            random_seed=9999,
            record_telemetry=True,
            record_frames=True,
        ),
    )


def get_custom_preset() -> ScenarioConfig:
    """7. Custom: Default base configuration for user customization."""
    return ScenarioConfig(
        scenario_name="Custom",
        description="Fully customizable scenario template. Adjust any optical, kinematic, disturbance, or simulation parameter.",
        camera=CameraConfig(
            width=640,
            height=480,
            horizontal_fov_deg=30.0,
            vertical_fov_deg=22.5,
            initial_pan_deg=0.0,
            initial_tilt_deg=0.0,
        ),
        camera_platform=PlatformConfig(
            motion_profile="static",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=0.0,
        ),
        beacon_platform=PlatformConfig(
            motion_profile="static",
            initial_position_x=0.0,
            initial_position_y=0.0,
            initial_position_z=1000.0,
        ),
        beacon=BeaconConfig(
            brightness=1.0,
            size=5.0,
            trajectory="static",
            trajectory_parameters={},
        ),
        disturbances=DisturbanceConfig(
            severity="off",
            vibration_enabled=False,
            vibration_magnitude=0.0,
            noise_enabled=False,
            noise_magnitude=0.0,
            blur_enabled=False,
            blur_strength=0.0,
            dropout_enabled=False,
            dropout_probability=0.0,
            dropout_duration=0.0,
        ),
        simulation=SimulationConfig(
            duration=30.0,
            fps=30.0,
            random_seed=42,
            record_telemetry=True,
            record_frames=False,
        ),
    )


PRESET_FACTORIES = {
    "easy_acquisition": get_easy_acquisition_preset,
    "easy acquisition": get_easy_acquisition_preset,
    "moving_beacon": get_moving_beacon_preset,
    "moving beacon": get_moving_beacon_preset,
    "platform_drift": get_platform_drift_preset,
    "platform drift": get_platform_drift_preset,
    "high_vibration": get_high_vibration_preset,
    "high vibration": get_high_vibration_preset,
    "beacon_dropout": get_beacon_dropout_preset,
    "beacon dropout": get_beacon_dropout_preset,
    "full_stress_test": get_full_stress_test_preset,
    "full stress test": get_full_stress_test_preset,
    "custom": get_custom_preset,
}


def get_preset(preset_name: str) -> ScenarioConfig:
    """Retrieve a ScenarioConfig instance by preset key or name."""
    normalized_key = preset_name.strip().lower().replace("-", "_")
    if normalized_key in PRESET_FACTORIES:
        return PRESET_FACTORIES[normalized_key]()
    raise KeyError(
        f"Unknown preset '{preset_name}'. Available presets: "
        f"['easy_acquisition', 'moving_beacon', 'platform_drift', 'high_vibration', 'beacon_dropout', 'full_stress_test', 'custom']"
    )


def list_available_presets() -> List[Dict[str, str]]:
    """Return catalog of presets with metadata for UI and API clients."""
    return [
        {
            "id": "easy_acquisition",
            "name": "Easy Acquisition",
            "difficulty": "Level 1 - Baseline",
            "description": "Stationary terminals with zero disturbance. Baseline optical calibration.",
        },
        {
            "id": "moving_beacon",
            "name": "Moving Beacon",
            "difficulty": "Level 2 - Mild",
            "description": "Linear beacon motion across camera FOV with minor sensor noise.",
        },
        {
            "id": "platform_drift",
            "name": "Platform Drift",
            "difficulty": "Level 3 - Moderate",
            "description": "Receiver drift and beacon sinusoidal sway dynamics.",
        },
        {
            "id": "high_vibration",
            "name": "High Vibration",
            "difficulty": "Level 4 - Challenging",
            "description": "High-frequency micro-vibrations and atmospheric blur.",
        },
        {
            "id": "beacon_dropout",
            "name": "Beacon Dropout",
            "difficulty": "Level 5 - Hard",
            "description": "Atmospheric scintillation deep fades and line-of-sight dropouts.",
        },
        {
            "id": "full_stress_test",
            "name": "Full Stress Test",
            "difficulty": "Level 6 - Extreme",
            "description": "Orbital kinematics, severe jitter, noise, blur, and deep fading.",
        },
        {
            "id": "custom",
            "name": "Custom",
            "difficulty": "User Defined",
            "description": "User-tunable scenario with full parameter customization.",
        },
    ]
