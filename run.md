# Quickstart Guide — Running FSOC Coarse Alignment Simulator

**Team PHARO — SIH26169**

Follow these steps to run both the FastAPI backend and React frontend locally.

---

## 1. Prerequisites
- **Python 3.11+** installed
- **Node.js 18+ & npm** installed

---

## 2. Launching Backend

Open a PowerShell terminal and run:

```powershell
cd D:\Projects\FSOC_Tracking_Sim\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`
- World status: `http://127.0.0.1:8000/world/status`

---

## 3. Launching Frontend

Open a second PowerShell terminal and run:

```powershell
cd D:\Projects\FSOC_Tracking_Sim\frontend
npm install
npm run dev
```

- Web Dashboard URL: `http://localhost:5173`

---

## 4. Running Automated Tests

```powershell
cd D:\Projects\FSOC_Tracking_Sim\backend
python -m pytest tests/ -v
```

All 139 unit and integration tests (Scenario Configuration, Virtual World Simulation, Virtual Camera & Optics, Disturbance & Noise Simulation, Beacon Detection & Centroiding) will execute with a 100% pass rate.

---

## 5. Usage Workflow

### Module 1: Scenario Configuration
1. Open `http://localhost:5173` in your browser.
2. Select **Module 1: Scenario Configuration** tab.
3. Select a scenario preset (e.g. *Easy Acquisition*, *High Vibration*, *Full Stress Test*).
4. Customize parameters and click **[ APPLY SCENARIO ]**.

### Module 2: Virtual World & Platform Simulation
1. Switch to **Module 2: Virtual World & Platforms** tab.
2. Click **[ STEP (+1 FRAME) ]** to advance simulation time by $dt$.
3. Or click **[ PLAY SIMULATION ]** to run continuous deterministic kinematic updates.
4. Observe real-time position/velocity changes for Camera and Beacon platforms.
5. Inspect the **Ground-Truth Relative Geometry** HUD (Range in meters, Azimuth in degrees, Elevation in degrees).
6. View the interactive **2D Tactical Spatial Radar Preview** in Top-Down $(X$-$Z)$ and Side-Elevation $(Z$-$Y)$ modes.
7. Click **[ RESET (T=0) ]** to return the simulation clock to the start.

### Module 3: Virtual Camera & Rendering
1. Switch to **Module 3: Virtual Camera & Rendering** tab.
2. View the **Synthetic Optical Focal Plane** with live SVG crosshairs, reticle rings, and target tracking marker.
3. Use the **Gimbal Pan-Tilt Manual Steering** sliders or fine nudge buttons ($\pm 0.2^\circ, \pm 1^\circ, \pm 5^\circ$) to adjust receiver boresight orientation.
4. Click **[ AUTO-CENTER ]** to automatically align boresight with the beacon's true line of sight.
5. Inspect the **Optical Intrinsics (Matrix $K$)** and **Optical Telemetry** (tracking error offsets $\Delta u, \Delta v$, apparent angles $\theta_{\text{az}}, \theta_{\text{el}}$).

### Module 4: Disturbance & Noise Simulation
1. Switch to **Module 4: Disturbance & Noise** tab.
2. Inspect the **Side-by-Side Viewfinder** comparing the `Clean Synthetic Camera Frame` (Ground Truth) vs `Disturbed Sensor Observation` (Detector Input).
3. Toggle and adjust the severity level (**OFF**, **LOW**, **MEDIUM**, **HIGH**) or customize fine-grained parameters:
   - **Platform Jitter**: Adjust vibration magnitude ($0.0 - 15.0\text{ px}$).
   - **Optical Blur**: Adjust PSF blur strength / sigma ($0.0 - 10.0$).
   - **Sensor Noise**: Adjust additive Gaussian noise magnitude ($0.0 - 0.5$).
   - **Beacon Dropout**: Adjust dropout probability ($0 - 100\%$) and burst duration ($0.0 - 5.0\text{ s}$).
4. Observe live telemetry diagnostics including noise standard deviation $\sigma$, jitter displacement vector $(dx, dy)$, and deep fade occlusion alerts.

### Module 5: Beacon Detection & Centroiding
1. Switch to **Module 5: Beacon Detection & Centroiding** tab.
2. Inspect the live **Optical Acquisition Viewfinder** with animated cyan/emerald target tracking reticles, spot bounding boxes, and yellow ground-truth error vectors.
3. Test different centroiding algorithms in real time:
   - **Hybrid Multi-Stage**: Combined windowed CoM with sub-pixel Gaussian peak refinement (recommended).
   - **Intensity CoM**: Background-subtracted Center of Mass.
   - **Adaptive Threshold**: Dynamic statistical $k$-$\sigma$ thresholding.
   - **2D Gaussian Fit**: Analytical log-parabolic sub-pixel peak estimator.
4. Tune detection parameters on the fly:
   - **$k$-$\sigma$ Threshold Multiplier**: Dynamic noise floor sensitivity.
   - **Minimum PNR**: Minimum peak-to-noise ratio to confirm beacon acquisition.
   - **Localized ROI Radius**: Size of cropped spot evaluation window.
   - **Sub-Pixel Gaussian Refinement**: Toggle sub-pixel peak fitting.
5. Monitor real-time telemetry metrics:
   - Estimated coordinates $(\hat{u}, \hat{v})$ vs Ground Truth $(u_{\text{true}}, v_{\text{true}})$.
   - Radial localization error $\Delta r = \sqrt{\Delta u^2 + \Delta v^2}$ in pixels.
   - Estimated line-of-sight boresight bearings $(\hat{\theta}_{\text{az}}, \hat{\theta}_{\text{el}})$.
   - Optical signal quality: Peak intensity, noise floor $\mu \pm \sigma$, PNR, SNR (dB), and confidence $\%$.
   - Cumulative detection success rate $\%$ and mean radial error.
