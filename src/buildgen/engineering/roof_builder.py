"""Detailed roof construction at component level.

Every individual element of a traditional cut timber roof:

Structure:
- Ridge board: horizontal board at apex
- Common rafters: sloping beams from wall plate to ridge
- Purlins: horizontal beams supporting rafters mid-span
- Ceiling joists / collar ties: horizontal members tying rafters
- Hip/valley rafters: diagonal rafters at roof intersections
- Wall plates: timber on wall tops, rafters bear on these

Covering:
- Battens: horizontal timber strips rafters, tiles/slates nail to these
- Counter battens: vertical strips for ventilation (modern)
- Roofing felt/membrane: waterproof layer under tiles
- Tiles or slates: individual weathering units
- Ridge tiles: capping at ridge
- Lead flashings: weathering at junctions

Dimensions from TRADA guidance, BS 5534, and measured examples.
"""

from __future__ import annotations

import math

from .elements import Element, ElementType


# ── Rafter dimensions (TRADA / BS EN 1995) ───────────────────────

RAFTER_WIDTH = 0.047     # 47mm standard
RAFTER_SPACING = 0.400   # 400mm centres

# Rafter depth from span table (C16, 400mm centres):
#   Span ≤ 2.0m: 47x100
#   Span ≤ 2.5m: 47x125
#   Span ≤ 3.0m: 47x150
#   Span ≤ 3.75m: 47x175
#   Span ≤ 4.5m: 47x200

# ── Ridge and purlins ────────────────────────────────────────────

RIDGE_W = 0.038          # 38mm ridge board width
RIDGE_H = 0.175          # 175mm ridge board depth (min = rafter depth)
PURLIN_W = 0.075         # 75mm purlin width
PURLIN_H = 0.175         # 175mm purlin depth

# ── Battens ───────────────────────────────────────────────────────

BATTEN_W = 0.038         # 38mm batten width
BATTEN_H = 0.025         # 25mm batten height
SLATE_BATTEN_GAUGE = 0.190  # 190mm gauge for 600x300 slates (double lap)
TILE_BATTEN_GAUGE = 0.100   # 100mm gauge for plain tiles (triple lap)

# ── Tiles and slates ─────────────────────────────────────────────

SLATE_600x300 = (0.600, 0.300, 0.005)  # L, W, T in metres
SLATE_500x250 = (0.500, 0.250, 0.005)
PLAIN_TILE = (0.265, 0.165, 0.012)
PANTILE = (0.420, 0.330, 0.015)

# Ridge tiles
RIDGE_TILE_L = 0.300     # 300mm ridge tile length
RIDGE_TILE_W = 0.250     # 250mm wide (half-round)
RIDGE_TILE_H = 0.075     # 75mm height

# ── Ceiling joists / collar ties ──────────────────────────────────

CEILING_JOIST_W = 0.047
CEILING_JOIST_H = 0.100   # 100mm for typical span
COLLAR_TIE_W = 0.047
COLLAR_TIE_H = 0.100

# ── Lead flashings ───────────────────────────────────────────────

LEAD_T = 0.002           # Code 4 lead: 2mm thick
LEAD_SOAKER_W = 0.175    # 175mm soaker width


def build_detailed_roof(
    width: float,
    depth: float,
    base_y: float,
    pitch_deg: float = 35.0,
    roof_type: str = "gable",
    covering: str = "slate",
    parent: str = "roof",
) -> list[Element]:
    """Build a complete roof with every component.

    Args:
        width: Building width (X dimension)
        depth: Building depth (Z dimension)
        base_y: Height of eaves (top of wall)
        pitch_deg: Roof pitch angle
        roof_type: "gable", "hip", or "flat"
        covering: "slate", "plain_tile", or "pantile"
    """
    elements = []

    pitch_rad = math.radians(pitch_deg)
    half_span = width / 2
    rafter_length = half_span / math.cos(pitch_rad)
    ridge_height = half_span * math.tan(pitch_rad)

    rafter_depth = _select_rafter_depth(rafter_length)
    num_rafters_per_side = int(depth / RAFTER_SPACING) + 1

    # ── WALL PLATES (on top of each wall) ──
    # South/north plates run along X
    for wz, name in [(0, "south"), (depth, "north")]:
        elements.append(Element(
            element_type=ElementType.WALL_PLATE,
            material_name="softwood_c24",
            x=width / 2, y=base_y, z=wz,
            length=width, width=0.100, height=0.075,
            parent=f"{parent}_wallplate_{name}",
        ))
    # East/west plates run along Z — swap length and width
    for wx, name in [(0, "west"), (width, "east")]:
        elements.append(Element(
            element_type=ElementType.WALL_PLATE,
            material_name="softwood_c24",
            x=wx, y=base_y, z=depth / 2,
            length=0.100, width=depth, height=0.075,
            parent=f"{parent}_wallplate_{name}",
        ))

    # ── RIDGE BOARD ──
    ridge_y = base_y + ridge_height
    if roof_type == "hip":
        # Hip ridge is shorter (inset from gable ends)
        ridge_start_z = half_span  # Inset by half-span
        ridge_end_z = depth - half_span
        ridge_len = max(0.1, ridge_end_z - ridge_start_z)
        ridge_cz = (ridge_start_z + ridge_end_z) / 2
    else:
        ridge_len = depth
        ridge_cz = depth / 2

    # Ridge runs along Z — swap length and width
    elements.append(Element(
        element_type=ElementType.RIDGE_BOARD,
        material_name="softwood_c24",
        x=width / 2, y=ridge_y, z=ridge_cz,
        length=RIDGE_W, width=ridge_len, height=max(RIDGE_H, rafter_depth),
        parent=f"{parent}_ridge",
    ))

    # ── PURLINS (if rafter span > 2.5m, need intermediate support) ──
    # For hip roofs, purlins get SHORTER as they go higher up the slope,
    # following the hip line. At height fraction t (0=eaves, 1=ridge):
    #   purlin extends from z = t*hip_inset to z = depth - t*hip_inset
    # This matches the diagonal hip rafter line.
    if rafter_length > 2.5:
        hip_inset_z = half_span if roof_type == "hip" else 0

        purlin_count = max(1, int(rafter_length / 2.0))
        for pi in range(1, purlin_count + 1):
            t = pi / (purlin_count + 1)
            purlin_y = base_y + t * ridge_height

            # Purlin Z limits follow the hip diagonal
            z_start = t * hip_inset_z
            z_end = depth - t * hip_inset_z
            purlin_span = max(0.5, z_end - z_start)
            purlin_cz = (z_start + z_end) / 2

            for side_x in [t * half_span, width - t * half_span]:
                elements.append(Element(
                    element_type=ElementType.PURLIN,
                    material_name="softwood_c24",
                    x=side_x, y=purlin_y, z=purlin_cz,
                    length=PURLIN_W, width=purlin_span, height=PURLIN_H,
                    parent=f"{parent}_purlin",
                ))

    # ── COMMON RAFTERS (both slopes) ──
    # Stepped segments for 2D diagnostic rendering.
    # For hip roof, skip rafters in the hip zone (those are jack rafters).
    segments_per_rafter = 8
    seg_dx = half_span / segments_per_rafter

    if roof_type == "hip":
        hip_inset = half_span
        rafter_z_min = hip_inset
        rafter_z_max = depth - hip_inset
    else:
        rafter_z_min = 0
        rafter_z_max = depth

    for side_name, x_start, x_dir in [("left", 0, 1), ("right", width, -1)]:
        for ri in range(num_rafters_per_side):
            rz = ri * RAFTER_SPACING
            if rz > depth:
                break

            # Skip rafters in hip zones (replaced by jack rafters)
            if roof_type == "hip" and (rz < rafter_z_min or rz > rafter_z_max):
                continue

            for si in range(segments_per_rafter):
                t = (si + 0.5) / segments_per_rafter
                sx = x_start + x_dir * t * half_span
                sy = base_y + t * ridge_height - rafter_depth / 2

                elements.append(Element(
                    element_type=ElementType.RAFTER,
                    material_name="softwood_c24",
                    x=sx, y=sy, z=rz,
                    length=seg_dx + 0.02,
                    width=RAFTER_WIDTH,
                    height=rafter_depth,
                    parent=f"{parent}_rafter_{side_name}_{ri}",
                ))

    # ── HIP ZONE JACK RAFTERS (shorter, in the hip triangles) ──
    if roof_type == "hip":
        for end_name, end_z, z_dir in [("front", 0, 1), ("rear", depth, -1)]:
            num_jacks = max(2, int(hip_inset / RAFTER_SPACING))
            for ji in range(1, num_jacks):
                t_jack = ji / num_jacks
                jack_z = end_z + z_dir * t_jack * hip_inset
                jack_max_rise = t_jack  # Jack rafters are shorter

                for side_name, x_start, x_dir in [("left", 0, 1), ("right", width, -1)]:
                    for si in range(int(segments_per_rafter * jack_max_rise)):
                        t = (si + 0.5) / segments_per_rafter
                        if t > jack_max_rise:
                            break
                        sx = x_start + x_dir * t * half_span
                        sy = base_y + t * ridge_height - rafter_depth / 2

                        elements.append(Element(
                            element_type=ElementType.RAFTER,
                            material_name="softwood_c24",
                            x=sx, y=sy, z=jack_z,
                            length=seg_dx + 0.02,
                            width=RAFTER_WIDTH,
                            height=rafter_depth,
                            parent=f"{parent}_jack_{end_name}_{side_name}_{ji}",
                        ))

    # ── CEILING JOISTS (tie the rafter feet together) ──
    for cj in range(num_rafters_per_side):
        cz = cj * RAFTER_SPACING
        if cz > depth:
            break
        elements.append(Element(
            element_type=ElementType.TIE_BEAM,
            material_name="softwood_c16",
            x=width / 2, y=base_y + CEILING_JOIST_H / 2, z=cz,
            length=width, width=CEILING_JOIST_W, height=CEILING_JOIST_H,
            parent=f"{parent}_ceiling_joist_{cj}",
        ))

    # ── HIP RAFTERS (for hip roof) ──
    if roof_type == "hip":
        hip_length = math.hypot(half_span, half_span / math.cos(pitch_rad) * math.sin(pitch_rad))
        hip_depth = rafter_depth * 1.5  # Hip rafters are deeper

        # Hip rafters as thin segments stepping diagonally
        inset = min(half_span, depth / 2)
        for corner_name, (corner_x, corner_z, ridge_z) in {
            "sw": (0, 0, inset),
            "se": (width, 0, inset),
            "nw": (0, depth, depth - inset),
            "ne": (width, depth, depth - inset),
        }.items():
            hip_segs = 5
            for si in range(hip_segs):
                t = (si + 0.5) / hip_segs
                hx = corner_x + t * (width / 2 - corner_x)
                hz = corner_z + t * (ridge_z - corner_z)
                hy = base_y + t * ridge_height - rafter_depth / 2

                seg_x = abs(width / 2 - corner_x) / hip_segs + 0.02
                seg_z = abs(ridge_z - corner_z) / hip_segs + 0.02

                elements.append(Element(
                    element_type=ElementType.RAFTER,
                    material_name="softwood_c24",
                    x=hx, y=hy, z=hz,
                    length=seg_x, width=seg_z,
                    height=rafter_depth * 1.5,  # Hips are deeper
                    parent=f"{parent}_hip_{corner_name}",
                ))

    # ── BATTENS (horizontal strips, tiles/slates nail to these) ──
    if covering == "slate":
        batten_gauge = SLATE_BATTEN_GAUGE
        tile_dims = SLATE_600x300
    elif covering == "plain_tile":
        batten_gauge = TILE_BATTEN_GAUGE
        tile_dims = PLAIN_TILE
    else:
        batten_gauge = 0.340  # Pantile gauge
        tile_dims = PANTILE

    num_battens = int(rafter_length / batten_gauge) + 1

    # For hip roof, battens follow the hip line (shorter at higher rows)
    hip_inset_z = half_span if roof_type == "hip" else 0

    for side_name, x_start, x_dir in [("left", 0, 1), ("right", width, -1)]:
        for bi in range(num_battens):
            t = bi / max(1, num_battens) * 0.95
            bx = x_start + x_dir * t * half_span
            by = base_y + t * ridge_height

            # Batten Z span follows hip line
            z_start = t * hip_inset_z
            z_end = depth - t * hip_inset_z
            batten_span = max(0.3, z_end - z_start)
            batten_cz = (z_start + z_end) / 2

            elements.append(Element(
                element_type=ElementType.STUD,
                material_name="softwood_c16",
                x=bx, y=by, z=batten_cz,
                length=BATTEN_W, width=batten_span, height=BATTEN_H,
                parent=f"{parent}_batten_{side_name}_{bi}",
            ))

    # ── TILES/SLATES ──
    # UNIFIED coverage: each row spans z = t*hip_inset to D - t*hip_inset
    # This covers the ENTIRE roof surface in one pass — no gaps.
    tile_l, tile_w, tile_t = tile_dims

    for side_name, x_start, x_dir in [("left", 0, 1), ("right", width, -1)]:
        for row in range(num_battens):
            t = row / max(1, num_battens) * 0.92
            row_x = x_start + x_dir * t * half_span
            row_y = base_y + t * ridge_height

            # Row Z limits follow hip diagonal
            z_start = t * hip_inset_z
            z_end = depth - t * hip_inset_z
            row_span = z_end - z_start
            if row_span < tile_w:
                break

            num_tiles_row = max(1, int(row_span / tile_w))
            for ti in range(num_tiles_row):
                tz = z_start + (ti + 0.5) * row_span / num_tiles_row

                mat = "roofing_slate" if covering == "slate" else "clay_roof_tile"
                elements.append(Element(
                    element_type=ElementType.SLATE if covering == "slate" else ElementType.TILE,
                    material_name=mat,
                    x=row_x, y=row_y, z=tz,
                    length=tile_w, width=tile_w, height=tile_t,
                    parent=f"{parent}_tile_{side_name}_{row}_{ti}",
                ))

    # ── FRONT AND REAR HIP SLOPE SLATES ──
    # These are the two triangular slopes at each end of a hip roof.
    # Each row runs across X (the building width) at a Z position
    # that advances from the end wall toward the ridge endpoint.
    # The row width narrows as it approaches the ridge (triangle shape).
    if roof_type == "hip":
        hip_slope_rows = max(4, int(half_span / batten_gauge))

        for end_name, end_z, z_dir in [("front", 0, 1), ("rear", depth, -1)]:
            for row in range(hip_slope_rows):
                t = (row + 0.5) / hip_slope_rows * 0.92
                row_z = end_z + z_dir * t * half_span
                row_y = base_y + t * ridge_height

                # Row width narrows from full building width to zero
                row_width = width * (1.0 - t)
                if row_width < tile_w:
                    break

                row_cx = width / 2
                num_tiles_row = max(1, int(row_width / tile_w))

                for ti in range(num_tiles_row):
                    tx = row_cx - row_width / 2 + (ti + 0.5) * row_width / num_tiles_row

                    mat = "roofing_slate" if covering == "slate" else "clay_roof_tile"
                    elements.append(Element(
                        element_type=ElementType.SLATE if covering == "slate" else ElementType.TILE,
                        material_name=mat,
                        x=tx, y=row_y, z=row_z,
                        length=tile_w, width=tile_w, height=tile_t,
                        parent=f"{parent}_hip_tile_{end_name}_{row}_{ti}",
                    ))

    # ── RIDGE TILES (only along the ridge, between hip endpoints) ──
    if roof_type == "hip":
        ridge_z_start = half_span
        ridge_z_end = depth - half_span
    else:
        ridge_z_start = 0
        ridge_z_end = depth

    ridge_span = max(0.1, ridge_z_end - ridge_z_start)
    num_ridge_tiles = max(1, int(ridge_span / RIDGE_TILE_L))
    for rti in range(num_ridge_tiles):
        rtz = ridge_z_start + (rti + 0.5) * ridge_span / num_ridge_tiles
        elements.append(Element(
            element_type=ElementType.TILE,
            material_name="clay_roof_tile",
            x=width / 2, y=ridge_y + RIDGE_TILE_H / 2, z=rtz,
            length=RIDGE_TILE_W, width=RIDGE_TILE_L, height=RIDGE_TILE_H,
            parent=f"{parent}_ridge_tile_{rti}",
        ))

    # ── HIP RIDGE TILES (along the 4 hip lines from corners to ridge) ──
    if roof_type == "hip":
        inset = half_span
        for corner_name, (cx, cz, rz) in {
            "sw": (0, 0, inset),
            "se": (width, 0, inset),
            "nw": (0, depth, depth - inset),
            "ne": (width, depth, depth - inset),
        }.items():
            hip_len = math.sqrt(half_span**2 + inset**2 + ridge_height**2)
            num_hip_tiles = int(hip_len / RIDGE_TILE_L)
            for hti in range(num_hip_tiles):
                t = (hti + 0.5) / max(1, num_hip_tiles)
                hx = cx + t * (width / 2 - cx)
                hy = base_y + t * ridge_height + RIDGE_TILE_H / 2
                hz = cz + t * (rz - cz)
                elements.append(Element(
                    element_type=ElementType.TILE,
                    material_name="clay_roof_tile",
                    x=hx, y=hy, z=hz,
                    length=RIDGE_TILE_W, width=RIDGE_TILE_W, height=RIDGE_TILE_H,
                    parent=f"{parent}_hip_ridge_{corner_name}_{hti}",
                ))

    # ── LEAD FLASHINGS (at abutments) ──
    # Ridge flashing (runs along Z)
    elements.append(Element(
        element_type=ElementType.PLASTER,
        material_name="wrought_iron",
        x=width / 2, y=ridge_y, z=depth / 2,
        length=0.300, width=depth, height=LEAD_T,  # Swapped: runs along Z
        parent=f"{parent}_ridge_flashing",
    ))

    return elements


def _select_rafter_depth(rafter_length: float) -> float:
    """Select rafter depth from span tables.

    C16 timber, 400mm centres, slate covering (~0.8 kN/m²).
    """
    if rafter_length <= 2.0:
        return 0.100
    elif rafter_length <= 2.5:
        return 0.125
    elif rafter_length <= 3.0:
        return 0.150
    elif rafter_length <= 3.75:
        return 0.175
    elif rafter_length <= 4.5:
        return 0.200
    else:
        return 0.225
