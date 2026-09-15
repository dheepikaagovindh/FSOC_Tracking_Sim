"""
Abstract Base Class for Beacon Trackers.
Team PHARO — SIH26169
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
import numpy as np


class BaseTracker(ABC):
    """
    Abstract interface for 2D focal-plane state estimators and trackers.
    """

    @abstractmethod
    def initialize(
        self,
        initial_position: np.ndarray,
        initial_velocity: Optional[np.ndarray] = None,
        initial_covariance: Optional[np.ndarray] = None,
        timestamp: float = 0.0,
    ) -> None:
        """
        Initialize the tracker state and covariance from the first measurement.
        """
        pass

    @abstractmethod
    def predict(self, dt: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Propagate state and covariance forward by elapsed time dt.
        Returns (predicted_state, predicted_covariance).
        """
        pass

    @abstractmethod
    def update(
        self,
        measurement: np.ndarray,
        measurement_cov: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Update state estimate using measurement vector z = [px, py]^T.
        Returns (updated_state, updated_covariance).
        """
        pass

    @abstractmethod
    def step(
        self,
        measurement: Optional[np.ndarray],
        dt: float,
        measurement_cov: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Execute a complete predict + (optional) update cycle for a frame.
        """
        pass

    @abstractmethod
    def predict_lead(self, lead_time: float) -> np.ndarray:
        """
        Extrapolate state into the future by lead_time seconds.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Clear all internal state, covariance, and history.
        """
        pass

    @abstractmethod
    def get_state(self) -> Optional[np.ndarray]:
        """
        Retrieve current state vector [px, py, vx, vy]^T or None if uninitialized.
        """
        pass

    @abstractmethod
    def get_covariance(self) -> Optional[np.ndarray]:
        """
        Retrieve current 4x4 covariance matrix P or None if uninitialized.
        """
        pass

    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Return True if tracker has been initialized.
        """
        pass
