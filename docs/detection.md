# Beacon Detection & Centroiding Specification (Module 5)

**FSOC AI-Based Virtual Camera Tracking Project**  
**Team PHARO — Smart India Hackathon (SIH26169)**

---

## 1. Purpose & Overview
The **Beacon Detection Module** is the optical perception stage of the Free-Space Optical Communication (FSOC) coarse alignment testbed. Its primary objective is to receive degraded focal plane observation frames from the **Disturbance & Noise Simulation Module (Module 4)**, locate the optical transmitter beacon spot on the image plane, and estimate continuous sub-pixel image coordinates $(\hat{u}, \hat{v})$ along with detection confidence and bounding geometry.

> [!IMPORTANT]
> **Strict Principle: No Ground-Truth Assistance**
> The Beacon Detector operates purely on the visual image pixels. It does **NOT** use ground-truth azimuth, elevation, 3D world position, range, or true projected $(u_{\text{true}}, v_{\text{true}})$ coordinates to assist, bias, or guide beacon detection. Ground truth is used strictly by offline benchmarking / telemetry for accuracy verification.

---

## 2. Input Contract
The detector accepts standard unprivileged image frames:
- **Image Input**: Disturbed camera sensor image ($H \times W$, `uint8` $[0, 255]$, grayscale or RGB).
- **Image Dimensions**: Width $W$ (default 640 px), Height $H$ (default 480 px).
- **Timestamp**: Frame simulation time $t$ in seconds.
- **Detector Configuration (`DetectionConfig`)**:
  - `method`: Detection algorithm (`opencv`, `mock`, future `yolo`).
  - `threshold`: Fixed intensity threshold (default 128).
  - `min_area`: Minimum spot area in pixels (default 4).
  - `max_area`: Maximum spot area in pixels (default 5000).
  - `min_brightness`: Minimum peak brightness (default 60).
  - `min_confidence`: Minimum confidence threshold to report detection (default 0.20).
  - `blur_kernel`: Preprocessing Gaussian filter kernel size (default 3, must be odd).
  - `use_otsu`: Boolean flag to enable Otsu automatic thresholding.
  - `morphology_enabled`: Morphological opening/closing noise suppression.

---

## 3. Output Contract (`DetectionResult`)
Every detection execution returns a structured, stable telemetry contract:

```json
{
  "detected": true,
  "center_x": 321.48,
  "center_y": 239.15,
  "u": 321.48,
  "v": 239.15,
  "confidence": 0.94,
  "candidate_count": 2,
  "bbox": {
    "x": 315,
    "y": 233,
    "width": 13,
    "height": 13
  },
  "timestamp": 2.0,
  "processing_time_ms": 2.34,
  "method": "opencv",
  "message": "Beacon spot localized successfully"
}
```

When no valid beacon candidate satisfies the detection constraints (or during dropout):
- `detected`: `false`
- `center_x`: `null`
- `center_y`: `null`
- `bbox`: `null`
- `confidence`: `0.0`
- `candidate_count`: `0`

---

## 4. Detection Pipeline

```
DISTURBED CAMERA SENSOR IMAGE (Module 4)
                  ↓
       1. Image Input Validation
                  ↓
       2. Grayscale Conversion (if 3-channel)
                  ↓
       3. Gaussian Blur Preprocessing (Optional)
                  ↓
       4. Intensity Thresholding (Fixed / Otsu / Adaptive)
                  ↓
       5. Morphological Cleanup (Opening / Closing)
                  ↓
       6. Connected Components / Contours Extraction
                  ↓
       7. Multi-Candidate Metric Computation & Filtering
                  ↓
       8. Candidate Scoring & Beacon Selection
                  ↓
       9. Sub-Pixel Center Calculation (Moments / CoM)
                  ↓
      10. Heuristic Confidence & Bounding Box Generation
                  ↓
  DETECTION RESULT TELEMETRY (For Future Module 6 Kalman Tracker)
```

---

## 5. Primary Detector: OpenCV Baseline (`OpenCVBeaconDetector`)
The OpenCV baseline detector provides a deterministic, lightweight, and robust classical computer vision implementation. It evaluates connected components without deep learning overhead, enabling near-real-time throughput (> 400 FPS) on standard CPU hardware.

---

## 6. Image Preprocessing (`preprocessing.py`)
1. **Input Validation**:
   - Ensures image is a valid 2D or 3D NumPy array of non-zero dimensions.
   - Converts `float` $[0.0, 1.0]$ ranges to `uint8` $[0, 255]$ if needed.
2. **Grayscale Conversion**:
   - Converts standard RGB/BGR arrays to single-channel luminance arrays using standard Rec.601 weights: $Y = 0.299R + 0.587G + 0.114B$.
3. **Gaussian Smoothing**:
   - If `blur_kernel >= 3`, applies a $(k \times k)$ Gaussian blur kernel to suppress single-pixel sensor shot noise while preserving the Point Spread Function (PSF) energy core.

---

## 7. Intensity Thresholding
Three configurable thresholding modes are supported:
1. **Fixed Intensity Threshold (Default)**:
   $$\text{Binary}(x, y) = \begin{cases} 255 & \text{if } I(x, y) \ge T_{\text{fixed}} \\ 0 & \text{otherwise} \end{cases}$$
2. **Otsu Automatic Binarization (`use_otsu=True`)**:
   - Computes intra-class variance minimization across the histogram to identify optimal bimodal separation.
3. **Adaptive Thresholding**:
   - Local neighbourhood adaptive Gaussian windowing for non-uniform illumination environments.

---

## 8. Candidate Extraction
Connected components are segmented via `cv2.findContours(..., cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`. For every candidate contour, the detector computes:
- Bounding box $(x, y, w, h)$
- Contour area $A$
- Spatial moments $(M_{00}, M_{10}, M_{01}, \mu_{20}, \mu_{02})$
- Peak intensity $I_{\max}$ within the bounding box
- Mean intensity $\bar{I}$
- Aspect ratio: $\text{AR} = \frac{\max(w, h)}{\min(w, h)}$
- Compactness: $\text{Compactness} = \frac{4\pi A}{P^2}$ where $P$ is the contour perimeter.

---

## 9. Candidate Filtering
Invalid candidates (e.g., thermal sensor hot pixels, background clutter, oversized glare) are rejected using configurable filter rules:
1. **Area Bounds**: $\text{min\_area} \le A \le \text{max\_area}$
2. **Dimensions**: $w \ge 2\text{ px}$ and $h \ge 2\text{ px}$ to eliminate isolated 1-pixel Gaussian spikes.
3. **Peak Brightness**: $I_{\max} \ge \text{min\_brightness}$
4. **Aspect Ratio**: $\text{AR} \le \text{max\_aspect\_ratio}$ (default $\le 3.5$)
5. **Background Contrast / PNR**: Contrast $I_{\max} - \mu_{\text{bg}} \ge 15$.

---

## 10. Candidate Scoring & Beacon Selection
When multiple bright candidates remain after filtering, they are scored using a normalized heuristic weight function:

$$\text{Score} = w_{\text{bright}} \cdot \left(\frac{I_{\max}}{255}\right) + w_{\text{area}} \cdot \text{AreaNorm}(A) + w_{\text{comp}} \cdot \text{Compactness}$$

- **Brightness Weight** ($w_{\text{bright}} = 0.50$): Favors laser/LED point sources with saturated optical cores.
- **Area Consistency** ($w_{\text{area}} = 0.25$): Matches the expected circular diffraction PSF footprint.
- **Compactness** ($w_{\text{comp}} = 0.25$): Penalizes elongated linear artifacts, streaks, and reflections.

The candidate with the highest composite score is selected as the active beacon spot.

---

## 11. Sub-Pixel Center Calculation & Confidence
1. **Sub-Pixel Centroid**:
   Calculated using image moments over the selected contour:
   $$\hat{u} = \frac{M_{10}}{M_{00}}, \quad \hat{v} = \frac{M_{01}}{M_{00}}$$
   where $M_{pq} = \sum_{x, y} x^p y^q I(x, y)$.

2. **Confidence Metric ($c \in [0.0, 1.0]$)**:
   Calculated as a heuristic quality metric combining:
   - Peak intensity ratio ($\frac{I_{\max}}{255}$)
   - Peak-to-Noise Ratio ($\text{PNR} = \frac{I_{\max} - \mu_{\text{bg}}}{\sigma_{\text{bg}}}$)
   - Contour circularity and compactness
   $$\text{Confidence} = \operatorname{clamp}\left(0.40 \cdot \frac{I_{\max}}{255} + 0.35 \cdot \sigma_{\text{sig}}(\text{PNR}) + 0.25 \cdot \text{Compactness}, \, 0.0, \, 1.0\right)$$

---

## 12. Dropout & Absence Behavior
When the optical beacon is occluded, dimmed below threshold, or dropped out by atmospheric turbulence (Module 4):
- The detector cleanly returns `detected = False`.
- `center_x = null`, `center_y = null`, `bbox = null`.
- No ghost coordinates, previous frame extrapolations, or ground-truth fallbacks are returned.
- Multi-frame temporal state estimation and re-acquisition is strictly delegated to the future Kalman Tracking Module (Module 6).

---

## 13. REST API Reference

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `POST` | `/detection/initialize` | Initialize detector from active scenario | `200`, `400` |
| `POST` | `/detection/reset` | Reset detection telemetry counters | `200`, `409` |
| `POST` | `/detection/config` | Dynamically update detector parameters | `200`, `400` |
| `POST` | `/detection/detect` | Run detection on latest disturbed sensor frame | `200`, `409` |
| `GET` | `/detection/result` | Retrieve latest detection result JSON | `200`, `409` |
| `GET` | `/detection/status` | Retrieve detector lifecycle and status | `200` |
| `GET` | `/detection/telemetry` | Retrieve execution telemetry and success rate | `200`, `409` |
| `GET` | `/detection/overlay` | Retrieve detection overlay image (PNG) | `200`, `409` |
| `GET` | `/detection/annotated-image`| Retrieve annotated HUD image (PNG) | `200`, `409` |

All endpoints are also prefixed under `/api/v1/detection/*`.

---

## 14. Frontend Dashboard Integration
The Mission Control UI provides a dedicated **Module 5: Beacon Detection & Centroiding** tab featuring:
- **`DetectionOverlay.jsx`**: Real-time sensor canvas overlay displaying cyan bounding boxes, green sub-pixel target reticles, and optical crosshairs without privileged ground-truth leakage.
- **`DetectionStatus.jsx`**: High-contrast status banner, heuristic confidence bar, sub-pixel $(u, v)$ coordinates, bounding box metrics, and candidate count.
- **`DetectionTelemetry.jsx`**: Execution latency benchmark, total frames processed, and cumulative detection success rate.
- **`DetectionControls.jsx`**: Interactive parameter sliders for threshold, area bounds, Gaussian blur kernel, Otsu mode, and detector method selector.

---

## 15. Testing & Verification Matrix
The test suite across `backend/tests/test_opencv_detector.py`, `backend/tests/test_detection.py`, and `backend/tests/test_detection_api.py` verifies:
- **Accuracy**: Sub-pixel radial error $< 0.15\text{ px}$ on clean and blurred synthetic beacons.
- **Off-Center Spot**: Accurate localization of $(400, 300)$ and arbitrary off-axis spots.
- **Noise Rejection**: Robust candidate extraction under Gaussian noise ($\sigma = 25$) and vibration jitter.
- **Multi-Object Ranking**: Strongest beacon correctly isolated from multiple distractor bright objects.
- **Dropout Handling**: Immediate `detected = False` when beacon is extinguished or out of FOV.
- **Edge Cases**: Zero-area handling, blank frames, saturated images, invalid configuration bounds.

---

## 16. Limitations & Future YOLO Integration
- **Current Baseline**: The classical OpenCV detector relies on intensity contrast and geometric compactness. It is sensitive to large diffuse background glares or complex textured optical clutter.
- **YOLO Deep Learning Architecture**:
  The system is built on the abstract `BaseDetector` interface (`backend/app/detection/base.py`). In a future module, a lightweight YOLO neural detector can be plugged in seamlessly:
  ```
  OpenCVBeaconDetector (Classical Baseline)
                   OR
  YOLOBeaconDetector (Deep Neural Network)
                   ↓
         Common DetectionResult
  ```
  The downstream Kalman Filter (Module 6) and Controller (Module 8) will consume the identical `DetectionResult` contract without requiring any code modifications.
