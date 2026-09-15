# FSOC Scenario Configuration Specification

**Team PHARO — SIH26169**

## 1. Overview
The Scenario Configuration Module is the single source of truth for parameterizing the Free-Space Optical Communication (FSOC) coarse alignment simulation pipeline.

```
USER CONFIGURATION / API / UI
              ↓
      ScenarioConfig (JSON / Pydantic)
              ↓
      ScenarioValidator (Physical bounds & consistency)
              ↓
      ScenarioFactory / Service
              ↓
      Simulation Initialization (World, Camera, Disturbances, Controllers)
```

## 2. Schema Specification

### 2.1 Camera (`CameraConfig`)
| Field | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `width` | int | 640 | $[64, 7680]$ | Sensor horizontal pixel count |
| `height` | int | 480 | $[64, 4320]$ | Sensor vertical pixel count |
| `horizontal_fov_deg` | float | 30.0 | $(0.0, 180.0)$ | Horizontal Field of View (deg) |
| `vertical_fov_deg` | float | 22.5 | $(0.0, 180.0)$ | Vertical Field of View (deg) |
| `initial_pan_deg` | float | 0.0 | $[-180.0, 180.0]$ | Initial gimbal pan offset (deg) |
| `initial_tilt_deg` | float | 0.0 | $[-90.0, 90.0]$ | Initial gimbal tilt offset (deg) |

### 2.2 Platform Kinematics (`PlatformConfig`)
| Field | Type | Default | Valid Values | Description |
|---|---|---|---|---|
| `motion_profile` | string | "static" | `static`, `drift`, `sway`, `orbit` | Platform motion model |
| `initial_position_x` | float | 0.0 | Any float | Initial World X position (m) |
| `initial_position_y` | float | 0.0 | Any float | Initial World Y position (m) |
| `initial_position_z` | float | 0.0 / 1000.0 | Any float | Initial World Z position (m) |
| `velocity_x` | float | 0.0 | Any float | Translation velocity X (m/s) |
| `velocity_y` | float | 0.0 | Any float | Translation velocity Y (m/s) |
| `velocity_z` | float | 0.0 | Any float | Translation velocity Z (m/s) |
| `amplitude` | float | 0.0 | $\ge 0.0$ | Oscillation/orbit amplitude |
| `frequency` | float | 0.0 | $\ge 0.0$ | Oscillation/orbit frequency (Hz) |

### 2.3 Beacon Transmitter (`BeaconConfig`)
| Field | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `brightness` | float | 1.0 | $(0.0, 100.0]$ | Normalized optical intensity |
| `size` | float | 5.0 | $(0.0, 500.0]$ | Effective spot diameter |
| `trajectory` | string | "static" | `static`, `linear`, `circular`, `custom` | Relative motion profile |
| `trajectory_parameters` | dict | `{}` | Key-value pairs | Custom trajectory parameters |

### 2.4 Disturbances (`DisturbanceConfig`)
| Field | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `severity` | string | "off" | `off`, `low`, `medium`, `high` | Master severity preset |
| `vibration_enabled` | bool | False | True/False | Toggle platform vibration |
| `vibration_magnitude` | float | 0.0 | $\ge 0.0$ | RMS jitter magnitude |
| `noise_enabled` | bool | False | True/False | Toggle sensor noise |
| `noise_magnitude` | float | 0.0 | $\ge 0.0$ | Noise standard deviation |
| `blur_enabled` | bool | False | True/False | Toggle optical blur |
| `blur_strength` | float | 0.0 | $\ge 0.0$ | Blur PSF kernel sigma |
| `dropout_enabled` | bool | False | True/False | Toggle atmospheric dropouts |
| `dropout_probability`| float | 0.0 | $[0.0, 1.0]$ | Dropout rate per frame |
| `dropout_duration` | float | 0.0 | $\ge 0.0$ | Mean burst duration (sec) |

### 2.5 Simulation Execution (`SimulationConfig`)
| Field | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `duration` | float | 30.0 | $(0.0, 3600.0]$ | Duration in seconds |
| `fps` | float | 30.0 | $(0.0, 240.0]$ | Target frame rate |
| `random_seed` | int | 42 | $\ge 0$ | Seed for stochastic engines |
| `record_telemetry` | bool | True | True/False | Time-series logging toggle |
| `record_frames` | bool | False | True/False | Raw frame recording toggle |
