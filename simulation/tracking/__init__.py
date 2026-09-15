"""
Beacon Tracking & Motion Prediction Simulation Package (Standalone Layer).
Team PHARO — SIH26169
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.tracking.models import (
    TrackingConfig,
    TrackingResult,
    TrackingStatus,
    TrackingStatusInfo,
    TrackingTelemetry,
)
from app.tracking.base import BaseTracker
from app.tracking.kalman_tracker import KalmanTracker
from app.tracking.service import TrackingService, tracking_service

__all__ = [
    "TrackingConfig",
    "TrackingResult",
    "TrackingStatus",
    "TrackingStatusInfo",
    "TrackingTelemetry",
    "BaseTracker",
    "KalmanTracker",
    "TrackingService",
    "tracking_service",
]
