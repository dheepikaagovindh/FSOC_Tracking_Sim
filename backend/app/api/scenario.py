"""
Scenario Configuration API Endpoints.
Team PHARO — SIH26169
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..scenario.models import ScenarioConfig
from ..scenario.service import scenario_service
from ..scenario.validator import ScenarioValidator
from ..scenario.factory import ScenarioFactory

router = APIRouter(tags=["Scenario Configuration"])


class ScenarioApplyResponse(BaseModel):
    status: str = Field(default="SCENARIO_READY", description="Simulation scenario state")
    message: str = Field(description="Operational status message")
    scenario: ScenarioConfig = Field(description="Active scenario configuration")
    validation: Dict[str, Any] = Field(description="Validation outcomes and warnings")


class ScenarioValidationRequest(BaseModel):
    scenario: ScenarioConfig


class SimulationStartResponse(BaseModel):
    status: str = Field(default="SCENARIO_READY")
    message: str = Field(default="Scenario verified and ready for tracking simulation.")
    scenario_name: str
    simulation_context: Dict[str, Any]


@router.get("/scenario", response_model=ScenarioConfig, summary="Get Active Scenario")
def get_active_scenario():
    """Retrieve the currently active FSOC scenario configuration."""
    return scenario_service.get_active_scenario()


@router.post("/scenario", response_model=ScenarioApplyResponse, summary="Apply Scenario Configuration")
def apply_scenario(config: ScenarioConfig):
    """
    Apply a complete scenario configuration.
    Performs full validation and transitions simulator state to SCENARIO_READY.
    """
    applied_config, val_result = scenario_service.update_scenario(config)
    if not val_result.is_valid or applied_config is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Scenario configuration validation failed.",
                "errors": val_result.errors,
                "warnings": val_result.warnings,
            },
        )
    return ScenarioApplyResponse(
        status="SCENARIO_READY",
        message="Scenario validated and configured successfully.",
        scenario=applied_config,
        validation=val_result.to_dict(),
    )


@router.get("/scenario/presets", response_model=List[Dict[str, str]], summary="List Available Presets")
def list_presets():
    """Retrieve catalog of all predefined scenario presets."""
    return scenario_service.list_presets()


@router.post("/scenario/preset/{preset_name}", response_model=ScenarioApplyResponse, summary="Load Scenario Preset")
def load_preset(preset_name: str):
    """
    Load and activate a predefined scenario preset.
    Supported: 'easy_acquisition', 'moving_beacon', 'platform_drift', 'high_vibration',
    'beacon_dropout', 'full_stress_test', 'custom'.
    """
    try:
        preset_config, val_result = scenario_service.load_preset(preset_name)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return ScenarioApplyResponse(
        status="SCENARIO_READY",
        message=f"Preset '{preset_config.scenario_name}' loaded successfully.",
        scenario=preset_config,
        validation=val_result.to_dict(),
    )


@router.post("/scenario/reset", response_model=ScenarioApplyResponse, summary="Reset to Default Configuration")
def reset_scenario():
    """Reset configuration back to default Easy Acquisition baseline."""
    default_config = scenario_service.reset_scenario()
    val_result = ScenarioValidator.validate(default_config)
    return ScenarioApplyResponse(
        status="SCENARIO_READY",
        message="Scenario reset to default Easy Acquisition baseline.",
        scenario=default_config,
        validation=val_result.to_dict(),
    )


@router.post("/scenario/validate", summary="Validate Scenario (Dry-Run)")
def validate_scenario(config: ScenarioConfig):
    """Validate a scenario configuration payload without modifying active state."""
    val_result = ScenarioValidator.validate(config)
    return val_result.to_dict()


@router.post("/scenario/start", response_model=SimulationStartResponse, summary="Verify & Initialize Simulation")
def start_simulation():
    """
    Verify active scenario and build simulation initialization context.
    Confirms 'SCENARIO READY' for future tracking pipeline integration.
    """
    active_scenario = scenario_service.get_active_scenario()
    val_result = ScenarioValidator.validate(active_scenario)
    if not val_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cannot start simulation with invalid scenario.",
                "errors": val_result.errors,
            },
        )

    sim_context = ScenarioFactory.build_simulation_context(active_scenario)
    return SimulationStartResponse(
        status="SCENARIO_READY",
        message="Active scenario is validated and simulation components are initialized. Ready for tracking execution.",
        scenario_name=active_scenario.scenario_name,
        simulation_context=sim_context,
    )


@router.get("/scenario/status", summary="Get Simulator Status")
def get_simulator_status():
    """Get full system status, scenario metadata, and lifecycle info."""
    return scenario_service.get_simulator_status()
