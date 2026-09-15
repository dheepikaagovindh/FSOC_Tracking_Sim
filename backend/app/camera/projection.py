"""
Optical Projection and Coordinate Transformation Mathematics.
Team PHARO — SIH26169

Provides pure mathematical transformations for:
- Camera intrinsic parameters derivation from FOV
- World-to-Camera 3D coordinate rotation and translation
- Pinhole camera projection to 2D focal plane
- Apparent boresight azimuth and elevation calculation
- FOV visibility and boundary classification
"""

from __future__ import annotations
import math
from typing import Tuple

from ..world.models import Vector3D
from .models import (
    CameraIntrinsics,
    CameraPose,
    ProjectedPoint,
    CameraAngles,
    CameraVisibility,
    VisibilityReason,
)


def calculate_intrinsics(
    width: int,
    height: int,
    hfov_deg: float,
    vfov_deg: float,
) -> CameraIntrinsics:
    """
    Compute pinhole optical intrinsics from sensor dimensions and field-of-view angles.
    
    Equations:
      fx = width / (2 * tan(hfov_rad / 2))
      fy = height / (2 * tan(vfov_rad / 2))
      cx = width / 2.0
      cy = height / 2.0
    """
    if width <= 0 or height <= 0:
        raise ValueError(f"Image dimensions must be positive integers, got {width}x{height}")
    if not (0.0 < hfov_deg < 180.0):
        raise ValueError(f"Horizontal FOV must be in (0, 180) degrees, got {hfov_deg}")
    if not (0.0 < vfov_deg < 180.0):
        raise ValueError(f"Vertical FOV must be in (0, 180) degrees, got {vfov_deg}")

    hfov_rad = math.radians(hfov_deg)
    vfov_rad = math.radians(vfov_deg)

    fx = float(width) / (2.0 * math.tan(hfov_rad / 2.0))
    fy = float(height) / (2.0 * math.tan(vfov_rad / 2.0))
    cx = float(width) / 2.0
    cy = float(height) / 2.0

    return CameraIntrinsics(
        fx=fx,
        fy=fy,
        cx=cx,
        cy=cy,
        width=width,
        height=height,
        hfov_deg=hfov_deg,
        vfov_deg=vfov_deg,
    )


def world_to_camera_frame(
    r_world: Vector3D,
    pan_deg: float,
    tilt_deg: float,
) -> Vector3D:
    """
    Transform world-relative displacement vector into camera reference frame.
    
    Coordinate Frame Conventions:
      World Frame:
        +X: Horizontal (right)
        +Y: Vertical (up)
        +Z: Forward (depth)
      Camera Frame:
        +X_c: Right
        +Y_c: Up
        +Z_c: Forward (optical axis / boresight)
      
      Gimbal Orientation:
        pan_deg:  Rotation about world +Y axis (yaw).
                  Positive pan turns camera to the right.
        tilt_deg: Rotation about camera lateral +X axis (pitch).
                  Positive tilt pitches camera upward.
                  
      Transformation Matrix:
        R = R_X(tilt) * R_Y(pan)
        r_camera = R * r_world
    """
    pan_rad = math.radians(pan_deg)
    tilt_rad = math.radians(tilt_deg)

    cos_p = math.cos(pan_rad)
    sin_p = math.sin(pan_rad)
    cos_t = math.cos(tilt_rad)
    sin_t = math.sin(tilt_rad)

    dx = r_world.x
    dy = r_world.y
    dz = r_world.z

    # Step 1: Pan rotation around Y axis
    # X1 = cos(p)*dx - sin(p)*dz
    # Y1 = dy
    # Z1 = sin(p)*dx + cos(p)*dz
    x1 = cos_p * dx - sin_p * dz
    y1 = dy
    z1 = sin_p * dx + cos_p * dz

    # Step 2: Tilt rotation around X axis
    # X_c = X1
    # Y_c = cos(t)*Y1 - sin(t)*Z1
    # Z_c = sin(t)*Y1 + cos(t)*Z1
    x_c = x1
    y_c = cos_t * y1 - sin_t * z1
    z_c = sin_t * y1 + cos_t * z1

    return Vector3D(x=x_c, y=y_c, z=z_c)


def project_to_pixel(
    point_cam: Vector3D,
    intrinsics: CameraIntrinsics,
) -> ProjectedPoint:
    """
    Project 3D camera-frame coordinates to 2D continuous pixel coordinates.
    
    Equations:
      u = fx * (X_cam / Z_cam) + cx
      v = cy - fy * (Y_cam / Z_cam)
      
    Note: v uses minus sign because pixel coordinate v increases downward,
          while camera Y_cam is defined upward.
    """
    # Guard against division by zero for points on or behind focal center plane
    z = point_cam.z
    if abs(z) < 1e-9:
        z_safe = 1e-9 if z >= 0 else -1e-9
    else:
        z_safe = z

    norm_x = point_cam.x / z_safe
    norm_y = point_cam.y / z_safe

    u = intrinsics.fx * norm_x + intrinsics.cx
    v = intrinsics.cy - intrinsics.fy * norm_y

    return ProjectedPoint(
        u=u,
        v=v,
        normalized_x=norm_x,
        normalized_y=norm_y,
    )


def calculate_camera_angles(point_cam: Vector3D) -> CameraAngles:
    """
    Calculate apparent azimuth and elevation angles relative to camera optical boresight.
    
    Convention:
      Azimuth:   atan2(X_cam, Z_cam) in degrees (positive = right of boresight)
      Elevation: atan2(Y_cam, sqrt(X_cam^2 + Z_cam^2)) in degrees (positive = above boresight)
    """
    x = point_cam.x
    y = point_cam.y
    z = point_cam.z

    r_horiz = math.sqrt(x * x + z * z)

    if r_horiz == 0.0 and y == 0.0:
        az_deg = 0.0
        el_deg = 0.0
    else:
        az_deg = math.degrees(math.atan2(x, z))
        el_deg = math.degrees(math.atan2(y, r_horiz))

    return CameraAngles(
        azimuth_deg=az_deg,
        elevation_deg=el_deg,
    )


def check_visibility(
    point_cam: Vector3D,
    proj: ProjectedPoint,
    width: int,
    height: int,
) -> CameraVisibility:
    """
    Determine if beacon is physically in front of camera and inside sensor bounds.
    
    Criteria:
      in_front_of_camera:    Z_cam > 0
      inside_horizontal_fov: 0.0 <= u < width (and in_front_of_camera)
      inside_vertical_fov:   0.0 <= v < height (and in_front_of_camera)
    """
    in_front = point_cam.z > 0.0
    in_h_fov = (0.0 <= proj.u < float(width)) and in_front
    in_v_fov = (0.0 <= proj.v < float(height)) and in_front
    is_visible = in_front and in_h_fov and in_v_fov

    if not in_front:
        reason: VisibilityReason = "BEHIND_CAMERA"
    elif not is_visible:
        reason = "OUT_OF_FOV"
    else:
        reason = "VISIBLE"

    return CameraVisibility(
        visible=is_visible,
        in_front_of_camera=in_front,
        inside_horizontal_fov=in_h_fov,
        inside_vertical_fov=in_v_fov,
        reason=reason,
    )
