# Module 10 — Tracking FSM & Re-acquisition

**Team PHARO — SIH26169**

## Purpose
Governs coarse alignment supervisory states, scan patterns, acquisition logic, lock verification, and intelligent re-acquisition after signal interruption.

## Planned States & Transitions
- `IDLE`: Simulator initialized, waiting for START command.
- `SPIRAL_SEARCH`: Expanding Archimedean spiral scanning pattern when beacon is outside camera FOV.
- `ACQUISITION`: Initial beacon spot detection verification and centroid lock.
- `COARSE_TRACKING`: Closed-loop PID & Kalman tracking keeping spot within central threshold ($\le 5$ pixels).
- `RE_ACQUISITION`: Coasting on Kalman momentum during dropouts, transitioning to local raster/box search if lock is not restored within timeout.
