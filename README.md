# FSOC Coarse Alignment Simulator

**Software-Only Free-Space Optical Communication Coarse Alignment Simulator**  
**Team PHARO — Smart India Hackathon (SIH26169)**

---

## 1. Project Purpose & Problem Statement
In Free-Space Optical Communication (FSOC) and inter-satellite / airborne laser communication links, establishing and maintaining the optical Line-of-Sight (LOS) requires extreme precision (sub-milliradian pointing). Before high-bandwidth fine tracking (e.g. Fast Steering Mirrors / quadrant detectors) can lock onto a beam, a **Coarse Alignment & Acquisition System** must locate the optical beacon in a wide field-of-view camera, estimate its kinematic trajectory through severe disturbances (platform micro-vibrations, aerodynamic sway, atmospheric scintillation, and dropouts), and drive a 2-DOF pan-tilt gimbal to align the optical boresight.

This software-only simulator provides an end-to-end sandbox to develop, test, and benchmark AI/CV detection, Kalman state estimation, PID gimbal control, and acquisition finite state machines without requiring physical optical test benches.

---

## 2. Complete Closed-Loop Pipeline Vision

```
SIMULATE (World & Platforms)            <--- [MODULE 2 COMPLETED]
    ↓
RENDER (Virtual Camera & Optics)         <--- [MODULE 3 COMPLETED]
    ↓
DISTURB (Vibrations, Sensor Noise, Blur) <--- [MODULE 4 COMPLETED]
    ↓
DETECT (Centroiding & Sub-Pixel Localization) <--- [MODULE 5 COMPLETED]
    ↓
TRACK (Kalman State Estimator & Coasting)
    ↓
CALCULATE ERROR (Boresight Angular Offsets)
    ↓
CONTROL (Dual-Axis PID / Feed-Forward)
    ↓
GIMBAL MOVEMENT (Pan-Tilt Dynamic Actuators)
    ↓
UPDATED CAMERA VIEW (Closed-Loop Rendering)
    ↓
RE-ACQUIRE IF LOST (Supervisory Tracking FSM)
    ↓
EVALUATE (CEP50, Jitter RMS, TTA Metrics)
```

---

## 3. Current Development Stage: Modules 1–5 Completed

### Module 1: Scenario Configuration
- Typed Pydantic v2 configuration models (`ScenarioConfig`).
- 7 Progressive Presets (Easy Acquisition to Full Stress Test).
- Dedicated Physical Bounds & Domain Validator.
- Simulation initialization contract factory.

### Module 2: Virtual World & Platform Simulation
- **3D Cartesian Coordinate System**: $X$ = Horizontal, $Y$ = Vertical, $Z$ = Depth / Forward axis.
- **Platform Kinematics**:
  - `STATIC`: Fixed coordinates, zero velocity.
  - `DRIFT`: Constant linear velocity ($\mathbf{P}_0 + \mathbf{V}_0 t$).
  - `SWAY`: Sinusoidal oscillation ($\mathbf{P}_0 + \mathbf{A}\sin(2\pi f t)$) with exact analytical velocity ($\mathbf{A} 2\pi f \cos(2\pi f t)$).
  - `ORBIT`: Circular motion in $X$-$Z$ plane with exact analytical velocity.
- **Ground-Truth Relative Geometry**:
  - Distance / Range $R = \sqrt{\Delta x^2 + \Delta y^2 + \Delta z^2}$
  - Azimuth $\theta_{\text{az}} = \operatorname{atan2}(\Delta x, \Delta z)$ in degrees
  - Elevation $\theta_{\text{el}} = \operatorname{atan2}(\Delta y, \sqrt{\Delta x^2 + \Delta z^2})$ in degrees
  - Robust division-by-zero boundary handling.
- **Simulation Clock**: Independent discrete clock ($dt = 1/\text{FPS}$, step, reset, set time).
- **FastAPI Endpoints**: `/world/initialize`, `/world/reset`, `/world/step`, `/world/time`, `/world/state`, `/world/platform/{id}`, `/world/geometry`, `/world/status`.

### Module 3: Virtual Camera & Optical Image Generation
- **Pinhole Optical Intrinsics**: Derives focal lengths ($f_x, f_y$), principal point ($c_x, c_y$), and matrix $\mathbf{K}$ from resolution and FOV.
- **Gimbal Coordinate Rotation**: Transforms world LOS vectors into camera sensor frame via $\mathbf{R}_X(\text{tilt}) \cdot \mathbf{R}_Y(\text{pan})$.
- **Focal Plane Projection**: Continuous $(u, v)$ pixel projection, normalized camera coordinates, and apparent azimuth/elevation bearings.
- **Visibility & Boundary Diagnostics**: Classifies beacon as `VISIBLE`, `BEHIND_CAMERA`, or `OUT_OF_FOV`.
- **Synthetic Frame Synthesis**: 8-bit grayscale optical sensor rendering with Gaussian/disk laser spot rasterization and PNG byte stream encoding.
- **FastAPI Endpoints**: `/camera/initialize`, `/camera/reset`, `/camera/pose`, `/camera/capture`, `/camera/frame`, `/camera/image`, `/camera/intrinsics`, `/camera/status`, `/camera/telemetry`.
- **Frontend HUD Optical Viewfinder**: Interactive synthetic focal plane canvas, HUD crosshair reticles, dynamic target tracking diamond, interactive pan-tilt manual steering sliders & nudge controls, auto-center assistance, and real-time optical telemetry cards.

### Module 4: Disturbance & Noise Simulation
- **Sensor Noise Model**: Zero-mean additive Gaussian noise $I' = \operatorname{clip}(I + \mathcal{N}(0, \sigma^2), 0, 255)$ with deterministic frame RNG.
- **Optical & Atmospheric Blur**: 2D Gaussian PSF dispersion kernel modeling turbulence and defocus.
- **Platform Micro-Vibration**: Harmonic 2D image-plane jitter displacement $dx(t), dy(t)$ with affine shift and black border policy (no wrap-around).
- **Beacon Dropout**: Deterministic temporal burst state machine simulating atmospheric deep fades without invoking any computer vision detector.
- **Severity Presets**: Progressive preset scaling across `OFF`, `LOW`, `MEDIUM`, and `HIGH` with fine-grained parameter overrides.
- **FastAPI Endpoints**: `/disturbance/initialize`, `/disturbance/reset`, `/disturbance/config`, `/disturbance/process`, `/disturbance/frame`, `/disturbance/image`, `/disturbance/status`, `/disturbance/telemetry`.
- **Frontend Comparative Viewfinder**: Side-by-side comparative display (`Clean Camera Frame` vs `Disturbed Observation`), interactive severity buttons, parameter sliders, and real-time telemetry diagnostics.

### Module 5: Beacon Detection & Centroiding
- **Robust Background Estimation**: Median and Median Absolute Deviation (MAD) for spot-resistant $\mu_{\text{bg}}, \sigma_{\text{bg}}$ estimation.
- **Dynamic $k$-$\sigma$ Thresholding**: Adaptive segmentation threshold $T = \mu_{\text{bg}} + k_\sigma \cdot \sigma_{\text{bg}}$.
- **Centroiding Algorithms**:
  - Intensity-Weighted Center of Mass (CoM).
  - Adaptive Threshold localized centroiding.
  - 2D Gaussian log-parabolic sub-pixel peak estimator.
  - Hybrid Multi-Stage engine (CoM + Sub-pixel refinement).
- **Optical Signal Metrics**: PNR, SNR (dB), integrated flux, and composite confidence score $c \in [0.0, 1.0]$.
- **Boresight Bearing Estimation**: Apparent azimuth ($\hat{\theta}_{\text{az}}$) and elevation ($\hat{\theta}_{\text{el}}$) bearings.
- **FastAPI Endpoints**: `/detection/initialize`, `/detection/reset`, `/detection/config`, `/detection/detect`, `/detection/result`, `/detection/status`, `/detection/telemetry`, `/detection/annotated-image`.
- **Frontend HUD Viewfinder**: Live optical viewfinder, animated cyan/emerald target reticles, ground-truth error vector, algorithm selector, parameter sliders, and real-time telemetry diagnostics.

---

## 4. Directory Structure

```
FSOC_Tracking_Sim/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application with CORS & OpenAPI
│   │   ├── core/
│   │   │   └── state.py         # Thread-safe simulator state manager
│   │   ├── scenario/
│   │   │   ├── models.py        # Pydantic schema models
│   │   │   ├── presets.py       # 7 Scenario presets
│   │   │   ├── validator.py     # Physical bounds validator
│   │   │   ├── service.py       # Scenario business service
│   │   │   └── factory.py       # Module initialization factory
│   │   ├── world/
│   │   │   ├── models.py        # 3D Vectors, PlatformState, RelativeGeometry
│   │   │   ├── motion.py        # MotionEngine (Static, Drift, Sway, Orbit)
│   │   │   ├── platform.py      # Platform model
│   │   │   ├── world.py         # Virtual World environment class
│   │   │   └── service.py       # World service layer
│   │   ├── camera/              # Virtual Camera & Pinhole optics
│   │   ├── disturbance/         # Disturbance & Noise simulation
│   │   ├── detection/           # Beacon Detection & Sub-Pixel Centroiding
│   │   └── api/                 # REST API endpoints for all modules
│   ├── tests/                   # 126 unit & integration test cases
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── scenario/        # Module 1 UI components
│   │   │   ├── world/           # Module 2 UI components
│   │   │   ├── camera/          # Module 3 UI components
│   │   │   ├── disturbance/     # Module 4 UI components
│   │   │   └── detection/       # Module 5 UI components
│   │   ├── services/            # API client services
│   │   ├── styles/              # Aerospace HUD styling
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── simulation/
│   ├── world/
│   ├── camera/
│   ├── disturbance/
│   └── detection/
│
├── docs/                        # Complete technical specifications (Modules 1-5)
├── README.md
└── run.md
```

---

## 5. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Uvicorn, NumPy, Pillow, Pytest, HTTPX
- **Frontend**: React 18, Vite, Vanilla Modern CSS (Dark HUD Theme), Lucide Icons

---

## 6. How to Run

### Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation available at: `http://127.0.0.1:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Dashboard available at: `http://localhost:5173/`

### Running Backend Tests
```bash
python -m pytest backend/tests -v
```
*(126 total passing unit & integration tests across Modules 1–5 with 100% pass rate).*
