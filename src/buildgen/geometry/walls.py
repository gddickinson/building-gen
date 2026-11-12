"""Wall mesh generation with door and window openings.

Walls are boxes along their centre line; openings are left by assembling the wall from solid pieces
(build_wall_with_openings), so no mesh boolean engine (manifold3d, Blender) is needed.
"""

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


def opening_span(
    wall: WallSegment,
    opening: Opening,
    floor_y: float,
    wall_height: float,
) -> tuple[float, float, float, float] | None:
    """Where an opening cuts this wall: (along_start, along_end, y_bottom, y_top), or None if not on it.

    Distances along the wall are measured from wall.start and clipped to the wall; heights are clipped
    to the storey (floor_y .. floor_y + wall_height).
    """
    ox, oy = opening.position
    sx, sy = wall.start
    ex, ey = wall.end

    dx = ex - sx
    dy = ey - sy
    length = (dx * dx + dy * dy) ** 0.5
    if length < 0.01:
        return None

    # Project opening position onto wall line
    t = ((ox - sx) * dx + (oy - sy) * dy) / (length * length)
    px = sx + t * dx
    py = sy + t * dy
    dist = ((ox - px) ** 2 + (oy - py) ** 2) ** 0.5
    if dist > wall.thickness * 2 or t < -0.1 or t > 1.1:
        return None

    if opening.opening_type == OpeningType.WINDOW:
        y_bot = floor_y + opening.sill_height
        y_top = floor_y + opening.sill_height + opening.height
    else:
        y_bot = floor_y
        y_top = floor_y + opening.height

    centre = t * length
    a = max(0.0, centre - opening.width / 2.0)
    b = min(length, centre + opening.width / 2.0)
    y_bot = max(floor_y, y_bot)
    y_top = min(floor_y + wall_height, y_top)
    if b - a < 1e-6 or y_top - y_bot < 1e-6:
        return None
    return (a, b, y_bot, y_top)


def _subtract_ranges(solid: list, cut: tuple) -> list:
    """Remove the interval cut=(lo, hi) from a sorted list of (lo, hi) intervals."""
    out = []
    for lo, hi in solid:
        if cut[1] <= lo or cut[0] >= hi:
            out.append((lo, hi))
            continue
        if cut[0] > lo:
            out.append((lo, cut[0]))
        if cut[1] < hi:
            out.append((cut[1], hi))
    return [r for r in out if r[1] - r[0] > 1e-6]


def build_wall_with_openings(
    wall: WallSegment,
    spans: list,
    floor_y: float,
    wall_height: float,
    style: StyleParams,
) -> trimesh.Trimesh | None:
    """Build a wall with its door and window openings left open.

    The wall is assembled from solid boxes around the openings (below sills, above heads, between
    openings), so it needs no mesh boolean engine. spans come from opening_span().
    """
    if not spans:
        return build_wall_mesh(wall, floor_y, wall_height, style)

    sx, sy = wall.start
    ex, ey = wall.end
    dx = ex - sx
    dy = ey - sy
    length = (dx * dx + dy * dy) ** 0.5
    y0, y1 = floor_y, floor_y + wall_height

    cuts = sorted({0.0, length} | {s[0] for s in spans} | {s[1] for s in spans})
    pieces = []  # [along_start, along_end, solid vertical ranges]
    for u, v in zip(cuts[:-1], cuts[1:]):
        if v - u < 1e-6:
            continue
        mid = (u + v) / 2.0
        solid = [(y0, y1)]
        for a, b, yb, yt in spans:
            if a < mid < b:
                solid = _subtract_ranges(solid, (yb, yt))
        if pieces and pieces[-1][2] == solid:
            pieces[-1][1] = v
        else:
            pieces.append([u, v, solid])

    meshes = []
    volume = 0.0
    for u, v, solid in pieces:
        start = (sx + dx / length * u, sy + dy / length * u)
        end = (sx + dx / length * v, sy + dy / length * v)
        part = WallSegment(start=start, end=end, wall_type=wall.wall_type, thickness=wall.thickness)
        for lo, hi in solid:
            m = build_wall_mesh(part, lo, hi - lo, style)
            if m is not None:
                meshes.append(m)
                volume += (v - u) * wall.thickness * (hi - lo)

    if not meshes or volume <= 0.01:
        return build_wall_mesh(wall, floor_y, wall_height, style)
    return trimesh.util.concatenate(meshes)


def cut_opening_in_wall(
    wall_mesh: trimesh.Trimesh,
    wall: WallSegment,
    opening: Opening,
    floor_y: float,
    style: StyleParams,
) -> trimesh.Trimesh:
    """Return the wall rebuilt with one door or window opening left open (or wall_mesh if not on it).

    Kept for compatibility; GeometryBuilder collects every opening with opening_span() and calls
    build_wall_with_openings() once per wall.
    """
    span = opening_span(wall, opening, floor_y, style.floor_height)
    if span is None:
        return wall_mesh
    return build_wall_with_openings(wall, [span], floor_y, style.floor_height, style)
