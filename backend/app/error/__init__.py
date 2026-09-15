"""
Boresight Alignment & Error Calculation Module (Module 7).
Team PHARO — SIH26169

Public exports for app.error.
"""

from .models import (
    AlignmentConfig,
    AlignmentError,
    ErrorStatus,
    ErrorSource,
    ErrorStatusInfo,
    ErrorTelemetry,
)
from .calculator import ErrorCalculator
from .service import AlignmentService, alignment_service

__all__ = [
    "AlignmentConfig",
    "AlignmentError",
    "ErrorStatus",
    "ErrorSource",
    "ErrorStatusInfo",
    "ErrorTelemetry",
    "ErrorCalculator",
    "AlignmentService",
    "alignment_service",
]
