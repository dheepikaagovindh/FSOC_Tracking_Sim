"""
Mock Detector for Unit and Integration Testing.
Team PHARO — SIH26169

Used exclusively for test isolation. NOT intended for production tracking.
"""

from __future__ import annotations
import time
from typing import Optional
import numpy as np

from .base import BaseDetector
from .models import (
    DetectionConfig,
    DetectionResult,
    BoundingBox,
)


class MockBeaconDetector(BaseDetector):
    """
    Configurable mock detector for automated test suites.
    """

    def __init__(
        self,
        config: Optional[DetectionConfig] = None,
        mock_detected: bool = True,
        mock_center_x: float = 320.0,
        mock_center_y: float = 240.0,
        mock_confidence: float = 0.95,
        mock_bbox: Optional[BoundingBox] = None,
    ):
        super().__init__(config=config or DetectionConfig(method="mock"))
        self.mock_detected = mock_detected
        self.mock_center_x = mock_center_x
        self.mock_center_y = mock_center_y
        self.mock_confidence = mock_confidence
        self.mock_bbox = mock_bbox or BoundingBox(x=315, y=235, width=11, height=11)

    def detect(
        self,
        image: np.ndarray,
        timestamp: Optional[float] = None,
        config: Optional[DetectionConfig] = None,
    ) -> DetectionResult:
        t_start = time.perf_counter()
        ts = timestamp if timestamp is not None else 0.0
        t_exec = (time.perf_counter() - t_start) * 1000.0

        if not self.mock_detected:
            return DetectionResult(
                detected=False,
                center_x=None,
                center_y=None,
                bbox=None,
                confidence=0.0,
                candidate_count=0,
                method="mock",
                timestamp=ts,
                processing_time_ms=round(t_exec, 3),
                message="Mock detector forced negative detection",
            )

        return DetectionResult(
            detected=True,
            center_x=self.mock_center_x,
            center_y=self.mock_center_y,
            u=self.mock_center_x,
            v=self.mock_center_y,
            confidence=self.mock_confidence,
            bbox=self.mock_bbox,
            candidate_count=1,
            selected_candidate=0,
            method="mock",
            timestamp=ts,
            processing_time_ms=round(t_exec, 3),
            message="Mock detector simulated positive detection",
        )
