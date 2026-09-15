"""
Abstract Base Detector Interface.
Team PHARO — SIH26169

Defines the pluggable detector contract allowing OpenCV, Mock, and future YOLO models
to be swapped without modifying downstream tracking or API layers.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np

from .models import DetectionResult, DetectionConfig


class BaseDetector(ABC):
    """
    Abstract interface for all optical beacon detectors.
    """

    def __init__(self, config: Optional[DetectionConfig] = None):
        self._config = config or DetectionConfig()

    @property
    def config(self) -> DetectionConfig:
        return self._config

    @config.setter
    def config(self, new_config: DetectionConfig):
        self._config = new_config

    @abstractmethod
    def detect(
        self,
        image: np.ndarray,
        timestamp: Optional[float] = None,
        config: Optional[DetectionConfig] = None,
    ) -> DetectionResult:
        """
        Execute beacon detection on an input image array.

        Parameters:
          image: 2D or 3D NumPy array containing the sensor observation.
          timestamp: Optional simulation timestamp in seconds.
          config: Optional runtime configuration override.

        Returns:
          DetectionResult containing detection state, coordinates, confidence, bounding box, and latency.
        """
        pass
