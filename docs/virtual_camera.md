# Virtual Camera & Optical Image Generation Specification

**Team PHARO — Smart India Hackathon (SIH26169)**  
**Module 3 Technical Specification**

---

## 1. Overview & Purpose
The **Virtual Camera & Optical Rendering Module** bridges the 3D ground-truth kinematic world (Module 2) and the 2D synthetic optical receiver focal plane.

It models:
1. **Pinhole Camera Optical Intrinsics**: Derives focal lengths ($f_x, f_y$) and principal point ($c_x, c_y$) from configured resolution and Field-of-View (FOV) angles.
2. **Gimbal Frame Transformation**: Rotates world-relative line-of-sight displacement vectors into the camera's reference frame based on 2-DOF pan (yaw) and tilt (pitch) gimbal angles.
3. **Focal Plane Projection**: Maps 3D camera-frame coordinates to 2D continuous pixel coordinates $(u, v)$ with boundary clipping and visibility classification.
4. **Apparent Angular Bearing**: Computes boresight-relative azimuth ($\theta_{\text{az}}$) and elevation ($\theta_{\text{el}}$) tracking errors.
5. **Synthetic Sensor Rendering**: Synthesizes 8-bit grayscale optical sensor frames containing the focused laser beacon spot with configurable intensity and footprint radius.

```
+-------------------------------------------------------------+
|               VIRTUAL WORLD ENGINE (MODULE 2)               |
|  Camera Platform Position P_c(t), Beacon Position P_b(t)    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|       GIMBAL ORIENTATION & COORDINATE TRANSFORMATION        |
|  r_world = P_b - P_c                                        |
|  r_cam = R_X(tilt) * R_Y(pan) * r_world                     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               PINHOLE PROJECTION & ANGLES                   |
|  u = fx * (X_cam / Z_cam) + cx                              |
|  v = cy - fy * (Y_cam / Z_cam)                              |
|  θ_az = atan2(X_cam, Z_cam)                                 |
|  θ_el = atan2(Y_cam, sqrt(X_cam^2 + Z_cam^2))               |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               SYNTHETIC SENSOR FRAME SYNTHESIS              |
|  • 8-bit Grayscale NumPy Matrix (Height x Width)            |
|  • Beacon Spot Footprint & Intensity Mapping                |
|  • Lossless PNG Byte Stream Encoding                        |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               DOWNSTREAM PIPELINE CONSUMERS                 |
|  • Module 4: Disturbance Simulation (Jitter, Blur, Fades)   |
|  • Module 5: Spot Detection & AI Centroiding                |
|  • Module 6: Kalman State Estimator & Coasting              |
|  • Module 8: Dual-Axis PID Gimbal Controller                |
+-------------------------------------------------------------+
```

---

## 2. Coordinate Frames & Transformations

### 2.1 World Coordinate Frame ($\mathcal{F}_W$)
- $+X_W$: Horizontal right
- $+Y_W$: Vertical up
- $+Z_W$: Forward (optical propagation direction)

### 2.2 Camera Reference Frame ($\mathcal{F}_C$)
- $+X_C$: Camera sensor right
- $+Y_C$: Camera sensor up
- $+Z_C$: Optical axis / boresight direction (forward)

### 2.3 Gimbal Rotation Conventions
- **Pan ($\psi$ / `pan_deg`)**: Gimbal rotation about world $+Y_W$ axis (yaw). Positive pan turns the camera right.
- **Tilt ($\theta$ / `tilt_deg`)**: Gimbal rotation about camera lateral $+X_C$ axis (pitch). Positive tilt pitches the camera upward.

### 2.4 Transformation Mathematics
Given world-relative displacement $\mathbf{r}_W = \mathbf{P}_b - \mathbf{P}_c = (\Delta x, \Delta y, \Delta z)^T$:

$$\mathbf{r}_C = \mathbf{R}_X(\theta) \cdot \mathbf{R}_Y(\psi) \cdot \mathbf{r}_W$$

$$\mathbf{R}_Y(\psi) = \begin{bmatrix} \cos\psi & 0 & -\sin\psi \\ 0 & 1 & 0 \\ \sin\psi & 0 & \cos\psi \end{bmatrix}$$

$$\mathbf{R}_X(\theta) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta \\ 0 & \sin\theta & \cos\theta \end{bmatrix}$$

Expanding analytically:
$$X_1 = \Delta x \cos\psi - \Delta z \sin\psi$$
$$Y_1 = \Delta y$$
$$Z_1 = \Delta x \sin\psi + \Delta z \cos\psi$$

$$X_C = X_1$$
$$Y_C = Y_1 \cos\theta - Z_1 \sin\theta$$
$$Z_C = Y_1 \sin\theta + Z_1 \cos\theta$$

---

## 3. Optical Pinhole Model & Intrinsics

Given sensor width $W$ (pixels), height $H$ (pixels), horizontal field of view $\text{HFOV}$ (deg), and vertical field of view $\text{VFOV}$ (deg):

### 3.1 Focal Lengths
$$f_x = \frac{W}{2 \cdot \tan\left(\frac{\text{HFOV}_{\text{rad}}}{2}\right)}$$

$$f_y = \frac{H}{2 \cdot \tan\left(\frac{\text{VFOV}_{\text{rad}}}{2}\right)}$$

### 3.2 Principal Point (Optical Center)
$$c_x = \frac{W}{2.0}, \quad c_y = \frac{H}{2.0}$$

### 3.3 Intrinsic Matrix $\mathbf{K}$
$$\mathbf{K} = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

---

## 4. Focal Plane Projection & Apparent Angles

### 4.1 Pixel Coordinates $(u, v)$
For a point $\mathbf{r}_C = (X_C, Y_C, Z_C)$ in front of the camera ($Z_C > 0$):

$$u = f_x \cdot \frac{X_C}{Z_C} + c_x$$

$$v = c_y - f_y \cdot \frac{Y_C}{Z_C}$$

> [!NOTE]
> The vertical coordinate $v$ uses subtraction because in standard digital image conventions, $v = 0$ is the **top** of the image and increases **downward**, whereas physical camera $Y_C$ is defined **upward**.

### 4.2 Apparent Angular Bearing Relative to Boresight
$$\theta_{\text{az}} = \operatorname{atan2}(X_C, Z_C) \cdot \frac{180^\circ}{\pi}$$

$$\theta_{\text{el}} = \operatorname{atan2}\left(Y_C, \sqrt{X_C^2 + Z_C^2}\right) \cdot \frac{180^\circ}{\pi}$$

### 4.3 Visibility Classification
A target is classified as:
- **`VISIBLE`**: $Z_C > 0$ and $0 \le u < W$ and $0 \le v < H$.
- **`BEHIND_CAMERA`**: $Z_C \le 0$.
- **`OUT_OF_FOV`**: $Z_C > 0$, but $u < 0$, $u \ge W$, $v < 0$, or $v \ge H$.

---

## 5. Synthetic Image Synthesis

### 5.1 Spot Footprint & Intensity
Given `BeaconConfig.brightness` $B \in [0.0, 1.0]$ and `BeaconConfig.size` $S > 0$:
- **Intensity**: $I = \operatorname{round}(B \cdot 255) \in [0, 255]$.
- **Radius**: $r = \max(1.0, S / 2.0)$ pixels.

### 5.2 Rasterization
For pixels $(x, y)$ in the bounding neighborhood $[u - r, u + r] \times [v - r, v + r]$:

$$\text{pixel}(y, x) = \begin{cases} I & \text{if } (x - u)^2 + (y - v)^2 \le r^2 \\ 0 & \text{otherwise} \end{cases}$$

The generated image is a 2D `uint8` NumPy array of shape $(H, W)$, encoded to PNG for web transmission.

---

## 6. REST API Reference

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `POST` | `/camera/initialize` | Initialize camera optical parameters and sync with scenario | `200`, `400` |
| `POST` | `/camera/reset` | Reset gimbal orientation to initial configured pan/tilt | `200`, `409` |
| `POST` | `/camera/pose` | Set explicit gimbal pan and tilt orientation angles | `200`, `400`, `409` |
| `POST` | `/camera/capture` | Capture and render fresh optical sensor frame at current timestamp | `200`, `409` |
| `GET` | `/camera/frame` | Retrieve latest frame metadata (projection, angles, visibility) | `200`, `409` |
| `GET` | `/camera/image` | Retrieve rendered 8-bit synthetic optical image as PNG | `200`, `409` |
| `GET` | `/camera/intrinsics`| Retrieve optical intrinsic parameters ($f_x, f_y, c_x, c_y$, matrix $\mathbf{K}$) | `200`, `409` |
| `GET` | `/camera/status` | Retrieve camera status, optical configuration, and pose | `200` |
| `GET` | `/camera/telemetry`| Retrieve comprehensive real-time optical tracking telemetry | `200`, `409` |

---

## 7. Canonical Test Cases & Verification Matrix

The test suite in `backend/tests/test_camera.py` validates 7 canonical optical geometry requirements:

| # | Test Scenario | Inputs | Expected Output | Status |
|---|---|---|---|---|
| 1 | Center Boresight | $\mathbf{P}_c=(0,0,0), \text{pan}=0, \text{tilt}=0, \mathbf{P}_b=(0,0,50)$ | $u=320.0, v=240.0, \theta_{\text{az}}=0^\circ, \theta_{\text{el}}=0^\circ$, `VISIBLE` | **PASSED** |
| 2 | Horizontal Offset | $\mathbf{P}_c=(0,0,0), \text{pan}=0, \text{tilt}=0, \mathbf{P}_b=(10,0,50)$ | $u > 320, v=240, \theta_{\text{az}} = 11.31^\circ$, `VISIBLE` | **PASSED** |
| 3 | Vertical Offset | $\mathbf{P}_c=(0,0,0), \text{pan}=0, \text{tilt}=0, \mathbf{P}_b=(0,8,50)$ | $u=320, v < 240, \theta_{\text{el}} = 9.09^\circ$, `VISIBLE` | **PASSED** |
| 4 | Behind Camera | $\mathbf{P}_c=(0,0,0), \text{pan}=0, \text{tilt}=0, \mathbf{P}_b=(0,0,-50)$ | `visible = False`, `BEHIND_CAMERA` | **PASSED** |
| 5 | Out of FOV | $\mathbf{P}_c=(0,0,0), \text{pan}=0, \text{tilt}=0, \mathbf{P}_b=(100,0,50)$ | $u \ge 640$, `visible = False`, `OUT_OF_FOV` | **PASSED** |
| 6 | Pan Compensation | $\mathbf{P}_b=(10,0,50), \text{pan} = \operatorname{atan2}(10, 50)$ | $r_{C,x} = 0, u = 320.0, \theta_{\text{az}} = 0^\circ$ | **PASSED** |
| 7 | Tilt Compensation | $\mathbf{P}_b=(0,10,50), \text{tilt} = \operatorname{atan2}(10, 50)$ | $r_{C,y} = 0, v = 240.0, \theta_{\text{el}} = 0^\circ$ | **PASSED** |
