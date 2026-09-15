# Module 6 — Kalman Tracking

**Team PHARO — SIH26169**

## Purpose
Estimates true beacon spot position, velocity, and trajectory dynamics in the focal plane while filtering measurement noise and coasting through temporary dropouts.

## Planned Capabilities
- **Linear / Extended Kalman Filter (KF/EKF)**: 4-state $[x, y, \dot{x}, \dot{y}]^T$ or 6-state kinematic motion models.
- **Dropout Coasting**: Forward state covariance propagation when detector reports loss of detection.
- **Innovation Filtering**: Outlier rejection for false positive reflections or noise spikes.
- **State Prediction**: Lead prediction compensating for camera exposure, processing latency, and gimbal actuator lag.
