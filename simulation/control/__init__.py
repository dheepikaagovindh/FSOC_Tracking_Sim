"""
Boresight Error Calculation & Alignment Simulation Package (Standalone Layer).
Team PHARO — SIH26169
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.error.models import (
    AlignmentConfig,
    AlignmentError,
    ErrorStatus,
    ErrorSource,
    ErrorStatusInfo,
    ErrorTelemetry,
)
from app.error.calculator import ErrorCalculator
from app.error.service import AlignmentService, alignment_service

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
