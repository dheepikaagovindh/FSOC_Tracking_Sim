# Module 9 — Gimbal & Actuator Simulation

**Team PHARO — SIH26169**

## Purpose
Simulates physical 2-DOF pan-tilt gimbal electro-mechanical dynamics, motor response limits, and encoder feedback.

## Planned Capabilities
- **Mechanical Dynamics**: 2nd-order transfer function modeling motor torque, inertia, damping, and back-EMF.
- **Actuator Physical Limits**: Max slew rate ($\omega_{\max} \approx 60^\circ/\text{s}$), max angular acceleration ($\alpha_{\max}$), and mechanical travel limits.
- **Encoder Simulation**: Discrete angular encoder resolution with quantization noise.
- **Orientation Update**: Closed-loop orientation feedback updating camera boresight vector in the world frame.
