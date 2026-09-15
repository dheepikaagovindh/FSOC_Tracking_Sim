# Module 5 — Beacon Detection

**Team PHARO — SIH26169**

## Purpose
Performs optical image processing on incoming synthetic camera frames to detect and localize the optical beacon spot.

## Planned Capabilities
- **Classical Centroiding**: Center of Mass (CoM) intensity weighted centroid calculation for sub-pixel accuracy.
- **Adaptive Thresholding**: Otsu / background adaptive noise floor subtraction.
- **AI-Based Bounding Box Detection**: Lightweight CNN / YOLO detector for robust spot identification against clutter and solar background glare.
- **Signal Quality Metrics**: Computes Peak-to-Noise Ratio (PNR) and detection confidence scores.
