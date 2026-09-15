# Module 2 — Virtual World & Platform Simulation

**Team PHARO — SIH26169**

## Purpose
Simulates 3D spatial coordinate frames and physical kinematics of both the optical receiver terminal (Camera Platform) and optical transmitter terminal (Beacon Platform).

## Planned Capabilities
- **Coordinate Systems**: World reference frame (NED / Cartesian meters), platform body frame, optical boresight frame.
- **Motion Profiles**:
  - `static`: Fixed terminal coordinates.
  - `drift`: Constant linear velocity translation ($\mathbf{r}(t) = \mathbf{r}_0 + \mathbf{v} t$).
  - `sway`: Sinusoidal platform oscillations ($\mathbf{r}(t) = \mathbf{r}_0 + \mathbf{A} \sin(2\pi f t)$).
  - `orbit`: Circular/elliptical orbital trajectory around target reference point.
- **Relative Geometry**: Continuous calculation of true range, Line-of-Sight (LOS) azimuth, and elevation angles.

## Inputs from ScenarioConfig
- `ScenarioConfig.camera_platform`
- `ScenarioConfig.beacon_platform`
- `ScenarioConfig.beacon.trajectory`
