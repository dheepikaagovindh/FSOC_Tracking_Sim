# Module 13 — Visualization & Telemetry Streaming

**Team PHARO — SIH26169**

## Purpose
Provides visual output streams, 2D focal plane synthetic views with HUD crosshairs, and 3D terminal trajectory rendering.

## Planned Capabilities
- **2D Synthetic Focal Plane Stream**: Real-time rendering of camera sensor view with optical crosshairs, detected centroid marker, Kalman predicted track, and boresight target reticle.
- **3D World & Orbit Visualizer**: Interactive Three.js / WebGL visualization of terminal positions, gimbal orientation vectors, and optical beam cone in world space.
- **Real-Time Telemetry Dashboard**: Time-series charts for pointing error $(\Delta \text{Az}, \Delta \text{El})$, gimbal angular velocity, Kalman innovation, and disturbance state.
