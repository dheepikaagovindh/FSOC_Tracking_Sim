"""
Unit Tests for 2D Constant-Velocity Kalman Filter Beacon Tracker.
Team PHARO — SIH26169
"""

import numpy as np
import pytest

from app.tracking.models import TrackingConfig
from app.tracking.kalman_tracker import KalmanTracker


def test_tracker_initial_state():
    """Verify tracker starts uninitialized and rejects operations before initialization."""
    tracker = KalmanTracker()
    assert tracker.is_initialized() is False
    assert tracker.get_state() is None
    assert tracker.get_covariance() is None
    assert tracker.get_position() is None
    assert tracker.get_velocity() is None

    with pytest.raises(RuntimeError):
        tracker.predict(dt=0.033)

    with pytest.raises(RuntimeError):
        tracker.update(np.array([100.0, 200.0]))


def test_tracker_initialization():
    """Verify first valid detection properly initializes state vector and covariance."""
    cfg = TrackingConfig(
        initial_position_uncertainty=50.0,
        initial_velocity_uncertainty=200.0,
    )
    tracker = KalmanTracker(cfg)
    pos_0 = np.array([320.5, 240.5])
    tracker.initialize(pos_0, timestamp=1.0)

    assert tracker.is_initialized() is True
    pos = tracker.get_position()
    assert pos is not None
    assert np.isclose(pos[0], 320.5)
    assert np.isclose(pos[1], 240.5)

    vel = tracker.get_velocity()
    assert vel is not None
    assert np.isclose(vel[0], 0.0)
    assert np.isclose(vel[1], 0.0)

    cov = tracker.get_covariance()
    assert cov is not None
    assert cov.shape == (4, 4)
    assert np.isclose(cov[0, 0], 50.0)
    assert np.isclose(cov[1, 1], 50.0)
    assert np.isclose(cov[2, 2], 200.0)
    assert np.isclose(cov[3, 3], 200.0)


def test_static_target_convergence():
    """Verify that repeated observations of a stationary beacon converge to zero velocity."""
    cfg = TrackingConfig(process_noise=1.0, measurement_noise=2.0)
    tracker = KalmanTracker(cfg)
    tracker.initialize(np.array([300.0, 200.0]))

    dt = 0.033
    for _ in range(50):
        tracker.predict(dt)
        tracker.update(np.array([300.0, 200.0]))

    pos = tracker.get_position()
    vel = tracker.get_velocity()
    unc_p = tracker.get_position_uncertainty()

    assert pos is not None and vel is not None and unc_p is not None
    assert np.isclose(pos[0], 300.0, atol=0.1)
    assert np.isclose(pos[1], 200.0, atol=0.1)
    assert np.isclose(vel[0], 0.0, atol=0.2)
    assert np.isclose(vel[1], 0.0, atol=0.2)
    # Covariance should have converged to a small steady-state uncertainty
    assert unc_p[0] < 5.0
    assert unc_p[1] < 5.0


def test_constant_velocity_estimation():
    """Verify Kalman filter accurately tracks moving beacon and estimates velocity."""
    cfg = TrackingConfig(process_noise=5.0, measurement_noise=1.0)
    tracker = KalmanTracker(cfg)

    true_vx = 30.0  # px/s
    true_vy = -15.0  # px/s
    x0, y0 = 100.0, 300.0

    tracker.initialize(np.array([x0, y0]))

    dt = 0.0333  # ~30 FPS
    t = 0.0
    for i in range(1, 60):
        t += dt
        true_x = x0 + true_vx * t
        true_y = y0 + true_vy * t

        tracker.predict(dt)
        tracker.update(np.array([true_x, true_y]))

    pos = tracker.get_position()
    vel = tracker.get_velocity()

    assert pos is not None and vel is not None
    assert np.isclose(pos[0], true_x, atol=1.0)
    assert np.isclose(pos[1], true_y, atol=1.0)
    assert np.isclose(vel[0], true_vx, atol=2.0)
    assert np.isclose(vel[1], true_vy, atol=2.0)


def test_measurement_noise_filtering():
    """Verify Kalman filtered estimate has lower error variance than noisy measurements."""
    np.random.seed(42)
    cfg = TrackingConfig(process_noise=1.0, measurement_noise=16.0)
    tracker = KalmanTracker(cfg)

    true_x, true_y = 320.0, 240.0
    tracker.initialize(np.array([true_x, true_y]))

    noise_sigma = 4.0
    raw_errors = []
    filtered_errors = []

    dt = 0.033
    for _ in range(100):
        meas_x = true_x + np.random.normal(0, noise_sigma)
        meas_y = true_y + np.random.normal(0, noise_sigma)

        raw_errors.append((meas_x - true_x)**2 + (meas_y - true_y)**2)

        tracker.predict(dt)
        tracker.update(np.array([meas_x, meas_y]))

        fx, fy = tracker.get_position()
        filtered_errors.append((fx - true_x)**2 + (fy - true_y)**2)

    raw_rmse = np.sqrt(np.mean(raw_errors[20:]))
    filtered_rmse = np.sqrt(np.mean(filtered_errors[20:]))

    # Kalman filter must attenuate noise variance
    assert filtered_rmse < raw_rmse
    assert filtered_rmse < noise_sigma * 0.7


def test_lead_prediction():
    """Verify lead prediction projects state forward along estimated velocity vector."""
    tracker = KalmanTracker()
    tracker.initialize(np.array([200.0, 150.0]), initial_velocity=np.array([20.0, -10.0]))

    lead_state = tracker.predict_lead(lead_time=0.5)
    assert np.isclose(lead_state[0, 0], 200.0 + 20.0 * 0.5)
    assert np.isclose(lead_state[1, 0], 150.0 - 10.0 * 0.5)
    assert np.isclose(lead_state[2, 0], 20.0)
    assert np.isclose(lead_state[3, 0], -10.0)


def test_covariance_positive_definiteness():
    """Verify covariance matrix remains positive-definite and symmetric after many updates."""
    tracker = KalmanTracker()
    tracker.initialize(np.array([100.0, 100.0]))

    for i in range(100):
        dt = 0.02 + 0.01 * (i % 3)
        tracker.predict(dt)
        tracker.update(np.array([100.0 + i, 100.0 - 0.5 * i]))

        cov = tracker.get_covariance()
        assert cov is not None
        # Check symmetry
        assert np.allclose(cov, cov.T, atol=1e-8)
        # Check positive eigenvalues
        eigvals = np.linalg.eigvalsh(cov)
        assert np.all(eigvals > 0)


def test_tracker_reset():
    """Verify reset clears state, covariance, and marks tracker uninitialized."""
    tracker = KalmanTracker()
    tracker.initialize(np.array([320.0, 240.0]))
    assert tracker.is_initialized() is True

    tracker.reset()
    assert tracker.is_initialized() is False
    assert tracker.get_state() is None
    assert tracker.get_covariance() is None
