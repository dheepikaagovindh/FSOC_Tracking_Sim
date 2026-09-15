# Module 3 — Virtual Camera & Rendering

**Team PHARO — SIH26169**

## Purpose
Models the receiver terminal's optical sensor geometry and projects the 3D optical beacon onto a 2D synthetic focal plane pixel array.

## Planned Capabilities
- **Pinhole & Lens Optics**: Pin-hole projection model with horizontal/vertical focal lengths derived from FOV and pixel dimensions.
- **Spot Rendering**: 2D Gaussian intensity profile modeling the focused laser beacon spot.
- **Sensor Geometry**: Configurable resolution ($W \times H$), pixel pitch, and clipping at FOV boundaries.
- **Gimbal Frame Transformation**: Transforms world LOS vector into camera sensor coordinate frame based on active gimbal pan/tilt orientation.

## Inputs from ScenarioConfig
- `ScenarioConfig.camera` (`width`, `height`, `horizontal_fov_deg`, `vertical_fov_deg`, `initial_pan_deg`, `initial_tilt_deg`)
- `ScenarioConfig.beacon` (`brightness`, `size`)
