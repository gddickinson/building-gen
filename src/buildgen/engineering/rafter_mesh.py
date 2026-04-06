"""Create proper angled rafter meshes for 3D export.

A rafter is a long thin timber beam running at the roof pitch angle
from the wall plate (eaves) up to the ridge board. It CANNOT be
represented as an axis-aligned box — it must be a rotated mesh.

This module creates trimesh geometry for individual rafters with
correct pitch angle, birdsmouth cut at the eaves, and connection
to the ridge at the top.
"""

from __future__ import annotations

import math

import numpy as np
import trimesh


def create_rafter_mesh(
    eaves_x: float, eaves_y: float, eaves_z: float,
    ridge_x: float, ridge_y: float,
    section_width: float = 0.047,
    section_depth: float = 0.150,
    color: list[int] | None = None,
) -> trimesh.Trimesh:
    """Create a single rafter as a properly angled 3D mesh.

    The rafter runs from (eaves_x, eaves_y, eaves_z) to
    (ridge_x, ridge_y, eaves_z) — same Z, angled in XY plane.

    Args:
        eaves_x, eaves_y: Position of rafter foot (on wall plate)
        eaves_z: Z position (along building depth)
        ridge_x, ridge_y: Position of rafter head (at ridge)
        section_width: Timber width (across the slope, typically 47mm)
        section_depth: Timber depth (along the slope, typically 150mm)
    """
    if color is None:
        color = [180, 150, 100, 255]

    # Rafter direction vector
    dx = ridge_x - eaves_x
    dy = ridge_y - eaves_y
    rafter_length = math.hypot(dx, dy)

    if rafter_length < 0.1:
        return trimesh.Trimesh()

    # Create a box at the origin aligned along X axis
    # then rotate it to the correct pitch angle
    box = trimesh.creation.box(
        extents=[rafter_length, section_depth, section_width],
    )

    # Rotation angle around Z axis (pitch)
    pitch_angle = math.atan2(dy, dx)

    # Rotation matrix around Z axis
    cos_a = math.cos(pitch_angle)
    sin_a = math.sin(pitch_angle)
    rot = np.array([
        [cos_a, -sin_a, 0, 0],
        [sin_a,  cos_a, 0, 0],
        [0,      0,     1, 0],
        [0,      0,     0, 1],
    ], dtype=np.float64)

    box.apply_transform(rot)

    # Translate to midpoint of the rafter
    mid_x = (eaves_x + ridge_x) / 2
    mid_y = (eaves_y + ridge_y) / 2
    box.apply_translation([mid_x, mid_y, eaves_z])

    box.visual.face_colors = color
    return box


def create_hip_rafter_mesh(
    corner_x: float, corner_y: float, corner_z: float,
    ridge_x: float, ridge_y: float, ridge_z: float,
    section_width: float = 0.063,
    section_depth: float = 0.200,
    color: list[int] | None = None,
) -> trimesh.Trimesh:
    """Create a hip rafter running diagonally from corner to ridge.

    Hip rafters run at an angle in BOTH plan (XZ) and elevation (Y),
    so they need full 3D rotation.
    """
    if color is None:
        color = [170, 140, 90, 255]

    dx = ridge_x - corner_x
    dy = ridge_y - corner_y
    dz = ridge_z - corner_z

    rafter_length = math.sqrt(dx**2 + dy**2 + dz**2)
    if rafter_length < 0.1:
        return trimesh.Trimesh()

    # Create box along X axis
    box = trimesh.creation.box(
        extents=[rafter_length, section_depth, section_width],
    )

    # We need to rotate the box to align with the direction vector (dx, dy, dz)
    # Default direction is along X axis (1, 0, 0)
    # Use trimesh's align_vectors to find the rotation
    source = np.array([1, 0, 0], dtype=np.float64)
    target = np.array([dx, dy, dz], dtype=np.float64)
    target = target / np.linalg.norm(target)

    # Build rotation matrix using Rodrigues' formula
    rot_matrix = _rotation_matrix_between(source, target)
    transform = np.eye(4)
    transform[:3, :3] = rot_matrix

    box.apply_transform(transform)

    # Translate to midpoint
    mid = np.array([
        (corner_x + ridge_x) / 2,
        (corner_y + ridge_y) / 2,
        (corner_z + ridge_z) / 2,
    ])
    box.apply_translation(mid)

    box.visual.face_colors = color
    return box


def create_all_roof_meshes(
    width: float,
    depth: float,
    eaves_y: float,
    ridge_height: float,
    pitch_deg: float,
    rafter_spacing: float = 0.400,
    rafter_section: tuple[float, float] = (0.047, 0.150),
    roof_type: str = "hip",
) -> list[trimesh.Trimesh]:
    """Create all rafter meshes for a complete roof.

    Returns list of trimesh objects for each rafter, ready to merge
    into the scene.
    """
    meshes = []

    half_span = width / 2
    ridge_y = eaves_y + ridge_height
    rw, rd = rafter_section

    num_rafters = int(depth / rafter_spacing) + 1

    if roof_type == "hip":
        inset = half_span  # Hip inset from each end
        ridge_start_z = inset
        ridge_end_z = depth - inset
    else:
        ridge_start_z = 0
        ridge_end_z = depth

    # Common rafters — left slope
    for ri in range(num_rafters):
        rz = ri * rafter_spacing
        if rz > depth:
            break

        # Skip rafters in the hip zone (replaced by jack rafters)
        if roof_type == "hip" and (rz < ridge_start_z or rz > ridge_end_z):
            continue

        # Left rafter: eaves at x=0, ridge at x=width/2
        mesh = create_rafter_mesh(
            0, eaves_y, rz,
            half_span, ridge_y,
            rw, rd,
        )
        meshes.append(mesh)

        # Right rafter: eaves at x=width, ridge at x=width/2
        mesh = create_rafter_mesh(
            width, eaves_y, rz,
            half_span, ridge_y,
            rw, rd,
        )
        meshes.append(mesh)

    # Hip rafters (4 diagonals from corners to ridge ends)
    if roof_type == "hip":
        hip_corners = [
            (0, eaves_y, 0, half_span, ridge_y, ridge_start_z),
            (width, eaves_y, 0, half_span, ridge_y, ridge_start_z),
            (0, eaves_y, depth, half_span, ridge_y, ridge_end_z),
            (width, eaves_y, depth, half_span, ridge_y, ridge_end_z),
        ]
        for cx, cy, cz, rx, ry, rz in hip_corners:
            mesh = create_hip_rafter_mesh(
                cx, cy, cz, rx, ry, rz,
                0.063, 0.200,
            )
            meshes.append(mesh)

        # Jack rafters in the hip zones (shorter rafters from eaves to hip)
        for end_z, ridge_z_end in [(0, ridge_start_z), (depth, ridge_end_z)]:
            num_jacks = max(2, int(inset / rafter_spacing))
            for ji in range(1, num_jacks):
                t = ji / num_jacks
                jack_z = end_z + t * (ridge_z_end - end_z)
                jack_ridge_y = eaves_y + t * ridge_height

                # Left jack
                mesh = create_rafter_mesh(
                    0, eaves_y, jack_z,
                    t * half_span, jack_ridge_y,
                    rw, rd,
                )
                meshes.append(mesh)

                # Right jack
                mesh = create_rafter_mesh(
                    width, eaves_y, jack_z,
                    width - t * half_span, jack_ridge_y,
                    rw, rd,
                )
                meshes.append(mesh)

    # ── RIDGE BOARD (runs along Z only between hip endpoints) ──
    ridge_len = max(0.1, ridge_end_z - ridge_start_z)
    ridge_board = trimesh.creation.box(
        extents=[0.022, 0.170, ridge_len],
    )
    ridge_board.apply_translation([
        half_span, ridge_y, (ridge_start_z + ridge_end_z) / 2,
    ])
    ridge_board.visual.face_colors = [180, 150, 100, 255]
    meshes.append(ridge_board)

    # ── PURLINS (mid-span support, length follows hip line) ──
    # At height fraction t, purlin runs from z=t*inset to z=depth-t*inset
    hip_inset_z = half_span if roof_type == "hip" else 0
    rafter_length_calc = half_span / math.cos(math.radians(pitch_deg))
    if rafter_length_calc > 2.5:
        purlin_count = max(1, int(rafter_length_calc / 2.0))
        for pi in range(1, purlin_count + 1):
            t = pi / (purlin_count + 1)
            purlin_y = eaves_y + t * ridge_height

            z_start = t * hip_inset_z
            z_end = depth - t * hip_inset_z
            purlin_span = max(0.5, z_end - z_start)
            purlin_cz = (z_start + z_end) / 2

            for side_x in [t * half_span, width - t * half_span]:
                purlin = trimesh.creation.box(
                    extents=[0.047, 0.175, purlin_span],
                )
                purlin.apply_translation([side_x, purlin_y, purlin_cz])
                purlin.visual.face_colors = [190, 160, 110, 255]
                meshes.append(purlin)

    # ── CEILING JOISTS / TIE BEAMS (horizontal, tying rafter feet) ──
    tie_spacing = rafter_spacing * 3  # Every 3rd rafter bay
    num_ties = int(depth / tie_spacing) + 1
    for ti in range(num_ties):
        tz = ti * tie_spacing
        if tz > depth:
            break
        tie = trimesh.creation.box(
            extents=[width, 0.100, 0.047],
        )
        tie.apply_translation([half_span, eaves_y + 0.050, tz])
        tie.visual.face_colors = [200, 170, 120, 255]
        meshes.append(tie)

    # ── WALL PLATES (on top of walls, rafters sit on these) ──
    for wz in [0, depth]:
        wp = trimesh.creation.box(
            extents=[width, 0.075, 0.100],
        )
        wp.apply_translation([half_span, eaves_y - 0.038, wz])
        wp.visual.face_colors = [200, 170, 120, 255]
        meshes.append(wp)

    for wx in [0, width]:
        wp = trimesh.creation.box(
            extents=[0.100, 0.075, depth],
        )
        wp.apply_translation([wx, eaves_y - 0.038, depth / 2])
        wp.visual.face_colors = [200, 170, 120, 255]
        meshes.append(wp)

    return meshes


def _rotation_matrix_between(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute rotation matrix to rotate vector a to align with vector b."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)

    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)

    if s < 1e-10:
        if c > 0:
            return np.eye(3)
        else:
            # 180 degree rotation — pick arbitrary perpendicular axis
            perp = np.array([1, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1, 0])
            axis = np.cross(a, perp)
            axis = axis / np.linalg.norm(axis)
            K = np.array([
                [0, -axis[2], axis[1]],
                [axis[2], 0, -axis[0]],
                [-axis[1], axis[0], 0],
            ])
            return np.eye(3) + 2 * K @ K

    # Skew-symmetric matrix
    K = np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0],
    ])

    return np.eye(3) + K + K @ K * (1 - c) / (s * s)
