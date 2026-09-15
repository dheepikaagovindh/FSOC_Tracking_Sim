"""
Domain Models and Data Structures for Disturbance & Noise Simulation.
Team PHARO — SIH26169
"""

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

from ..scenario.models import DisturbanceConfig


class NoiseMetadata(BaseModel):
    """Metadata for applied sensor noise."""
    enabled: bool = Field(description="Whether sensor noise is enabled")
    magnitude: float = Field(description="Configured noise magnitude")
    sigma: float = Field(description="Effective Gaussian standard deviation in 8-bit scale (0-255)")
    applied: bool = Field(description="Whether noise was actively applied to frame")


class BlurMetadata(BaseModel):
    """Metadata for applied optical blur."""
    enabled: bool = Field(description="Whether optical blur is enabled")
    strength: float = Field(description="Configured blur strength / sigma")
    kernel_size: int = Field(description="Effective Gaussian blur kernel footprint diameter")
    applied: bool = Field(description="Whether blur was actively applied to frame")


class VibrationMetadata(BaseModel):
    """Metadata for applied image-plane vibration / jitter."""
    enabled: bool = Field(description="Whether image-plane vibration is enabled")
    magnitude: float = Field(description="Configured vibration magnitude (pixels)")
    offset_x: float = Field(description="Instantaneous horizontal image shift dx in pixels")
    offset_y: float = Field(description="Instantaneous vertical image shift dy in pixels")
    applied: bool = Field(description="Whether non-zero vibration shift was applied")


class DropoutMetadata(BaseModel):
    """Metadata for applied atmospheric deep fades and beacon dropouts."""
    enabled: bool = Field(description="Whether dropout simulation is enabled")
    probability: float = Field(description="Configured frame dropout probability")
    duration: float = Field(description="Configured dropout duration in seconds")
    active: bool = Field(description="Whether a dropout event is actively suppressing the beacon")
    remaining_duration: float = Field(default=0.0, description="Remaining duration of active dropout burst in seconds")
    applied: bool = Field(description="Whether beacon spot was actively removed or occluded in this frame")


class DisturbanceMetadata(BaseModel):
    """Consolidated metadata of all environmental disturbances applied to a frame."""
    severity: str = Field(description="Active disturbance severity level ('off', 'low', 'medium', 'high')")
    noise: NoiseMetadata = Field(description="Sensor noise diagnostics")
    blur: BlurMetadata = Field(description="Optical blur diagnostics")
    vibration: VibrationMetadata = Field(description="Image vibration diagnostics")
    dropout: DropoutMetadata = Field(description="Beacon dropout diagnostics")
    random_seed: int = Field(description="Master random seed used for reproducibility")
    frame_index: int = Field(description="Discrete simulation frame index: round(timestamp * fps)")
    applied_effects_count: int = Field(description="Number of distinct disturbance effects applied")


class DisturbanceFrame(BaseModel):
    """Complete disturbed camera observation frame packet."""
    timestamp: float = Field(description="Simulation timestamp in seconds", ge=0.0)
    frame_index: int = Field(description="Simulation frame index", ge=0)
    width: int = Field(description="Sensor image width in pixels", ge=1)
    height: int = Field(description="Sensor image height in pixels", ge=1)
    metadata: DisturbanceMetadata = Field(description="Detailed disturbance diagnostics")
    is_disturbed: bool = Field(description="True if any disturbance altered the clean frame")


class DisturbanceStatus(BaseModel):
    """Lifecycle status, active configuration, and telemetry overview of Disturbance module."""
    initialized: bool = Field(description="Whether disturbance processor is initialized")
    scenario_name: str = Field(description="Active scenario title")
    severity: str = Field(description="Active severity level ('off', 'low', 'medium', 'high')")
    config: DisturbanceConfig = Field(description="Active DisturbanceConfig parameters")
    dropout_active: bool = Field(description="Whether a dropout event is currently active")
    current_timestamp: float = Field(description="Current simulation timestamp in seconds")


class DisturbanceTelemetry(BaseModel):
    """Real-time disturbance telemetry for HUD and diagnostic displays."""
    timestamp: float = Field(description="Current timestamp in seconds")
    frame_index: int = Field(description="Current frame index")
    severity: str = Field(description="Disturbance severity level")
    noise_sigma: float = Field(description="Sensor noise standard deviation")
    blur_strength: float = Field(description="Blur strength")
    vibration_offset_x: float = Field(description="Vibration horizontal shift (px)")
    vibration_offset_y: float = Field(description="Vibration vertical shift (px)")
    dropout_active: bool = Field(description="Dropout active state")
    dropout_remaining_duration: float = Field(description="Remaining dropout burst duration (s)")
    beacon_visible_in_clean: bool = Field(description="Whether beacon is visible in clean camera frame")
    beacon_occluded_by_dropout: bool = Field(description="Whether beacon was suppressed by dropout")
