"""Grid-based floor plan layout.

Instead of BSP subdivision, this lays out rooms on a defined grid.
Each room occupies one cell of a rows x columns grid. The grid
proportions come from the template (based on real floor plans).

Variation is achieved by:
  - Scaling the overall footprint (width_var, depth_var)
  - Including/excluding optional rooms
  - Adjusting row heights proportionally
  - Adding random jitter to dividing lines
"""

from __future__ import annotations

import random
from pathlib import Path

import yaml
from shapely.geometry import box

from ..program.models import BuildingProgram, RoomType
from .models import FloorPlan, RoomPolygon, Opening, OpeningType, WallSegment, WallType
from .fixtures import place_fixtures_in_room


def load_grid_template(template_path: Path) -> dict:
    """Load a grid-based template YAML."""
    with open(template_path) as f:
        return yaml.safe_load(f)


def generate_from_grid(
    template: dict,
    seed: int = 0,
    style: str = "georgian",
) -> tuple[list[FloorPlan], float, float]:
    """Generate floor plans from a grid template.

    Returns:
        (floor_plans, footprint_width, footprint_depth)
    """
    rng = random.Random(seed)

    # Determine footprint with variation
    fp = template.get("footprint", {})
    width = fp.get("width", 8.5) + rng.uniform(
        -fp.get("width_var", 0.8), fp.get("width_var", 0.8)
    )
    depth = fp.get("depth", 11.0) + rng.uniform(
        -fp.get("depth_var", 1.0), fp.get("depth_var", 1.0)
    )
    wall_t = fp.get("wall_thickness", 0.35)

    grid = template.get("grid", {})
    col_widths = grid.get("col_widths", [0.42, 0.16, 0.42])
    num_cols = len(col_widths)

    # Calculate absolute column positions
    total_cw = sum(col_widths)
    col_positions = []  # (x_start, x_end) for each column
    x = 0.0
    for cw in col_widths:
        col_w = width * (cw / total_cw)
        # Add slight random jitter to interior dividing lines
        jitter = rng.uniform(-0.1, 0.1)
        col_positions.append((x, x + col_w + jitter))
        x += col_w + jitter
    # Fix last column to reach the building edge
    if col_positions:
        last = col_positions[-1]
        col_positions[-1] = (last[0], width)

    floor_plans = []

    for floor_def in grid.get("floors", []):
        floor_idx = floor_def["index"]
        row_fracs = floor_def.get("rows", [0.5, 0.5])
        num_rows = len(row_fracs)

        # Calculate absolute row positions
        total_rf = sum(row_fracs)
        row_positions = []  # (y_start, y_end) for each row
        y = 0.0
        for rf in row_fracs:
            row_h = depth * (rf / total_rf)
            jitter = rng.uniform(-0.15, 0.15)
            row_positions.append((y, y + row_h + jitter))
            y += row_h + jitter
        if row_positions:
            last = row_positions[-1]
            row_positions[-1] = (last[0], depth)

        rooms: list[RoomPolygon] = []
        footprint = box(0, 0, width, depth)

        for room_def in floor_def.get("rooms", []):
            # Check optional rooms
            if room_def.get("optional", False):
                if rng.random() > room_def.get("probability", 0.5):
                    continue

            col = room_def.get("col", 0)
            row = room_def.get("row", 0)

            if col >= num_cols or row >= num_rows:
                continue

            x1, x2 = col_positions[col]
            y1, y2 = row_positions[row]

            # Ensure positive dimensions
            if x2 <= x1 or y2 <= y1:
                continue

            # Sub-cell splitting: room can take a fraction of the cell
            # "half": "top"/"bottom"/"left"/"right" takes half the cell
            # "fraction": 0.0-1.0 takes that fraction (from the specified side)
            half = room_def.get("half", None)
            frac = room_def.get("fraction", 0.5)
            if half == "top":
                y1 = y2 - (y2 - y1) * frac
            elif half == "bottom":
                y2 = y1 + (y2 - y1) * frac
            elif half == "left":
                x2 = x1 + (x2 - x1) * frac
            elif half == "right":
                x1 = x2 - (x2 - x1) * frac

            # Multi-column span
            col_span = room_def.get("col_span", 1)
            if col_span > 1 and col + col_span - 1 < num_cols:
                _, x2 = col_positions[col + col_span - 1]

            # Multi-row span
            row_span = room_def.get("row_span", 1)
            if row_span > 1 and row + row_span - 1 < num_rows:
                _, y2 = row_positions[row + row_span - 1]

            poly = box(x1, y1, x2, y2)
            room_type = room_def.get("type", "generic")

            room = RoomPolygon(
                name=room_def["name"],
                room_type=room_type,
                polygon=poly,
                floor=floor_idx,
            )
            rooms.append(room)

        _resolve_overlaps(rooms)

        plan = FloorPlan(
            floor_index=floor_idx,
            rooms=rooms,
            footprint=footprint,
        )

        # Extract walls
        plan.walls = _extract_walls(plan, wall_t)

        # Place doors and windows
        _place_doors_grid(plan, rng)
        _place_windows_grid(plan, rng)

        # Place fixtures
        for room in plan.rooms:
            fixtures = place_fixtures_in_room(
                room.bounds, room.room_type, rng
            )
            room._fixtures = fixtures

        floor_plans.append(plan)

    return floor_plans, width, depth


def _resolve_overlaps(rooms: list[RoomPolygon], eps: float = 1e-9) -> None:
    """Give a cell shared by two rooms to the smaller one, trimming the larger (in place).

    Templates put some rooms in part of a cell that another room also fills (a WC in the bottom of the
    staircase cell, a hallway spanning the staircase's row, a closet in half a bedroom). The smaller room
    must cover a whole side of the larger one; the larger keeps the rest of its rectangle.
    """
    for _ in range(len(rooms)):
        changed = False
        for i, a in enumerate(rooms):
            for b in rooms[i + 1:]:
                ab, bb = a.bounds, b.bounds
                if min(ab[2], bb[2]) - max(ab[0], bb[0]) <= eps or min(ab[3], bb[3]) - max(ab[1], bb[1]) <= eps:
                    continue
                big, small = (a, b) if a.area >= b.area else (b, a)
                g, m = list(big.bounds), small.bounds
                if m[0] <= g[0] + eps and m[2] >= g[2] - eps:      # small spans big's width
                    if m[3] >= g[3] - eps:
                        g[3] = m[1]
                    elif m[1] <= g[1] + eps:
                        g[1] = m[3]
                    else:
                        continue
                elif m[1] <= g[1] + eps and m[3] >= g[3] - eps:    # small spans big's depth
                    if m[2] >= g[2] - eps:
                        g[2] = m[0]
                    elif m[0] <= g[0] + eps:
                        g[0] = m[2]
                    else:
                        continue
                else:
                    continue
                if g[2] - g[0] > eps and g[3] - g[1] > eps:
                    big.polygon = box(*g)
                    changed = True
        if not changed:
            return


def _extract_walls(plan: FloorPlan, thickness: float) -> list[WallSegment]:
    """Extract walls using structure-first approach.

    1. ALWAYS create complete exterior walls from the footprint boundary
    2. Add interior partition walls from shared room edges
    This guarantees 100% exterior wall coverage on every floor.
    """
    walls = []

    # ── Step 1: Complete exterior walls from footprint ──
    # These exist regardless of what rooms are inside
    if plan.footprint:
        ext_coords = list(plan.footprint.exterior.coords)
        for i in range(len(ext_coords) - 1):
            s = (round(ext_coords[i][0], 2), round(ext_coords[i][1], 2))
            e = (round(ext_coords[i+1][0], 2), round(ext_coords[i+1][1], 2))
            from shapely.geometry import LineString
            edge = LineString([s, e])
            if edge.length < 0.01:
                continue
            walls.append(WallSegment(
                start=s, end=e,
                wall_type=WallType.EXTERIOR,
                thickness=thickness,
            ))

    # ── Step 2: Interior partition walls from room edges ──
    # An interior wall exists where two rooms share an edge
    # OR where a room edge is not on the exterior boundary
    fp_boundary = plan.footprint.boundary if plan.footprint else None
    seen_edges = set()

    # Track which edges are exterior (already added above)
    ext_edge_keys = set()
    for w in walls:
        s = (round(w.start[0], 2), round(w.start[1], 2))
        e = (round(w.end[0], 2), round(w.end[1], 2))
        ext_edge_keys.add((min(s, e), max(s, e)))

    for room in plan.rooms:
        coords = list(room.polygon.exterior.coords)
        for i in range(len(coords) - 1):
            s = (round(coords[i][0], 2), round(coords[i][1], 2))
            e = (round(coords[i+1][0], 2), round(coords[i+1][1], 2))

            from shapely.geometry import LineString
            edge = LineString([s, e])
            if edge.length < 0.01:
                continue

            key = (min(s, e), max(s, e))

            # Skip if already added as exterior wall
            if key in ext_edge_keys:
                continue

            # Skip if already added as interior wall
            if key in seen_edges:
                continue
            seen_edges.add(key)

            # Check if this edge is on the exterior boundary
            # (it might be a sub-segment of an exterior wall)
            is_on_boundary = False
            if fp_boundary:
                from shapely.geometry import Point
                d1 = fp_boundary.distance(Point(s))
                d2 = fp_boundary.distance(Point(e))
                mid = ((s[0]+e[0])/2, (s[1]+e[1])/2)
                d_mid = fp_boundary.distance(Point(mid))
                is_on_boundary = d1 < 0.1 and d2 < 0.1 and d_mid < 0.1

            if not is_on_boundary:
                walls.append(WallSegment(
                    start=s, end=e,
                    wall_type=WallType.INTERIOR,
                    thickness=thickness * 0.4,  # Interior walls thinner
                ))

    return walls


def _place_doors_grid(plan: FloorPlan, rng: random.Random) -> None:
    """Place doors between adjacent rooms in a grid layout."""
    from shapely.geometry import LineString

    placed = set()

    for i, room_a in enumerate(plan.rooms):
        for j, room_b in enumerate(plan.rooms):
            if i >= j:
                continue
            if room_a.room_type == "stairwell" or room_b.room_type == "stairwell":
                continue

            # Check if rooms share an edge
            shared = _shared_edge(room_a, room_b)
            if not shared:
                continue

            key = tuple(sorted([room_a.name, room_b.name]))
            if key in placed:
                continue
            placed.add(key)

            mid = ((shared[0][0]+shared[1][0])/2, (shared[0][1]+shared[1][1])/2)
            room_a.openings.append(Opening(
                opening_type=OpeningType.DOOR,
                position=mid, width=0.9, height=2.1,
            ))

    # Front door — find any entrance-type room
    if plan.floor_index == 0 and plan.footprint:
        fb = plan.footprint.bounds
        entrance = None
        for name in ["entrance_hall", "hallway", "entrance_passage",
                     "hall", "foyer", "entrance"]:
            entrance = plan.room_by_name(name)
            if entrance:
                break

        if entrance:
            cx = (entrance.bounds[0] + entrance.bounds[2]) / 2
            entrance.openings.append(Opening(
                opening_type=OpeningType.FRONT_DOOR,
                position=(cx, fb[1]), width=1.1, height=2.4,
            ))

        # Rear door — add a back door on a rear room (kitchen or back room)
        for name in ["kitchen", "scullery", "back_room", "morning_room"]:
            rear = plan.room_by_name(name)
            if rear:
                rcx = (rear.bounds[0] + rear.bounds[2]) / 2
                rear.openings.append(Opening(
                    opening_type=OpeningType.FRONT_DOOR,
                    position=(rcx, fb[3]), width=0.9, height=2.1,
                ))
                break


def _place_windows_grid(plan: FloorPlan, rng: random.Random) -> None:
    """Place windows only on true exterior walls.

    An edge is exterior if it lies on the building footprint boundary (rooms
    are inside the footprint, so such an edge is never shared with another
    room). Earlier only edges matching a whole side of the footprint counted,
    so rooms sharing a facade with a neighbour got no windows.
    """
    if not plan.footprint:
        return

    no_window_types = {"stairwell", "landing", "storage", "pantry", "wc",
                       "dressing_room", "hallway"}

    from shapely.geometry import LineString, Point

    fp_boundary = plan.footprint.boundary

    def on_boundary(a, b) -> bool:
        """The edge a-b lies along the footprint boundary (a whole side or part of one)."""
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        return all(fp_boundary.distance(Point(p)) < 0.01 for p in (a, b, mid))

    for room in plan.rooms:
        if room.room_type in no_window_types:
            continue

        coords = list(room.polygon.exterior.coords)
        for i in range(len(coords) - 1):
            edge = LineString([coords[i], coords[i+1]])
            if edge.length < 1.0:
                continue

            # Only edges on the outside of the building get windows
            if not on_boundary(coords[i], coords[i+1]):
                continue

            num_win = max(1, int(edge.length / 2.0))
            for wi in range(num_win):
                t = (wi + 0.5) / num_win
                pt = edge.interpolate(t, normalized=True)
                room.openings.append(Opening(
                    opening_type=OpeningType.WINDOW,
                    position=(pt.x, pt.y),
                    width=1.0, height=1.4, sill_height=0.9,
                ))


def _shared_edge(room_a: RoomPolygon, room_b: RoomPolygon) -> tuple | None:
    """Find shared edge between two rooms."""
    from shapely.geometry import LineString

    coords_a = list(room_a.polygon.exterior.coords)
    coords_b = list(room_b.polygon.exterior.coords)

    for i in range(len(coords_a) - 1):
        edge_a = LineString([coords_a[i], coords_a[i+1]])
        if edge_a.length < 0.1:
            continue
        for j in range(len(coords_b) - 1):
            edge_b = LineString([coords_b[j], coords_b[j+1]])
            if edge_b.length < 0.1:
                continue
            if edge_a.distance(edge_b) < 0.05:
                # Check for overlap
                inter = edge_a.buffer(0.02).intersection(edge_b.buffer(0.02))
                if inter and not inter.is_empty and inter.area > 0.01:
                    return (coords_a[i], coords_a[i+1])
    return None
