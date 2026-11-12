"""Roof mesh generation."""

from __future__ import annotations

import numpy as np
import trimesh
from shapely.geometry import Polygon

from ..style.models import StyleParams


def build_roof_mesh(
    footprint: Polygon,
    base_y: float,
    style: StyleParams,
) -> trimesh.Trimesh | None:
    """Build a roof mesh from a building footprint.

    Currently supports gable and hip roofs for rectangular footprints.
    """
    coords = list(footprint.exterior.coords)[:-1]
    if len(coords) != 4:
        # Fallback: flat roof for non-rectangular footprints
        return _build_flat_roof(footprint, base_y, style)

    minx, miny, maxx, maxy = footprint.bounds
    w = maxx - minx  # width (X)
    d = maxy - miny  # depth (Z)

    ridge_height = style.roof_pitch * min(w, d) / 2.0

    if style.roof_type == "gable":
        return _build_gable_roof(minx, miny, maxx, maxy, base_y, ridge_height, style)
    elif style.roof_type == "hip":
        return _build_hip_roof(minx, miny, maxx, maxy, base_y, ridge_height, style)
    else:
        return _build_flat_roof(footprint, base_y, style)


def _build_gable_roof(
    minx: float, miny: float, maxx: float, maxy: float,
    base_y: float, ridge_height: float, style: StyleParams,
) -> trimesh.Trimesh:
    """Gable roof — ridge runs along the longer axis."""
    w = maxx - minx
    d = maxy - miny
    overhang = style.roof_overhang

    ridge_y = base_y + ridge_height
    eaves = [
        [minx - overhang, base_y, miny - overhang],  # 0: front-left
        [maxx + overhang, base_y, miny - overhang],  # 1: front-right
        [maxx + overhang, base_y, maxy + overhang],  # 2: back-right
        [minx - overhang, base_y, maxy + overhang],  # 3: back-left
    ]

    if d >= w:
        # Ridge runs along depth (Z axis): townhouses are deeper than wide
        mid_x = (minx + maxx) / 2.0
        verts = eaves + [
            [mid_x, ridge_y, miny - overhang],            # 4: ridge front
            [mid_x, ridge_y, maxy + overhang],            # 5: ridge back
        ]
        faces = [
            # Left slope
            [0, 4, 5], [0, 5, 3],
            # Right slope
            [1, 2, 5], [1, 5, 4],
            # Front gable triangle
            [0, 1, 4],
            # Back gable triangle
            [2, 3, 5],
        ]
    else:
        # Ridge runs along width (X axis): gables at the sides
        mid_z = (miny + maxy) / 2.0
        verts = eaves + [
            [minx - overhang, ridge_y, mid_z],            # 4: ridge left
            [maxx + overhang, ridge_y, mid_z],            # 5: ridge right
        ]
        faces = [
            # Front slope
            [0, 5, 4], [0, 1, 5],
            # Back slope
            [3, 5, 2], [3, 4, 5],
            # Left gable triangle
            [0, 4, 3],
            # Right gable triangle
            [1, 2, 5],
        ]

    return _roof_mesh(verts, faces, style)


def _build_hip_roof(
    minx: float, miny: float, maxx: float, maxy: float,
    base_y: float, ridge_height: float, style: StyleParams,
) -> trimesh.Trimesh:
    """Hip roof — all sides slope inward."""
    w = maxx - minx
    d = maxy - miny
    overhang = style.roof_overhang

    ridge_y = base_y + ridge_height
    # Ridge is inset from the shorter dimension
    inset = min(w, d) / 2.0
    eaves = [
        [minx - overhang, base_y, miny - overhang],  # 0
        [maxx + overhang, base_y, miny - overhang],  # 1
        [maxx + overhang, base_y, maxy + overhang],  # 2
        [minx - overhang, base_y, maxy + overhang],  # 3
    ]

    if d >= w:
        # Townhouse (deeper than wide): ridge runs along depth
        mid_x = (minx + maxx) / 2.0
        verts = eaves + [
            [mid_x, ridge_y, miny + inset],               # 4
            [mid_x, ridge_y, maxy - inset],               # 5
        ]
        faces = [
            # Front hip
            [0, 1, 4],
            # Right slope
            [1, 2, 5], [1, 5, 4],
            # Back hip
            [2, 3, 5],
            # Left slope
            [3, 0, 4], [3, 4, 5],
        ]
    else:
        # Wider than deep: ridge runs along width
        mid_z = (miny + maxy) / 2.0
        verts = eaves + [
            [minx + inset, ridge_y, mid_z],               # 4: ridge left
            [maxx - inset, ridge_y, mid_z],               # 5: ridge right
        ]
        faces = [
            # Left hip
            [3, 0, 4],
            # Front slope
            [0, 1, 5], [0, 5, 4],
            # Right hip
            [1, 2, 5],
            # Back slope
            [2, 3, 4], [2, 4, 5],
        ]

    return _roof_mesh(verts, faces, style)


def _build_flat_roof(
    footprint: Polygon, base_y: float, style: StyleParams,
) -> trimesh.Trimesh:
    """Simple flat roof / parapet."""
    parapet_h = 0.3
    coords = list(footprint.exterior.coords)[:-1]
    n = len(coords)

    verts = []
    for c in coords:
        verts.append([c[0], base_y, c[1]])
    for c in coords:
        verts.append([c[0], base_y + parapet_h, c[1]])

    faces = []
    # Top face
    for i in range(1, n - 1):
        faces.append([n, n + i, n + i + 1])
    # Sides
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j])
        faces.append([i, n + j, n + i])

    return _roof_mesh(verts, faces, style)


def _roof_mesh(verts: list, faces: list, style: StyleParams) -> trimesh.Trimesh:
    """Roof mesh with its faces turned to face outward.

    The face lists above are wound with normals pointing down into the building; a roof is an open
    surface, so fix_normals() cannot correct that, and viewers that cull back faces hid the roof.
    """
    faces = [list(reversed(f)) for f in faces]
    mesh = trimesh.Trimesh(
        vertices=np.array(verts, dtype=np.float64),
        faces=np.array(faces, dtype=np.int64),
    )
    mesh.fix_normals()
    mesh.visual.face_colors = np.tile(style.roof_color, (len(faces), 1))
    return mesh
