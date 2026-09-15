"""
2D Constant-Velocity Kalman Filter Beacon Tracker.
Team PHARO — SIH26169

Implements discrete-time linear Kalman filtering for 2D focal-plane beacon spot
position and velocity estimation with Joseph-form covariance updates and lead prediction.
"""

from __future__ import annotations
import logging
from typing import Optional, Tuple
import numpy as np

from .base import BaseTracker
from .models import TrackingConfig

logger = logging.getLogger("fsoc.tracking.kalman")


class KalmanTracker(BaseTracker):
    """
    2D Constant-Velocity Kalman Filter State Estimator.

    State Vector:
        x = [px, py, vx, vy]^T
        px: Focal-plane horizontal position (pixels)
        py: Focal-plane vertical position (pixels)
        vx: Horizontal focal-plane velocity (pixels/s)
        vy: Vertical focal-plane velocity (pixels/s)

    Measurement Vector:
        z = [px, py]^T
    """

    def __init__(self, config: Optional[TrackingConfig] = None):
        self._config = config if config is not None else TrackingConfig()
        self._state: Optional[np.ndarray] = None  # 4x1 vector
        self._cov: Optional[np.ndarray] = None    # 4x4 matrix
        self._initialized: bool = False
        self._last_timestamp: float = 0.0

        # Fixed measurement matrix H (2x4)
        self._H = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0]
        ], dtype=np.float64)

        # 4x4 Identity matrix
        self._I4 = np.eye(4, dtype=np.float64)

    @property
    def config(self) -> TrackingConfig:
        return self._config

    @config.setter
    def config(self, new_config: TrackingConfig) -> None:
        self._config = new_config

    def is_initialized(self) -> bool:
        return self._initialized and self._state is not None and self._cov is not None

    def get_state(self) -> Optional[np.ndarray]:
        if self._state is None:
            return None
        return self._state.copy()

    def get_covariance(self) -> Optional[np.ndarray]:
        if self._cov is None:
            return None
        return self._cov.copy()

    def get_position(self) -> Optional[Tuple[float, float]]:
        if self._state is None:
            return None
        return (float(self._state[0, 0]), float(self._state[1, 0]))

    def get_velocity(self) -> Optional[Tuple[float, float]]:
        if self._state is None:
            return None
        return (float(self._state[2, 0]), float(self._state[3, 0]))

    def get_position_uncertainty(self) -> Optional[Tuple[float, float]]:
        """
        Return 1-sigma standard deviation for (x, y) position: (sqrt(P[0,0]), sqrt(P[1,1])).
        """
        if self._cov is None:
            return None
        var_x = max(0.0, float(self._cov[0, 0]))
        var_y = max(0.0, float(self._cov[1, 1]))
        return (float(np.sqrt(var_x)), float(np.sqrt(var_y)))

    def get_velocity_uncertainty(self) -> Optional[Tuple[float, float]]:
        """
        Return 1-sigma standard deviation for (vx, vy) velocity: (sqrt(P[2,2]), sqrt(P[3,3])).
        """
        if self._cov is None:
            return None
        var_vx = max(0.0, float(self._cov[2, 2]))
        var_vy = max(0.0, float(self._cov[3, 3]))
        return (float(np.sqrt(var_vx)), float(np.sqrt(var_vy)))

    def initialize(
        self,
        initial_position: np.ndarray,
        initial_velocity: Optional[np.ndarray] = None,
        initial_covariance: Optional[np.ndarray] = None,
        timestamp: float = 0.0,
    ) -> None:
        """
        Initialize the Kalman filter state from the first valid beacon measurement.

        Args:
            initial_position: 2-element array [px, py]
            initial_velocity: Optional 2-element array [vx, vy], defaults to [0, 0]
            initial_covariance: Optional 4x4 matrix P_0
            timestamp: Initial simulation time in seconds
        """
        pos = np.asarray(initial_position, dtype=np.float64).flatten()
        if pos.shape[0] != 2 or not np.all(np.isfinite(pos)):
            raise ValueError(f"Invalid initial position: {pos}")

        vel = np.zeros(2, dtype=np.float64)
        if initial_velocity is not None:
            v_arr = np.asarray(initial_velocity, dtype=np.float64).flatten()
            if v_arr.shape[0] == 2 and np.all(np.isfinite(v_arr)):
                vel = v_arr

        # State vector x = [px, py, vx, vy]^T
        self._state = np.array([
            [pos[0]],
            [pos[1]],
            [vel[0]],
            [vel[1]]
        ], dtype=np.float64)

        # Covariance matrix P
        if initial_covariance is not None and initial_covariance.shape == (4, 4) and np.all(np.isfinite(initial_covariance)):
            self._cov = initial_covariance.astype(np.float64)
        else:
            p_var = float(self._config.initial_position_uncertainty)
            v_var = float(self._config.initial_velocity_uncertainty)
            self._cov = np.diag([p_var, p_var, v_var, v_var]).astype(np.float64)

        self._last_timestamp = float(timestamp)
        self._initialized = True
        logger.debug("KalmanTracker initialized at pos=(%.2f, %.2f) t=%.3f", pos[0], pos[1], timestamp)

    def _build_F(self, dt: float) -> np.ndarray:
        """
        Construct 4x4 state transition matrix F for time step dt.
        """
        return np.array([
            [1.0, 0.0,  dt, 0.0],
            [0.0, 1.0, 0.0,  dt],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float64)

    def _build_Q(self, dt: float) -> np.ndarray:
        """
        Construct 4x4 discrete white-noise acceleration process covariance matrix Q(dt).
        Continuous spectral density q (acceleration noise).
        """
        q = float(self._config.process_noise)
        dt2 = dt * dt
        dt3 = dt2 * dt
        dt4 = dt3 * dt

        # Continuous White Noise Acceleration model
        # Position variance: q * dt^3 / 3
        # Position-Velocity covariance: q * dt^2 / 2
        # Velocity variance: q * dt
        q11 = (dt3 / 3.0) * q
        q12 = (dt2 / 2.0) * q
        q22 = dt * q

        return np.array([
            [q11, 0.0, q12, 0.0],
            [0.0, q11, 0.0, q12],
            [q12, 0.0, q22, 0.0],
            [0.0, q12, 0.0, q22]
        ], dtype=np.float64)

    def _build_R(self, measurement_cov: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Construct 2x2 measurement noise covariance matrix R.
        """
        if measurement_cov is not None:
            r_arr = np.asarray(measurement_cov, dtype=np.float64)
            if r_arr.shape == (2, 2) and np.all(np.isfinite(r_arr)):
                return r_arr
            elif r_arr.size == 1 and np.isfinite(r_arr.item()):
                val = float(r_arr.item())
                return np.diag([val, val]).astype(np.float64)

        r_val = max(1e-4, float(self._config.measurement_noise))
        return np.diag([r_val, r_val]).astype(np.float64)

    def predict(self, dt: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Kalman Prediction Step:
            x^- = F * x
            P^- = F * P * F^T + Q
        """
        if not self.is_initialized():
            raise RuntimeError("KalmanTracker cannot predict before initialization")

        # Bound dt safely
        safe_dt = max(self._config.min_dt, min(dt, self._config.max_dt))

        F = self._build_F(safe_dt)
        Q = self._build_Q(safe_dt)

        # State prediction
        self._state = F @ self._state

        # Covariance prediction
        self._cov = F @ self._cov @ F.T + Q

        # Enforce symmetry
        self._cov = 0.5 * (self._cov + self._cov.T)

        self._sanitize_state_and_covariance()
        return self._state.copy(), self._cov.copy()

    def update(
        self,
        measurement: np.ndarray,
        measurement_cov: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Kalman Measurement Update Step:
            y = z - H * x^-
            S = H * P^- * H^T + R
            K = P^- * H^T * S^-1
            x = x^- + K * y
            P = (I - K*H) * P^- * (I - K*H)^T + K * R * K^T  (Joseph Form)
        """
        if not self.is_initialized():
            raise RuntimeError("KalmanTracker cannot update before initialization")

        z = np.asarray(measurement, dtype=np.float64).flatten()
        if z.shape[0] != 2 or not np.all(np.isfinite(z)):
            logger.warning("Rejecting invalid measurement for update: %s", z)
            return self._state.copy(), self._cov.copy()

        z = z.reshape(2, 1)
        R = self._build_R(measurement_cov)

        # Innovation (measurement residual)
        y = z - (self._H @ self._state)

        # Innovation covariance S (2x2)
        S = self._H @ self._cov @ self._H.T + R
        S = 0.5 * (S + S.T)

        # Compute Kalman Gain K (4x2) using numerically stable solve
        try:
            # S is 2x2; solve S * K^T = H * P
            # K = P * H^T * S^-1 => K^T = S^-1 * H * P
            PHt = self._cov @ self._H.T  # 4x2
            K = np.linalg.solve(S.T, PHt.T).T  # 4x2
        except np.linalg.LinAlgError:
            logger.warning("Singular innovation covariance S, adding diagonal regularization")
            S_reg = S + np.eye(2) * 1e-3
            PHt = self._cov @ self._H.T
            K = np.linalg.solve(S_reg.T, PHt.T).T

        # State update
        self._state = self._state + (K @ y)

        # Covariance update via Joseph Form for guaranteed positive semi-definiteness
        IKH = self._I4 - (K @ self._H)
        self._cov = (IKH @ self._cov @ IKH.T) + (K @ R @ K.T)

        # Enforce symmetry
        self._cov = 0.5 * (self._cov + self._cov.T)

        self._sanitize_state_and_covariance()
        return self._state.copy(), self._cov.copy()

    def step(
        self,
        measurement: Optional[np.ndarray],
        dt: float,
        measurement_cov: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Execute full predict + optional update step.
        """
        if not self.is_initialized():
            if measurement is not None:
                self.initialize(measurement)
                return self._state.copy(), self._cov.copy()
            raise RuntimeError("Cannot step uninitialized tracker without measurement")

        self.predict(dt)
        if measurement is not None:
            self.update(measurement, measurement_cov)

        return self._state.copy(), self._cov.copy()

    def predict_lead(self, lead_time: float) -> np.ndarray:
        """
        Extrapolate future state by lead_time (seconds).
        Returns predicted 4x1 state vector.
        """
        if not self.is_initialized():
            return np.zeros((4, 1), dtype=np.float64)

        tau = max(0.0, float(lead_time))
        F_lead = self._build_F(tau)
        pred_state = F_lead @ self._state
        return pred_state

    def reset(self) -> None:
        """
        Clear all internal state, covariance, and history.
        """
        self._state = None
        self._cov = None
        self._initialized = False
        self._last_timestamp = 0.0
        logger.debug("KalmanTracker state reset")

    def _sanitize_state_and_covariance(self) -> None:
        """
        Safety check to ensure state and covariance are finite and non-degenerate.
        """
        if self._state is not None and not np.all(np.isfinite(self._state)):
            logger.error("Non-finite values encountered in Kalman state! Resetting state to zeros.")
            self._state = np.zeros((4, 1), dtype=np.float64)

        if self._cov is not None:
            if not np.all(np.isfinite(self._cov)):
                logger.error("Non-finite values encountered in covariance! Resetting to default uncertainty.")
                p_var = float(self._config.initial_position_uncertainty)
                v_var = float(self._config.initial_velocity_uncertainty)
                self._cov = np.diag([p_var, p_var, v_var, v_var]).astype(np.float64)
            else:
                # Ensure diagonals remain strictly positive
                for i in range(4):
                    if self._cov[i, i] < 1e-6:
                        self._cov[i, i] = 1e-6
