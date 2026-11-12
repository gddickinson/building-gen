"""Floor slabs with rectangular openings (stairwells), built from boxes so the openings stay open."""

from __future__ import annotations

import trimesh

from .stairs import _make_box

SLAB_COLOR = [200, 200, 200, 255]


def solid_rects(bounds: tuple, holes: list) -> list[tuple[float, float, float, float]]:
    """Split the box bounds minus the box holes into rectangles (minx, miny, maxx, maxy).

    The plane is cut on every hole edge; in each strip between consecutive y cuts, neighbouring solid cells are
    merged into one rectangle, left to right, strips front (low y) to back.
    """
    minx, miny, maxx, maxy = bounds
    xs = sorted({minx, maxx} | {min(max(v, minx), maxx) for h in holes for v in (h[0], h[2])})
    ys = sorted({miny, maxy} | {min(max(v, miny), maxy) for h in holes for v in (h[1], h[3])})
    rects = []
    for y0, y1 in zip(ys[:-1], ys[1:]):
        if y1 - y0 <= 1e-9:
            continue
        cy = (y0 + y1) / 2
        run = None
        for x0, x1 in zip(xs[:-1], xs[1:]):
            if x1 - x0 <= 1e-9:
                continue
            cx = (x0 + x1) / 2
            solid = not any(h[0] < cx < h[2] and h[1] < cy < h[3] for h in holes)
            if solid:
                run = [run[0], x1] if run else [x0, x1]
            elif run:
                rects.append((run[0], y0, run[1], y1))
                run = None
        if run:
            rects.append((run[0], y0, run[1], y1))
    return rects


def stairwell_holes(bounds: tuple, stair_bounds: list, margin: float = 0.05) -> list:
    """Stairwell openings, inset by margin; a hole is skipped if it would leave 1 m^2 or less of slab."""
    holes = []
    for b in stair_bounds:
        hole = (b[0] + margin, b[1] + margin, b[2] - margin, b[3] - margin)
        if hole[2] <= hole[0] or hole[3] <= hole[1]:
            continue
        area = sum((r[2] - r[0]) * (r[3] - r[1]) for r in solid_rects(bounds, holes + [hole]))
        if area > 1.0:
            holes.append(hole)
    return holes


def build_slab_with_holes(bounds: tuple, holes: list, y: float, thickness: float) -> trimesh.Trimesh:
    """Slab over the box bounds with the holes left open, as one mesh of boxes (plan y -> 3D z)."""
    boxes = [_make_box(r[0], y, r[1], r[2], y + thickness, r[3], SLAB_COLOR) for r in solid_rects(bounds, holes)]
    return trimesh.util.concatenate(boxes)
