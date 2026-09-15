# Error Calculation & Boresight Alignment Specification (Module 7)

**FSOC AI-Based Virtual Camera Tracking Project**  
**Team PHARO — Smart India Hackathon (SIH26169)**

---

## 1. Purpose & Overview

The **Error Calculation & Alignment Module** is the optical boresight pointing error evaluation stage of the Free-Space Optical Communication (FSOC) coarse alignment testbed. Its primary objective is to receive continuous focal-plane target estimates from the **Beacon Tracking & Motion Prediction Module (Module 6)** and calculate high-precision alignment errors relative to the camera optical center (boresight axis).

The module calculates:
1. **Pixel Error**: $(e_x, e_y)$ and Euclidean pixel error magnitude $e_{\text{mag}}$.
2. **Normalized Image Error**: $(\bar{e}_x, \bar{e}_y) \in [-1.0, 1.0]$ and magnitude $\bar{e}_{\text{mag}}$.
3. **Angular Boresight Error**: $(\theta_x, \theta_y)$ in degrees and angular error magnitude $\theta_{\text{mag}}$.
4. **3D Conical Angular Separation**: $\theta_{\text{3D}}$ off the optical line-of-sight.
5. **Error Direction**: $\phi \in [-180^\circ, 180^\circ]$ vector angle.
6. **Error Derivative Rates**: $(\dot{e}_x, \dot{e}_y)$ in pixels per second.
7. **Alignment Lock Condition**: `ALIGNED` (within tolerance) vs `VALID` (tracking but misaligned) vs `INVALID` (lost/uninitialized).

> [!IMPORTANT]
> **Strict Principle: Ground-Truth Isolation**  
> Operational alignment errors are calculated strictly from the tracked/predicted beacon pixel coordinates produced by Module 6. Ground-truth 3D platform and beacon coordinates are **never** accessed for error calculation.

---

## 2. Coordinate System & Sign Conventions

The module strictly adheres to conventional image coordinates:
* Origin $(0, 0)$ is at the top-left corner of the sensor focal plane.
* Horizontal axis $+X$ points **Right**.
* Vertical axis $+Y$ points **Down**.
* Optical Center: $(c_x, c_y) = (W / 2.0, H / 2.0)$ (e.g. $(320.0, 240.0)$ for $640 \times 480$).

### Error Sign Interpretation

| Axis | Error Sign | Physical Interpretation |
| :--- | :--- | :--- |
| **Horizontal ($e_x, \theta_x$)** | Positive ($>0$) | Target is to the **RIGHT** of the optical boresight center |
| | Negative ($<0$) | Target is to the **LEFT** of the optical boresight center |
| **Vertical ($e_y, \theta_y$)** | Positive ($>0$) | Target is **BELOW** the optical boresight center ($+Y$ down) |
| | Negative ($<0$) | Target is **ABOVE** the optical boresight center |

---

## 3. Mathematical Formulations

### 3.1 Pixel Errors

Given target coordinates $(x_{\text{target}}, y_{\text{target}})$ and optical center $(c_x, c_y)$:

$$e_x = x_{\text{target}} - c_x$$
$$e_y = y_{\text{target}} - c_y$$
$$e_{\text{mag}} = \sqrt{e_x^2 + e_y^2}$$

### 3.2 Normalized Focal-Plane Errors

Normalized to unit radius relative to half-dimensions:

$$\bar{e}_x = \frac{e_x}{W / 2.0}, \qquad \bar{e}_y = \frac{e_y}{H / 2.0}$$
$$\bar{e}_{\text{mag}} = \sqrt{\bar{e}_x^2 + \bar{e}_y^2}$$

### 3.3 Angular Boresight Errors (Pinhole Projection)

From camera sensor dimensions $(W, H)$ and field-of-view $(\text{HFOV}, \text{VFOV})$:

$$f_x = \frac{W / 2.0}{\tan(\text{HFOV} / 2.0)}, \qquad f_y = \frac{H / 2.0}{\tan(\text{VFOV} / 2.0)}$$

The apparent angular pointing offsets in degrees:

$$\theta_x = \text{atan2}(e_x, f_x) \times \frac{180^\circ}{\pi}$$
$$\theta_y = \text{atan2}(e_y, f_y) \times \frac{180^\circ}{\pi}$$
$$\theta_{\text{mag}} = \sqrt{\theta_x^2 + \theta_y^2}$$

**Exact 3D Conical Angular Separation**:
$$\theta_{\text{3D}} = \text{atan2}\left(\sqrt{\left(\frac{e_x}{f_x}\right)^2 + \left(\frac{e_y}{f_y}\right)^2}, 1.0\right) \times \frac{180^\circ}{\pi}$$

### 3.4 Error Vector Direction

$$\phi = \text{atan2}(e_y, e_x) \times \frac{180^\circ}{\pi}$$

* $0^\circ$: Target is due Right $(+X)$
* $90^\circ$: Target is due Down $(+Y)$
* $\pm 180^\circ$: Target is due Left $(-X)$
* $-90^\circ$: Target is due Up $(-Y)$

### 3.5 Error Derivative Rates

$$\dot{e}_x = \frac{e_{x, k} - e_{x, k-1}}{\Delta t}, \qquad \dot{e}_y = \frac{e_{y, k} - e_{y, k-1}}{\Delta t}$$

---

## 4. Alignment / Lock Criteria

Alignment is achieved when pointing errors fall within user-configured tolerances:

### Angular Alignment Mode (Default)
* **Radial Lock**:
  $$\text{radially\_aligned} = \theta_{\text{mag}} \le \theta_{\text{tol}}$$
* **Component-wise Lock**:
  $$\text{aligned} = (|\theta_x| \le \theta_{\text{tol}}) \land (|\theta_y| \le \theta_{\text{tol}})$$

### Pixel Alignment Mode
* **Radial Lock**:
  $$\text{radially\_aligned} = e_{\text{mag}} \le \text{px}_{\text{tol}}$$
* **Component-wise Lock**:
  $$\text{aligned} = (|e_x| \le \text{px}_{\text{tol}}) \land (|e_y| \le \text{px}_{\text{tol}})$$

### Status Enum (`ErrorStatus`)
* **`ALIGNED`**: Target track is valid and error is within lock tolerance.
* **`VALID`**: Target track is valid, but error exceeds lock tolerance.
* **`INVALID`**: Tracker is `UNINITIALIZED`, `LOST`, or measurement corrupted.

---

## 5. Configuration Contract (`AlignmentConfig`)

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `enabled` | `bool` | `true` | Enables/disables error calculation engine |
| `pixel_tolerance` | `float` | `5.0` | Pixel radius tolerance for lock threshold (px) |
| `angular_tolerance_deg` | `float` | `0.25` | Angular threshold for lock condition (deg) |
| `use_angular_alignment` | `bool` | `true` | Evaluates lock condition using angular degrees |
| `use_radial_alignment` | `bool` | `true` | Requires radial magnitude $\le \text{tol}$ (circle vs box) |
| `use_prediction_when_tracking_missing` | `bool` | `true` | Uses motion prediction during detector dropouts |

---

## 6. Output Contract (`AlignmentError`)

```json
{
  "timestamp": 2.45,
  "valid": true,
  "status": "VALID",
  "source": "FILTERED",
  "target_x": 350.0,
  "target_y": 220.0,
  "center_x": 320.0,
  "center_y": 240.0,
  "pixel_error_x": 30.0,
  "pixel_error_y": -20.0,
  "pixel_error_magnitude": 36.056,
  "normalized_error_x": 0.0938,
  "normalized_error_y": -0.0833,
  "normalized_error_magnitude": 0.1254,
  "angular_error_x_deg": 1.4388,
  "angular_error_y_deg": -0.9634,
  "angular_error_magnitude_deg": 1.7317,
  "true_angular_separation_deg": 1.7308,
  "error_direction_deg": -33.69,
  "delta_error_x": 1.2,
  "delta_error_y": -0.8,
  "error_rate_x": 36.0,
  "error_rate_y": -24.0,
  "aligned": false,
  "radially_aligned": false,
  "tracking_confidence": 0.94,
  "image_width": 640,
  "image_height": 480,
  "horizontal_fov_deg": 30.0,
  "vertical_fov_deg": 22.5,
  "pixel_tolerance": 5.0,
  "angular_tolerance_deg": 0.25,
  "message": "Target VALID (Filtered Track | Pixel: 36.1px | Angular: 1.73°)"
}
```

---

## 7. REST API Endpoints

| Method | Path | Summary | Response |
| :--- | :--- | :--- | :--- |
| `POST` | `/error/initialize` | Initialize error engine from scenario | `ErrorStatusInfo` |
| `POST` | `/error/reset` | Clear error state to INVALID | `AlignmentError` |
| `GET` | `/error/status` | Retrieve lifecycle and statistics | `ErrorStatusInfo` |
| `POST` | `/error/calculate` | Calculate error from tracking packet | `AlignmentError` |
| `GET` | `/error/result` | Retrieve latest AlignmentError | `AlignmentError` |
| `POST` | `/error/config` | Update lock tolerances & modes | `ErrorStatusInfo` |
| `GET` | `/error/telemetry` | Real-time HUD diagnostics | `ErrorTelemetry` |
| `GET` | `/error/overlay` | Multi-layer boresight HUD PNG | `image/png` |
| `GET` | `/error/annotated-image`| PNG stream alias | `image/png` |

---

## 8. Integration with Future Modules

Module 7 outputs feed directly into:
* **Module 8 (Pan-Tilt / PID Controller)**:
  - Consumes `angular_error_x_deg` $\to$ Azimuth (Pan) proportional-integral loop.
  - Consumes `angular_error_y_deg` $\to$ Elevation (Tilt) proportional-integral loop.
  - Consumes `error_rate_x, error_rate_y` $\to$ Derivative error dampening.
  - Consumes `status` $\to$ Disables PID integration windup when `INVALID`.
* **Module 10 (Tracking FSM & Alignment Verification)**:
  - Monitors `aligned` and `status` to trigger Fine Tracking mode vs Coarse Acquisition mode.
