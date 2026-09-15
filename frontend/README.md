# FSOC Coarse Alignment Simulator — Frontend Dashboard

**Team PHARO — SIH26169**

This dashboard provides an aerospace mission-control user interface to configure, validate, and parameterize FSOC simulation scenarios before triggering the tracking loop.

## Features
- **Aerospace Cyber Dark HUD Theme**: Glassmorphic styling, crisp telemetry fonts, scanline grid accents.
- **7 Scenario Presets**: Instant loading of progressive challenge profiles (Easy Acquisition to Full Stress Test).
- **Interactive Controls**: Range sliders, numeric inputs, toggle switches, and segmented severity buttons.
- **Live Summary HUD**: Real-time calculated telemetry summary and instant boundary validation checks.
- **Simulation Verification**: Full handshake with FastAPI backend (`POST /scenario`, `POST /scenario/start`).

## Development Setup

```bash
# Install dependencies
npm install

# Start Vite Development Server
npm run dev
```

The frontend server runs on `http://localhost:5173` and proxies API requests to `http://127.0.0.1:8000`.
