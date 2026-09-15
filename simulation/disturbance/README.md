# Module 4 — Disturbance Simulation

**Team PHARO — SIH26169**

## Purpose
Simulates realistic aerospace flight disturbances, atmospheric turbulence, sensor noise, and optical path interruptions.

## Planned Capabilities
- **Platform Micro-Vibration**: Bandpass filtered random jitter modeling UAV drone rotors, aircraft engine vibrations, and base excitation.
- **Sensor Noise**: Gaussian white noise and background thermal read noise on sensor pixels.
- **Atmospheric & Motion Blur**: Point Spread Function (PSF) convolution and velocity-induced optical smear.
- **Deep Fades / Dropouts**: Markov-chain based atmospheric scintillation and cloud obscuration causing transient beacon signal loss.

## Inputs from ScenarioConfig
- `ScenarioConfig.disturbances` (`severity`, `vibration_*`, `noise_*`, `blur_*`, `dropout_*`)
