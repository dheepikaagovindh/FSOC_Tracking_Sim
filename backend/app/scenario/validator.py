"""
Scenario Configuration Validator.
Team PHARO — SIH26169

Provides dedicated, rigorous validation of simulation scenario configurations
before initialization of downstream simulation components.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import ValidationError
from .models import ScenarioConfig


class ValidationResult:
    """Encapsulates validation outcome, errors, and warnings."""

    def __init__(self, is_valid: bool = True, errors: Optional[List[str]] = None, warnings: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def add_error(self, field: str, message: str) -> None:
        self.is_valid = False
        self.errors.append(f"[{field}] {message}")

    def add_warning(self, field: str, message: str) -> None:
        self.warnings.append(f"[{field}] {message}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def __repr__(self) -> str:
        return f"ValidationResult(is_valid={self.is_valid}, errors={len(self.errors)}, warnings={len(self.warnings)})"


class ScenarioValidator:
    """Dedicated validation engine for FSOC Simulation Scenarios."""

    VALID_MOTION_PROFILES = {"static", "drift", "sway", "orbit"}
    VALID_TRAJECTORIES = {"static", "linear", "circular", "custom"}
    VALID_SEVERITIES = {"off", "low", "medium", "high"}

    @classmethod
    def validate_dict(cls, data: Dict[str, Any]) -> Tuple[Optional[ScenarioConfig], ValidationResult]:
        """Validate raw dictionary / JSON payload against ScenarioConfig specifications."""
        result = ValidationResult()

        if not isinstance(data, dict):
            result.add_error("root", "Scenario configuration payload must be a JSON object.")
            return None, result

        try:
            config = ScenarioConfig.model_validate(data)
        except ValidationError as e:
            for err in e.errors():
                loc = " -> ".join(str(item) for item in err["loc"])
                msg = err["msg"]
                result.add_error(loc, msg)
            return None, result

        # Perform additional domain/physical consistency validations
        cls._validate_domain_rules(config, result)
        return (config if result.is_valid else None), result

    @classmethod
    def validate(cls, config: ScenarioConfig) -> ValidationResult:
        """Validate an already instantiated ScenarioConfig object."""
        result = ValidationResult()
        cls._validate_domain_rules(config, result)
        return result

    @classmethod
    def _validate_domain_rules(cls, config: ScenarioConfig, result: ValidationResult) -> None:
        # 1. Camera Validation
        cam = config.camera
        if cam.width <= 0 or cam.height <= 0:
            result.add_error("camera.resolution", f"Camera resolution must be positive. Received {cam.width}x{cam.height}")
        elif cam.width < 64 or cam.height < 64:
            result.add_error("camera.resolution", f"Camera resolution {cam.width}x{cam.height} is below minimum supported 64x64.")
        elif cam.width > 7680 or cam.height > 4320:
            result.add_error("camera.resolution", f"Camera resolution {cam.width}x{cam.height} exceeds 8K limit (7680x4320).")

        if not (0.0 < cam.horizontal_fov_deg < 180.0):
            result.add_error("camera.horizontal_fov_deg", f"Horizontal FOV must be between 0° and 180°. Received {cam.horizontal_fov_deg}°")

        if not (0.0 < cam.vertical_fov_deg < 180.0):
            result.add_error("camera.vertical_fov_deg", f"Vertical FOV must be between 0° and 180°. Received {cam.vertical_fov_deg}°")

        if not (-180.0 <= cam.initial_pan_deg <= 180.0):
            result.add_error("camera.initial_pan_deg", f"Initial pan angle must be within [-180°, 180°]. Received {cam.initial_pan_deg}°")

        if not (-90.0 <= cam.initial_tilt_deg <= 90.0):
            result.add_error("camera.initial_tilt_deg", f"Initial tilt angle must be within [-90°, 90°]. Received {cam.initial_tilt_deg}°")

        # Aspect ratio consistency warning
        if cam.width > 0 and cam.height > 0 and cam.horizontal_fov_deg > 0 and cam.vertical_fov_deg > 0:
            pixel_aspect = cam.width / cam.height
            fov_aspect = cam.horizontal_fov_deg / cam.vertical_fov_deg
            if abs(pixel_aspect - fov_aspect) > 0.4:
                result.add_warning("camera.aspect_ratio", f"FOV aspect ratio ({fov_aspect:.2f}) deviates from pixel aspect ratio ({pixel_aspect:.2f}).")

        # 2. Platform Kinematics Validation (Camera & Beacon)
        for platform_name, plat in [("camera_platform", config.camera_platform), ("beacon_platform", config.beacon_platform)]:
            if plat.motion_profile.lower() not in cls.VALID_MOTION_PROFILES:
                result.add_error(f"{platform_name}.motion_profile", f"Unsupported motion profile '{plat.motion_profile}'. Must be one of {sorted(list(cls.VALID_MOTION_PROFILES))}")

            if plat.amplitude < 0.0:
                result.add_error(f"{platform_name}.amplitude", f"Amplitude cannot be negative. Received {plat.amplitude}")

            if plat.frequency < 0.0:
                result.add_error(f"{platform_name}.frequency", f"Frequency cannot be negative. Received {plat.frequency}")

            if plat.motion_profile.lower() in {"sway", "orbit"} and plat.amplitude == 0.0:
                result.add_warning(f"{platform_name}.amplitude", f"Motion profile '{plat.motion_profile}' selected with amplitude=0.0 will behave as static.")

        # 3. Beacon Validation
        b = config.beacon
        if b.brightness <= 0.0:
            result.add_error("beacon.brightness", f"Beacon brightness must be strictly positive (> 0.0). Received {b.brightness}")

        if b.size <= 0.0:
            result.add_error("beacon.size", f"Beacon size must be strictly positive (> 0.0). Received {b.size}")

        if b.trajectory.lower() not in cls.VALID_TRAJECTORIES:
            result.add_error("beacon.trajectory", f"Unsupported beacon trajectory '{b.trajectory}'. Must be one of {sorted(list(cls.VALID_TRAJECTORIES))}")

        # 4. Disturbance Validation
        dist = config.disturbances
        if dist.severity.lower() not in cls.VALID_SEVERITIES:
            result.add_error("disturbances.severity", f"Unsupported disturbance severity '{dist.severity}'. Must be one of {sorted(list(cls.VALID_SEVERITIES))}")

        if dist.vibration_magnitude < 0.0:
            result.add_error("disturbances.vibration_magnitude", f"Vibration magnitude cannot be negative. Received {dist.vibration_magnitude}")

        if dist.noise_magnitude < 0.0:
            result.add_error("disturbances.noise_magnitude", f"Noise magnitude cannot be negative. Received {dist.noise_magnitude}")

        if dist.blur_strength < 0.0:
            result.add_error("disturbances.blur_strength", f"Blur strength cannot be negative. Received {dist.blur_strength}")

        if not (0.0 <= dist.dropout_probability <= 1.0):
            result.add_error("disturbances.dropout_probability", f"Dropout probability must be in range [0.0, 1.0]. Received {dist.dropout_probability}")

        if dist.dropout_duration < 0.0:
            result.add_error("disturbances.dropout_duration", f"Dropout duration cannot be negative. Received {dist.dropout_duration}")

        # 5. Simulation Validation
        sim = config.simulation
        if sim.duration <= 0.0:
            result.add_error("simulation.duration", f"Simulation duration must be strictly positive (> 0.0s). Received {sim.duration}s")

        if sim.fps <= 0.0:
            result.add_error("simulation.fps", f"Simulation FPS must be strictly positive (> 0.0). Received {sim.fps}")
        elif sim.fps > 240.0:
            result.add_error("simulation.fps", f"Simulation FPS exceeds maximum supported rate (240 FPS). Received {sim.fps}")

        if sim.random_seed < 0:
            result.add_error("simulation.random_seed", f"Random seed must be non-negative (>= 0). Received {sim.random_seed}")
