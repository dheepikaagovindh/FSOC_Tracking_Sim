# Module 7 & 8 — Error Calculation & PID Control

**Team PHARO — SIH26169**

## Purpose
Calculates angular boresight pointing error between the optical center and the estimated beacon spot, generating corrective pan/tilt motor rate commands.

## Planned Capabilities
- **Boresight Error Mapping**: Conversion of pixel offsets $(\Delta u, \Delta v)$ to angular errors $(\Delta \text{Az}, \Delta \text{El})$ using camera focal length calibration.
- **Dual-Axis PID Controller**: Independent proportional-integral-derivative controllers for Pan (Azimuth) and Tilt (Elevation) axes.
- **Anti-Windup & Saturation**: Integrator clamping and command rate limiting to prevent actuator overshoot.
- **Feed-Forward Control**: Velocity feed-forward using Kalman velocity estimates to minimize dynamic tracking lag.
