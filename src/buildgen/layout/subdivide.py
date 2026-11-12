"""Floor plan subdivision — Georgian-style grid layout.

Based on analysis of real Georgian floor plans, buildings are laid out:
- Front-to-back: 2 rows of rooms separated by the staircase hall
- Left-to-right: rooms sized proportionally within each row
- Central hall with staircase runs the full depth of the building
- Small rooms (closets, WC) are placed as sub-divisions of larger spaces

This produces the classic Georgian plan: enter through a central hall,
rooms to left and right, stair rising at the back of the hall.
"""

from __future__ import annotations

import random
from shapely.geometry import Polygon, box

from ..program.models import RoomSpec, RoomType
from .models import RoomPolygon


_FRONT_TYPES = {
    RoomType.ENTRANCE_HALL, RoomType.PARLOUR, RoomType.DRAWING_ROOM,
    RoomType.SHOP_FLOOR,
}
_REAR_TYPES = {
    RoomType.KITCHEN, RoomType.SCULLERY, RoomType.PANTRY,
}
_SMALL_TYPES = {
    RoomType.LANDING, RoomType.WC, RoomType.STAIRWELL,
    RoomType.DRESSING_ROOM, RoomType.PANTRY, RoomType.STORAGE,
}
_CIRCULATION = {
    RoomType.ENTRANCE_HALL, RoomType.HALLWAY, RoomType.LANDING,
}


def subdivide_floor(
    footprint: Polygon,
    rooms: list[RoomSpec],
    stairwell_rect: tuple[float, float, float, float] | None,
    rng: random.Random,
) -> list[RoomPolygon]:
    """Subdivide using a Georgian-inspired 2-column layout.

    The floor is split into:
    - A central column containing the hall/landing + stairwell
    - Left and right columns containing the main rooms
    - Small rooms carved out of corners of main rooms
    """
    if not rooms:
        return []

    minx, miny, maxx, maxy = footprint.bounds
    fw = maxx - minx
    fd = maxy - miny

    # Separate room types
    circulation = [r for r in rooms if r.room_type in _CIRCULATION]
    small = [r for r in rooms if r.room_type in _SMALL_TYPES
             and r.room_type not in _CIRCULATION
             and not r.is_stairwell]
    front = [r for r in rooms if r.room_type in _FRONT_TYPES
             and r.room_type not in _CIRCULATION]
    rear = [r for r in rooms if r.room_type in _REAR_TYPES]
    main = [r for r in rooms if r not in circulation and r not in small
            and r not in front and r not in rear and not r.is_stairwell]

    result: list[RoomPolygon] = []

    # ── Define the central hall/stair column ──
    # Georgian convention: narrow hall (~1.0-1.4m) with stair behind
    # This maximises room widths on either side (rooms should be ~3.5-4.5m)
    hall_width = 1.2 + rng.uniform(-0.1, 0.1)

    if stairwell_rect:
        sx1, sy1, sx2, sy2 = stairwell_rect
        # Centre the hall column on the stairwell
        stair_cx = (sx1 + sx2) / 2
        hall_x1 = stair_cx - hall_width / 2
        hall_x2 = stair_cx + hall_width / 2
        # Ensure stairwell fits within hall column
        hall_x1 = min(hall_x1, sx1)
        hall_x2 = max(hall_x2, sx2)
    else:
        # Centre the hall in the building
        hall_x1 = minx + (fw - hall_width) / 2
        hall_x2 = hall_x1 + hall_width

    # Clamp hall to building bounds, ensuring rooms on both sides
    min_wing = 2.5  # Minimum wing width for rooms
    hall_x1 = max(minx + min_wing, hall_x1)
    hall_x2 = min(maxx - min_wing, hall_x2)
    # If building is too narrow for 3 columns, use 2
    if hall_x2 - hall_x1 < 1.0:
        hall_x1 = minx + fw * 0.4
        hall_x2 = hall_x1 + 1.2

    # ── Place circulation rooms in the hall column ──
    # The hall doesn't run the full depth — it occupies the front portion
    # of the central column, with the stairwell behind it
    if circulation:
        circ_room = circulation[0]
        # Hall depth: from front wall to just past the stairwell
        if stairwell_rect:
            # Hall runs from the front to the foot of the stairwell, which
            # sits behind it in the same column (it used to run on past the
            # stairwell, so the hall and stairwell overlapped)
            max_hall_area = circ_room.max_area * 1.3
            max_hall_depth = max_hall_area / (hall_x2 - hall_x1) if (hall_x2 - hall_x1) > 0 else fd
            hall_depth = min(sy1 - miny, max_hall_depth)
        else:
            hall_depth = min(fd * 0.4, circ_room.max_area / (hall_x2 - hall_x1))
            hall_depth = max(2.0, hall_depth)

        poly = box(hall_x1, miny, hall_x2, miny + hall_depth)
        result.append(RoomPolygon(
            name=circ_room.name,
            room_type=circ_room.room_type.value,
            polygon=poly,
            floor=circ_room.floor,
        ))

        # Additional circulation rooms become small rooms
        if len(circulation) > 1:
            small.extend(circulation[1:])

    # ── Left and right wings ──
    # Each wing is the full depth of the building but only half the width
    # Rooms are stacked front-to-back within each wing
    left_w = hall_x1 - minx
    right_w = maxx - hall_x2

    # All non-circulation, non-small rooms go into left/right wings
    all_wing_rooms = front + main + rear

    # Distribute rooms alternately to left and right, keeping balance
    left_rooms: list[RoomSpec] = []
    right_rooms: list[RoomSpec] = []
    left_area = 0.0
    right_area = 0.0

    # Front rooms first — one on each side if possible
    for i, r in enumerate(front):
        if left_area <= right_area:
            left_rooms.append(r)
            left_area += r.target_area
        else:
            right_rooms.append(r)
            right_area += r.target_area

    # Then main + rear rooms
    for r in main + rear:
        if left_area <= right_area:
            left_rooms.append(r)
            left_area += r.target_area
        else:
            right_rooms.append(r)
            right_area += r.target_area

    # ── Subdivide each wing front-to-back ──
    if left_rooms and left_w > 1.5:
        polys = _subdivide_column(minx, miny, hall_x1, maxy, left_rooms, rng)
        result.extend(polys)

    if right_rooms and right_w > 1.5:
        polys = _subdivide_column(hall_x2, miny, maxx, maxy, right_rooms, rng)
        result.extend(polys)

    # ── Place small rooms by carving from largest adjacent rooms ──
    for sr in small:
        result = _carve_small_room(result, sr, rng)

    return result


def _subdivide_column(
    minx: float, miny: float, maxx: float, maxy: float,
    rooms: list[RoomSpec],
    rng: random.Random,
) -> list[RoomPolygon]:
    """Subdivide a vertical column into rooms top-to-bottom.

    Front rooms go at the bottom (y=0 = street), rear rooms at top.
    Each room gets height proportional to its target area / column width.
    """
    if not rooms:
        return []

    col_w = maxx - minx
    col_h = maxy - miny

    if len(rooms) == 1:
        r = rooms[0]
        # Don't let a single room be too deep — cap at reasonable aspect
        room_h = col_h
        max_depth = col_w * 2.5  # Max depth:width ratio of 2.5:1
        if r.max_area > 0:
            max_from_area = r.max_area * 1.3 / col_w if col_w > 0 else room_h
            max_depth = min(max_depth, max_from_area)
        room_h = min(room_h, max_depth)
        room_h = max(2.0, room_h)
        poly = box(minx, miny, maxx, miny + room_h)
        return [RoomPolygon(
            name=r.name, room_type=r.room_type.value,
            polygon=poly, floor=r.floor,
        )]

    # Sort: front rooms first (low y), rear rooms last (high y)
    def sort_key(r: RoomSpec) -> int:
        if r.room_type in _FRONT_TYPES:
            return 0
        elif r.room_type in _REAR_TYPES:
            return 2
        return 1

    sorted_rooms = sorted(rooms, key=sort_key)

    # Calculate heights from target areas
    total_target = sum(r.target_area for r in sorted_rooms)
    heights = []
    for r in sorted_rooms:
        target_h = r.target_area / col_w if col_w > 0 else 3.0
        max_h = (r.max_area * 1.2) / col_w if col_w > 0 else target_h * 1.5
        min_h = max(2.0, r.min_area / col_w) if col_w > 0 else 2.0
        h = max(min_h, min(target_h, max_h))
        heights.append(h)

    # Scale to fit
    total_h = sum(heights)
    if total_h > 0:
        scale = col_h / total_h
        heights = [h * scale for h in heights]

    # Clamp oversized rooms
    for _ in range(5):
        surplus = 0.0
        growable = []
        for i, (h, r) in enumerate(zip(heights, sorted_rooms)):
            area = h * col_w
            max_area = r.max_area * 1.3
            if r.room_type in _SMALL_TYPES:
                max_area = r.max_area * 1.1
            if area > max_area and len(sorted_rooms) > 1:
                clamped_h = max_area / col_w
                surplus += h - clamped_h
                heights[i] = clamped_h
            else:
                growable.append(i)
        if surplus > 0.1 and growable:
            share = surplus / len(growable)
            for idx in growable:
                heights[idx] += share
        else:
            break

    result = []
    y = miny
    for i, (r, h) in enumerate(zip(sorted_rooms, heights)):
        if i == len(sorted_rooms) - 1:
            h = maxy - y
        if h < 0.5:
            continue
        # Add slight variation
        h += rng.uniform(-0.15, 0.15)
        h = max(1.5, h)
        if y + h > maxy:
            h = maxy - y

        poly = box(minx, y, maxx, y + h)
        result.append(RoomPolygon(
            name=r.name, room_type=r.room_type.value,
            polygon=poly, floor=r.floor,
        ))
        y += h

    return result


def _carve_small_room(
    existing: list[RoomPolygon],
    small_spec: RoomSpec,
    rng: random.Random,
) -> list[RoomPolygon]:
    """Carve a small room out of a corner of the largest rectangular room.

    The host keeps the rest of its rectangle as an L-shaped room (it used to
    keep its full rectangle, overlapping the small room); its main_bounds is
    the larger rectangular part, used for placing fittings. Rooms that are
    already L-shaped are not carved again.
    """
    if not existing:
        return existing

    rects = [r for r in existing if len(r.polygon.exterior.coords) == 5]
    candidates = [r for r in rects if r.area > small_spec.target_area * 2]
    if not candidates:
        candidates = [r for r in rects if r.area > small_spec.min_area * 1.5]
    if not candidates:
        return existing

    # Pick the largest candidate
    host = max(candidates, key=lambda r: r.area)
    hb = host.bounds  # (minx, miny, maxx, maxy)
    hw = hb[2] - hb[0]
    hh = hb[3] - hb[1]

    # Try to make it roughly square-ish
    target_area = small_spec.target_area
    small_w = min(hw * 0.35, max(1.0, (target_area ** 0.5)))
    small_h = target_area / small_w if small_w > 0 else 1.5
    small_h = min(small_h, hh * 0.45)
    small_w = max(0.8, small_w)
    small_h = max(0.8, small_h)

    corner = rng.choice(["tr", "tl", "br", "bl"])
    if corner == "tr":
        sx1, sy1 = hb[2] - small_w, hb[3] - small_h
        sx2, sy2 = hb[2], hb[3]
    elif corner == "tl":
        sx1, sy1 = hb[0], hb[3] - small_h
        sx2, sy2 = hb[0] + small_w, hb[3]
    elif corner == "br":
        sx1, sy1 = hb[2] - small_w, hb[1]
        sx2, sy2 = hb[2], hb[1] + small_h
    else:
        sx1, sy1 = hb[0], hb[1]
        sx2, sy2 = hb[0] + small_w, hb[1] + small_h

    if small_w >= hw or small_h >= hh:
        return existing  # the small room would take a whole side of the host

    small_poly = box(sx1, sy1, sx2, sy2)
    host_poly, main = _l_shape(hb, (sx1, sy1, sx2, sy2), corner)
    if host_poly.area < small_spec.min_area:
        return existing

    new_existing = [r for r in existing if r is not host]
    new_existing.append(RoomPolygon(
        name=host.name, room_type=host.room_type,
        polygon=host_poly, floor=host.floor, main_bounds=main,
    ))
    new_existing.append(RoomPolygon(
        name=small_spec.name,
        room_type=small_spec.room_type.value,
        polygon=small_poly,
        floor=small_spec.floor,
    ))

    return new_existing


def _l_shape(hb: tuple, sb: tuple, corner: str) -> tuple[Polygon, tuple]:
    """The host box hb minus the corner box sb: (L-shaped polygon, its larger rectangular part).

    The ring follows shapely.box's order (counter-clockwise from (maxx, miny)) with the cut corner
    replaced by the three corners of the notch.
    """
    x0, y0, x1, y1 = hb
    ring = {"br": (x1, y0), "tr": (x1, y1), "tl": (x0, y1), "bl": (x0, y0)}
    order = ["br", "tr", "tl", "bl"]
    inner = {"tr": (sb[0], sb[1]), "tl": (sb[2], sb[1]), "br": (sb[0], sb[3]), "bl": (sb[2], sb[3])}[corner]
    coords = []
    for i, k in enumerate(order):
        c = ring[k]
        if k != corner:
            coords.append(c)
            continue
        p, n = ring[order[i - 1]], ring[order[(i + 1) % 4]]
        a = (c[0], inner[1]) if p[0] == c[0] else (inner[0], c[1])
        d = (c[0], inner[1]) if n[0] == c[0] else (inner[0], c[1])
        coords.extend([a, inner, d])
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    # Larger rectangle of the L: the full-width band or the full-height band beside the notch
    band_w = (x0, y0, x1, y1 - sh) if corner in ("tr", "tl") else (x0, y0 + sh, x1, y1)
    band_h = (x0, y0, x1 - sw, y1) if corner in ("tr", "br") else (x0 + sw, y0, x1, y1)
    area = lambda b: (b[2] - b[0]) * (b[3] - b[1])
    main = band_w if area(band_w) >= area(band_h) else band_h
    return Polygon(coords), main
