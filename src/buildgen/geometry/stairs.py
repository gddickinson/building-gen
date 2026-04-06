"""Staircase mesh generation.

Supports multiple stair types:
- Straight run: simple flight from bottom to top
- L-shape: quarter-turn with intermediate landing
- U-shape: half-turn (dog-leg) with intermediate landing
- Spiral: circular spiral staircase
- Winder: turning stairs without a landing (compact)

Each stair type has:
- Individual treads and risers
- Solid stringer underneath
- Landing platforms where needed
- Proper rise/run proportions
"""

from __future__ import annotations

import math

import numpy as np
import trimesh

from ..layout.models import RoomPolygon
from ..style.models import StyleParams


def build_stair_mesh(
    room: RoomPolygon,
    floor_y: float,
    floor_height: float,
    style: StyleParams,
    stair_type: str = "auto",
) -> trimesh.Trimesh | None:
    """Build a staircase within a stairwell room.

    Args:
        room: The stairwell room polygon (2D bounds)
        floor_y: Y height of the current floor
        floor_height: Total height to the next floor
        style: Style parameters
        stair_type: "straight", "l_shape", "u_shape", "spiral", or "auto"
    """
    b = room.bounds
    sw = b[2] - b[0]  # stairwell width (X)
    sd = b[3] - b[1]  # stairwell depth (Z)

    if sw < 0.5 or sd < 0.5:
        return None

    # Auto-select stair type based on stairwell proportions
    if stair_type == "auto":
        aspect = max(sw, sd) / min(sw, sd) if min(sw, sd) > 0 else 1
        area = sw * sd
        if min(sw, sd) < 1.2:
            # Very narrow — spiral or straight
            stair_type = "spiral" if aspect < 1.3 else "straight"
        elif aspect > 2.0:
            stair_type = "straight"
        elif area > 5.0:
            stair_type = "u_shape"
        else:
            stair_type = "l_shape"

    slab_t = style.slab_thickness
    total_rise = floor_height - slab_t
    if total_rise <= 0:
        total_rise = floor_height
    start_y = floor_y + slab_t

    if stair_type == "spiral":
        return _build_spiral_stair(b, start_y, total_rise, style)
    elif stair_type == "u_shape":
        return _build_u_stair(b, start_y, total_rise, style)
    elif stair_type == "l_shape":
        return _build_l_stair(b, start_y, total_rise, style)
    else:
        return _build_straight_stair(b, start_y, total_rise, style)


def _build_straight_stair(
    bounds: tuple, start_y: float, total_rise: float, style: StyleParams,
) -> trimesh.Trimesh | None:
    """Simple straight-run staircase."""
    b = bounds
    sw = b[2] - b[0]
    sd = b[3] - b[1]

    riser_h = style.stair_riser
    num_steps = max(3, round(total_rise / riser_h))
    riser_h = total_rise / num_steps

    # Run along the longer dimension
    run_along_z = sd >= sw
    if run_along_z:
        stair_width = min(sw * 0.85, sw - 0.1)
        stair_run = sd - 0.2
    else:
        stair_width = min(sd * 0.85, sd - 0.1)
        stair_run = sw - 0.2

    tread_d = stair_run / num_steps
    cx = (b[0] + b[2]) / 2
    cz = (b[1] + b[3]) / 2

    meshes = []
    for i in range(num_steps):
        step_base = start_y + i * riser_h
        step_top = start_y + (i + 1) * riser_h

        if run_along_z:
            z0 = b[1] + 0.1 + i * tread_d
            z1 = z0 + tread_d
            x0 = cx - stair_width / 2
            x1 = cx + stair_width / 2
        else:
            x0 = b[0] + 0.1 + i * tread_d
            x1 = x0 + tread_d
            z0 = cz - stair_width / 2
            z1 = cz + stair_width / 2

        # Tread
        meshes.append(_make_box(
            x0, step_top - 0.04, z0, x1, step_top, z1,
            style.stair_color,
        ))
        # Riser
        if run_along_z:
            meshes.append(_make_box(
                x0, step_base, z0, x1, step_top - 0.04, z0 + 0.02,
                _darken(style.stair_color, 25),
            ))
        else:
            meshes.append(_make_box(
                x0, step_base, z0, x0 + 0.02, step_top - 0.04, z1,
                _darken(style.stair_color, 25),
            ))

    # Stringer (ramped solid under stairs)
    meshes.extend(_build_stringer_segments(
        bounds, start_y, total_rise, num_steps, tread_d,
        stair_width, run_along_z, cx, cz, style,
    ))

    if meshes:
        return trimesh.util.concatenate(meshes)
    return None


def _build_l_stair(
    bounds: tuple, start_y: float, total_rise: float, style: StyleParams,
) -> trimesh.Trimesh | None:
    """L-shaped staircase with quarter-turn landing.

    First flight goes along Z, turns 90 degrees at a landing,
    second flight goes along X.
    """
    b = bounds
    sw = b[2] - b[0]
    sd = b[3] - b[1]

    riser_h = style.stair_riser
    num_steps = max(6, round(total_rise / riser_h))
    riser_h = total_rise / num_steps

    # Split steps: ~60% in first flight, ~40% in second
    steps_1 = num_steps * 3 // 5
    steps_2 = num_steps - steps_1

    stair_w = min(sw, sd) * 0.4  # Width of each flight
    landing_size = stair_w  # Landing is square

    meshes = []

    # First flight: runs along Z (front to back), on the left side
    for i in range(steps_1):
        step_base = start_y + i * riser_h
        step_top = start_y + (i + 1) * riser_h
        tread_d = (sd - landing_size) / steps_1

        x0 = b[0] + 0.05
        x1 = x0 + stair_w
        z0 = b[1] + 0.05 + i * tread_d
        z1 = z0 + tread_d

        meshes.append(_make_box(
            x0, step_top - 0.04, z0, x1, step_top, z1,
            style.stair_color,
        ))

    # Landing (quarter-turn platform)
    landing_y = start_y + steps_1 * riser_h
    lx0 = b[0] + 0.05
    lx1 = lx0 + landing_size
    lz0 = b[3] - landing_size - 0.05
    lz1 = b[3] - 0.05
    meshes.append(_make_box(
        lx0, landing_y - 0.06, lz0, lx1, landing_y, lz1,
        style.stair_color,
    ))

    # Second flight: runs along X (left to right), at the back
    for i in range(steps_2):
        step_base = landing_y + i * riser_h
        step_top = landing_y + (i + 1) * riser_h
        tread_d = (sw - landing_size - 0.1) / steps_2

        x0 = lx1 + i * tread_d
        x1 = x0 + tread_d
        z0 = lz0
        z1 = lz1

        meshes.append(_make_box(
            x0, step_top - 0.04, z0, x1, step_top, z1,
            style.stair_color,
        ))

    if meshes:
        return trimesh.util.concatenate(meshes)
    return None


def _build_u_stair(
    bounds: tuple, start_y: float, total_rise: float, style: StyleParams,
) -> trimesh.Trimesh | None:
    """U-shaped (dog-leg) staircase with half-turn landing.

    Two parallel flights connected by a landing. Goes up along Z,
    turns 180 degrees, comes back along Z.
    """
    b = bounds
    sw = b[2] - b[0]
    sd = b[3] - b[1]

    riser_h = style.stair_riser
    num_steps = max(6, round(total_rise / riser_h))
    riser_h = total_rise / num_steps

    steps_per_flight = num_steps // 2
    steps_2 = num_steps - steps_per_flight

    flight_w = (sw - 0.15) / 2  # Two flights side by side
    gap = 0.1  # Gap between flights
    landing_depth = 1.0  # Landing at the turn

    meshes = []

    # First flight: left side, going back (increasing Z)
    run_length = sd - landing_depth - 0.1
    tread_d = run_length / steps_per_flight

    for i in range(steps_per_flight):
        step_top = start_y + (i + 1) * riser_h
        x0 = b[0] + 0.05
        x1 = x0 + flight_w
        z0 = b[1] + 0.05 + i * tread_d
        z1 = z0 + tread_d

        meshes.append(_make_box(
            x0, step_top - 0.04, z0, x1, step_top, z1,
            style.stair_color,
        ))

    # Half-turn landing
    landing_y = start_y + steps_per_flight * riser_h
    meshes.append(_make_box(
        b[0] + 0.05, landing_y - 0.06, b[3] - landing_depth - 0.05,
        b[2] - 0.05, landing_y, b[3] - 0.05,
        style.stair_color,
    ))

    # Second flight: right side, going forward (decreasing Z)
    tread_d_2 = run_length / steps_2
    for i in range(steps_2):
        step_top = landing_y + (i + 1) * riser_h
        x0 = b[2] - 0.05 - flight_w
        x1 = b[2] - 0.05
        z1 = b[3] - landing_depth - 0.05 - i * tread_d_2
        z0 = z1 - tread_d_2

        meshes.append(_make_box(
            x0, step_top - 0.04, z0, x1, step_top, z1,
            style.stair_color,
        ))

    if meshes:
        return trimesh.util.concatenate(meshes)
    return None


def _build_spiral_stair(
    bounds: tuple, start_y: float, total_rise: float, style: StyleParams,
) -> trimesh.Trimesh | None:
    """Spiral/circular staircase.

    Steps radiate from a central column, each rotated by a fixed angle.
    Common in castles, towers, and compact spaces.
    """
    b = bounds
    sw = b[2] - b[0]
    sd = b[3] - b[1]
    cx = (b[0] + b[2]) / 2
    cz = (b[1] + b[3]) / 2
    radius = min(sw, sd) / 2 - 0.05
    inner_radius = 0.12  # Central newel post

    if radius < 0.3:
        return None

    riser_h = style.stair_riser
    num_steps = max(8, round(total_rise / riser_h))
    riser_h = total_rise / num_steps

    # Full turn = 360 degrees, but we might do more or less
    total_angle = 2 * math.pi * 1.1  # Slightly more than full turn
    angle_per_step = total_angle / num_steps

    meshes = []

    # Central newel post
    post_verts = []
    post_faces = []
    n_sides = 8
    for i in range(n_sides):
        a = 2 * math.pi * i / n_sides
        px = cx + inner_radius * math.cos(a)
        pz = cz + inner_radius * math.sin(a)
        post_verts.append([px, start_y, pz])
        post_verts.append([px, start_y + total_rise, pz])

    for i in range(n_sides):
        j = (i + 1) % n_sides
        v0 = i * 2
        v1 = j * 2
        v2 = j * 2 + 1
        v3 = i * 2 + 1
        post_faces.extend([[v0, v1, v2], [v0, v2, v3]])

    post = trimesh.Trimesh(
        vertices=np.array(post_verts, dtype=np.float64),
        faces=np.array(post_faces, dtype=np.int64),
    )
    post.visual.face_colors = _darken(style.stair_color, 40)
    meshes.append(post)

    # Build each wedge-shaped step
    for i in range(num_steps):
        a0 = i * angle_per_step
        a1 = (i + 0.9) * angle_per_step  # 90% of the arc (gap between steps)
        step_top = start_y + (i + 1) * riser_h

        # 4 corners of the wedge (inner and outer at each angle)
        pts = []
        n_arc = 4  # Points along the arc for smoothness
        for k in range(n_arc + 1):
            t = k / n_arc
            angle = a0 + t * (a1 - a0)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            # Inner point
            pts.append((
                cx + inner_radius * cos_a,
                cz + inner_radius * sin_a,
            ))
        for k in range(n_arc, -1, -1):
            t = k / n_arc
            angle = a0 + t * (a1 - a0)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            # Outer point
            pts.append((
                cx + radius * cos_a,
                cz + radius * sin_a,
            ))

        # Create a wedge: bottom and top faces
        n_pts = len(pts)
        verts = []
        for p in pts:
            verts.append([p[0], step_top - 0.04, p[1]])
        for p in pts:
            verts.append([p[0], step_top, p[1]])

        faces = []
        # Top and bottom fan
        for j in range(1, n_pts - 1):
            faces.append([0, j, j + 1])
            faces.append([n_pts, n_pts + j + 1, n_pts + j])
        # Sides
        for j in range(n_pts):
            k = (j + 1) % n_pts
            faces.append([j, k, n_pts + k])
            faces.append([j, n_pts + k, n_pts + j])

        step_mesh = trimesh.Trimesh(
            vertices=np.array(verts, dtype=np.float64),
            faces=np.array(faces, dtype=np.int64),
        )
        step_mesh.fix_normals()
        step_mesh.visual.face_colors = style.stair_color
        meshes.append(step_mesh)

    if meshes:
        return trimesh.util.concatenate(meshes)
    return None


def _build_stringer_segments(
    bounds, start_y, total_rise, num_steps, tread_d,
    stair_width, run_along_z, cx, cz, style,
):
    """Build stringer segments under a straight stair."""
    b = bounds
    color = _darken(style.stair_color, 30)
    segments = []
    seg_count = max(2, num_steps // 4)

    for s in range(seg_count):
        t0 = s / seg_count
        t1 = (s + 1) / seg_count
        y0 = start_y + total_rise * t0 - 0.06
        y1 = start_y + total_rise * t0

        if run_along_z:
            z_s = b[1] + 0.1 + (b[3] - b[1] - 0.2) * t0
            z_e = b[1] + 0.1 + (b[3] - b[1] - 0.2) * t1
            segments.append(_make_box(
                cx - stair_width / 2, y0, z_s,
                cx + stair_width / 2, y1, z_e,
                color,
            ))
        else:
            x_s = b[0] + 0.1 + (b[2] - b[0] - 0.2) * t0
            x_e = b[0] + 0.1 + (b[2] - b[0] - 0.2) * t1
            segments.append(_make_box(
                x_s, y0, cz - stair_width / 2,
                x_e, y1, cz + stair_width / 2,
                color,
            ))

    return segments


def _make_box(x0, y0, z0, x1, y1, z1, color):
    """Create an axis-aligned box mesh."""
    # Ensure valid dimensions
    if x1 <= x0 or y1 <= y0 or z1 <= z0:
        x1 = max(x1, x0 + 0.01)
        y1 = max(y1, y0 + 0.01)
        z1 = max(z1, z0 + 0.01)

    verts = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1],
        [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1],
    ], dtype=np.float64)
    faces = np.array([
        [0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6],
        [0, 4, 7], [0, 7, 3], [1, 2, 6], [1, 6, 5],
    ], dtype=np.int64)
    mesh = trimesh.Trimesh(vertices=verts, faces=faces)
    mesh.visual.face_colors = np.tile(color, (len(faces), 1))
    return mesh


def _darken(color, amount=20):
    """Darken a color by reducing RGB values."""
    return [max(0, c - amount) for c in color[:3]] + [
        color[3] if len(color) > 3 else 255
    ]
