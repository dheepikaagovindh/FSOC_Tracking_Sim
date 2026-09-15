# Virtual World & Platform Kinematics Simulation Specification

**Team PHARO — Smart India Hackathon (SIH26169)**  
**Module 2 Technical Specification**

---

## 1. Overview & Purpose
The **Virtual World & Platform Simulation Module** provides a deterministic 3D simulation environment for Free-Space Optical Communication (FSOC) coarse alignment research.

It tracks the instantaneous spatial coordinates, velocities, and relative geometry between two optical communication terminals:
1. **Camera Platform (Receiver Terminal)**
2. **Beacon Platform (Transmitter Terminal)**

This module serves as the **numerical ground-truth source** for all downstream pipeline modules (Virtual Camera Rendering, Disturbance Simulation, Beacon Detection, Kalman Tracking, PID Gimbal Control, and Performance Evaluation).

```
+-------------------------------------------------------------+
|               SCENARIO CONFIGURATION (MODULE 1)             |
|   (Camera Platform Kinematics, Beacon Platform Kinematics)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|           VIRTUAL WORLD & PLATFORMS (MODULE 2)              |
|                                                             |
|   • 3D Coordinate Frame: X (Horiz), Y (Vert), Z (Forward)   |
|   • Simulation Clock (t >= 0, dt = 1/FPS)                   |
|   • Motion Engine: STATIC, DRIFT, SWAY, ORBIT               |
|   • Analytical Position & Velocity Evaluation               |
|   • Ground-Truth Relative Geometry: Range, Azimuth, Elev    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               FUTURE DOWNSTREAM PIPELINE CONSUMERS          |
|                                                             |
|   • Module 3: Virtual Camera (Focal Plane Spot Projection)  |
|   • Module 4: Disturbance Engine (Jitter & Scintillation)   |
|   • Module 5: Spot Detection & Centroiding                  |
|   • Module 6: Kalman State Estimator & Tracker              |
|   • Module 8: PID Gimbal Pan-Tilt Controller                |
+-------------------------------------------------------------+
```

---

## 2. World Coordinate System

We define a standard right-handed Cartesian coordinate system:

$$\text{Origin: } (0, 0, 0)$$

| Axis | Orientation | Physical Interpretation |
|---|---|---|
| **$X$** | Horizontal Axis | Lateral displacement (left negative, right positive) |
| **$Y$** | Vertical Axis | Altitude / vertical displacement (down negative, up positive) |
| **$Z$** | Depth / Forward Axis | Optical propagation axis / line-of-sight distance |

All coordinates and distances are represented as floating-point values in **meters ($\text{m}$)**.  
All velocities are represented in **meters per second ($\text{m/s}$)**.

---

## 3. Platform Model & Kinematics

Each terminal platform is modeled via `PlatformDefinition` and evaluated instantaneously via `MotionEngine`:

### 3.1 STATIC Motion Profile
The platform remains stationary at its initial coordinates:

$$\mathbf{P}(t) = \mathbf{P}_0$$

$$\mathbf{V}(t) = (0, 0, 0)$$

### 3.2 DRIFT Motion Profile
Constant linear velocity translation:

$$\mathbf{P}(t) = \mathbf{P}_0 + \mathbf{V}_0 \cdot t$$

$$\mathbf{V}(t) = \mathbf{V}_0$$

### 3.3 SWAY Motion Profile
Harmonic sinusoidal oscillation simulating platform vibration, oceanic wave sway, or aerodynamic flutter:

$$x(t) = x_0 + A_x \sin(2\pi f t + \phi_x)$$

$$y(t) = y_0 + A_y \sin(2\pi f t + \phi_y)$$

$$z(t) = z_0 + A_z \sin(2\pi f t + \phi_z)$$

**Analytical Velocities:**

$$v_x(t) = A_x \cdot (2\pi f) \cdot \cos(2\pi f t + \phi_x)$$

$$v_y(t) = A_y \cdot (2\pi f) \cdot \cos(2\pi f t + \phi_y)$$

$$v_z(t) = A_z \cdot (2\pi f) \cdot \cos(2\pi f t + \phi_z)$$

### 3.4 ORBIT Motion Profile
Circular / elliptical motion in the horizontal $X$-$Z$ plane around orbit center $\mathbf{c} = (c_x, c_y, c_z)$ with radius $R = A$ and frequency $f$:

$$x(t) = c_x + R \cos(2\pi f t + \phi)$$

$$y(t) = c_y$$

$$z(t) = c_z + R \sin(2\pi f t + \phi)$$

**Analytical Velocities:**

$$v_x(t) = -R \cdot (2\pi f) \cdot \sin(2\pi f t + \phi)$$

$$v_y(t) = 0$$

$$v_z(t) = R \cdot (2\pi f) \cdot \cos(2\pi f t + \phi)$$

---

## 4. Ground-Truth Relative Geometry

Given Camera Platform position $\mathbf{P}_c(t) = (x_c, y_c, z_c)$ and Beacon Platform position $\mathbf{P}_b(t) = (x_b, y_b, z_b)$:

### 4.1 Relative Position Vector
$$\Delta \mathbf{P} = \mathbf{P}_b - \mathbf{P}_c = (\Delta x, \Delta y, \Delta z)$$

$$\Delta x = x_b - x_c, \quad \Delta y = y_b - y_c, \quad \Delta z = z_b - z_c$$

### 4.2 Euclidean Range
$$R = \|\Delta \mathbf{P}\| = \sqrt{\Delta x^2 + \Delta y^2 + \Delta z^2}$$

### 4.3 Azimuth / Bearing ($\theta_{\text{az}}$)
Horizontal angle in degrees in the $X$-$Z$ plane:

$$\theta_{\text{az}} = \operatorname{atan2}(\Delta x, \Delta z) \cdot \frac{180^\circ}{\pi}$$

- $\theta_{\text{az}} = 0^\circ$: Beacon directly along forward $Z$-axis boresight.
- $\theta_{\text{az}} > 0^\circ$: Beacon displaced to the right ($+X$).
- $\theta_{\text{az}} < 0^\circ$: Beacon displaced to the left ($-X$).

### 4.4 Elevation Angle ($\theta_{\text{el}}$)
Vertical angle in degrees relative to the horizontal $X$-$Z$ plane:

$$R_{\text{horiz}} = \sqrt{\Delta x^2 + \Delta z^2}$$

$$\theta_{\text{el}} = \operatorname{atan2}(\Delta y, R_{\text{horiz}}) \cdot \frac{180^\circ}{\pi}$$

- $\theta_{\text{el}} = 0^\circ$: Beacon coplanar with receiver horizon ($y_b = y_c$).
- $\theta_{\text{el}} > 0^\circ$: Beacon elevated above receiver ($+Y$).
- $\theta_{\text{el}} < 0^\circ$: Beacon depressed below receiver ($-Y$).

> [!NOTE]
> **Boundary Safety**: If range $R = 0$ (both terminals co-located), $R = 0, \theta_{\text{az}} = 0^\circ, \theta_{\text{el}} = 0^\circ$. If $R_{\text{horiz}} = 0$ with $\Delta y \neq 0$, elevation correctly evaluates to $\pm 90^\circ$ without division-by-zero.

---

## 5. Simulation Clock & Determinism

- Simulation time $t \ge 0$ advances discretely by timestep $dt = 1 / \text{FPS}$.
- Stepping is decoupled from wall-clock execution for exact repeatability and test reproducibility.
- Identical `ScenarioConfig` + initial conditions + time $t$ produce 100% bit-exact results across platforms.

---

## 6. REST API Reference

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `POST` | `/world/initialize` | Initialize world state from `ScenarioConfig` | `200`, `400` |
| `POST` | `/world/reset` | Reset simulation time to $t=0.0$ | `200`, `409` |
| `POST` | `/world/step` | Advance clock by $dt$ (defaults to $1/\text{FPS}$) | `200`, `400`, `409` |
| `POST` | `/world/time` | Explicitly set simulation clock to $t$ | `200`, `400`, `409` |
| `GET` | `/world/state` | Retrieve full ground-truth world state snapshot | `200`, `409` |
| `GET` | `/world/platform/{id}` | Retrieve state for `'camera'` or `'beacon'` | `200`, `404`, `409` |
| `GET` | `/world/geometry` | Retrieve ground-truth relative geometry | `200`, `409` |
| `GET` | `/world/status` | Retrieve clock, initialization status, and metadata | `200` |

---

## 7. Downstream Module Integration Interface

When **Module 3 (Virtual Camera & Optical Projection)** is implemented, it will consume:
1. `world.get_camera_platform()` $\to$ Instantaneous receiver position $\mathbf{P}_c$.
2. `world.get_beacon_platform()` $\to$ Instantaneous transmitter position $\mathbf{P}_b$.
3. `world.get_relative_geometry()` $\to$ Line-of-sight vector, true range, and spherical bearing angles $(\theta_{\text{az}}, \theta_{\text{el}})$.
4. Transform ground-truth LOS angles through gimbal pointing attitude $(\text{Pan}, \text{Tilt})$ and camera focal length to compute focal plane spot coordinates $(u, v)$ in pixels.
