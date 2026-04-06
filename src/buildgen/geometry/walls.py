"""Wall mesh generation and opening cutting."""

from __future__ import annotations

import numpy as np
import trimesh

from ..layout.models import Opening, OpeningType, WallSegment, WallType
from ..style.models import StyleParams


def build_wall_mesh(
    wall: WallSegment,
    floor_y: float,
    wall_height: float,
    style: StyleParams,
) -> trimesh.Trimesh | None:
    """Build a 3D wall mesh from a 2D wall segment."""
    if wall.length < 0.01:
        return None

    sx, sy = wall.start
    ex, ey = wall.end
    t = wall.thickness / 2.0

    # Direction and normal
    dx = ex - sx
    dy = ey - sy
    length = (dx * dx + dy * dy) ** 0.5
    if length < 0.01:
        return None

    nx = -dy / length * t
    ny = dx / length * t

    # 4 corners of wall base (in XZ plane, Y is up)
    corners = [
        (sx + nx, sy + ny),  # start + normal
        (sx - nx, sy - ny),  # start - normal
        (ex - nx, ey - ny),  # end - normal
        (ex + nx, ey + ny),  # end + normal
    ]

    y_bot = floor_y
    y_top = floor_y + wall_height

    # 8 vertices: 4 bottom + 4 top
    verts = []
    for cx, cz in corners:
        verts.append([cx, y_bot, cz])
    for cx, cz in corners:
        verts.append([cx, y_top, cz])

    # 6 faces (2 triangles each for 6 quad faces of the box)
    faces = [
        # Bottom
        [0, 2, 1], [0, 3, 2],
        # Top
        [4, 5, 6], [4, 6, 7],
        # Front (normal side)
        [0, 4, 7], [0, 7, 3],
        # Back
        [1, 6, 5], [1, 2, 6],
        # Left end
        [0, 1, 5], [0, 5, 4],
        # Right end
        [2, 3, 7], [2, 7, 6],
    ]

    mesh = trimesh.Trimesh(
        vertices=np.array(verts, dtype=np.float64),
        faces=np.array(faces, dtype=np.int64),
    )
    mesh.fix_normals()

    # Color based on wall type
    if wall.wall_type == WallType.EXTERIOR:
        color = style.exterior_wall_color
    else:
        color = style.interior_wall_color

    mesh.visual.face_colors = np.tile(color, (len(faces), 1))
    return mesh


def cut_opening_in_wall(
    wall_mesh: trimesh.Trimesh,
    wall: WallSegment,
    opening: Opening,
    floor_y: float,
    style: StyleParams,
) -> trimesh.Trimesh:
    """Cut a door or window opening in a wall mesh.

    Uses boolean subtraction to carve the opening.
    Falls back to returning the original mesh if boolean fails.
    """
    ox, oy = opening.position
    sx, sy = wall.start
    ex, ey = wall.end

    # Check if opening is on this wall
    dx = ex - sx
    dy = ey - sy
    length = (dx * dx + dy * dy) ** 0.5
    if length < 0.01:
        return wall_mesh

    # Project opening position onto wall line
    t = ((ox - sx) * dx + (oy - sy) * dy) / (length * length)
    # Point on wall closest to opening
    px = sx + t * dx
    py = sy + t * dy
    dist = ((ox - px) ** 2 + (oy - py) ** 2) ** 0.5

    if dist > wall.thickness * 2 or t < -0.1 or t > 1.1:
        return wall_mesh

    # Create cutting box
    half_w = opening.width / 2.0
    ht = wall.thickness

    if opening.opening_type == OpeningType.WINDOW:
        y_bot = floor_y + opening.sill_height
        y_top = floor_y + opening.sill_height + opening.height
    else:
        y_bot = floor_y
        y_top = floor_y + opening.height

    # Normal direction
    nx = -dy / length
    ny = dx / length

    # Centre of cut
    cx = px
    cz = py
    # Build a box aligned with the wall
    box_verts = []
    for s in [-1, 1]:  # along wall
        for n in [-1, 1]:  # across wall (normal)
            for v in [0, 1]:  # vertical
                vx = cx + s * half_w * dx / length + n * ht * nx
                vz = cz + s * half_w * dy / length + n * ht * ny
                vy = y_bot + v * (y_top - y_bot)
                box_verts.append([vx, vy, vz])

    box_faces = [
        [0, 1, 3], [0, 3, 2],
        [4, 7, 5], [4, 6, 7],
        [0, 4, 5], [0, 5, 1],
        [2, 3, 7], [2, 7, 6],
        [0, 2, 6], [0, 6, 4],
        [1, 7, 3], [1, 5, 7],
    ]

    cut_box = trimesh.Trimesh(
        vertices=np.array(box_verts, dtype=np.float64),
        faces=np.array(box_faces, dtype=np.int64),
    )
    cut_box.fix_normals()

    try:
        result = wall_mesh.difference(cut_box)
        if result and result.volume > 0.01:
            result.visual.face_colors = wall_mesh.visual.face_colors[0]
            return result
    except Exception:
        pass

    return wall_mesh
