"""Detailed floor and ceiling construction at component level.

Every individual element of a floor/ceiling assembly:

Georgian/Victorian timber floor:
- Joists: structural beams spanning between walls
- Strutting: herringbone or solid strutting between joists
- Wall plates: timber beams on wall tops where joists bear
- Floorboards: tongue-and-groove boards nailed to joists
- Ceiling laths: thin timber strips nailed to joist undersides
- Plaster: 3-coat lime plaster on laths (hair-reinforced)
- Skirting boards: profiled timber at wall/floor junction
- Nails: cut nails fixing boards to joists

Ground floor options:
- Suspended timber (joists on sleeper walls over void)
- Solid (flagstones on earth, or later concrete)

Dimensions from BS 5268, BS EN 1995, and measured Georgian examples.
"""

from __future__ import annotations

import math

from .elements import Element, ElementType


# ── Joist dimensions (BS EN 1995 / span tables) ──────────────────

JOIST_WIDTHS = [0.038, 0.047, 0.050, 0.063, 0.075]  # Standard widths (m)
JOIST_DEPTHS = [0.100, 0.125, 0.150, 0.175, 0.200, 0.225, 0.250, 0.300]
JOIST_SPACINGS = [0.400, 0.450, 0.600]  # Centres (m)

# ── Floorboard dimensions ────────────────────────────────────────

# Tongue-and-groove softwood boards
BOARD_WIDTHS = [0.100, 0.125, 0.150, 0.175]  # Face width (m)
BOARD_T_TG = 0.022     # 22mm T&G boards (standard)
BOARD_T_SQUARE = 0.025  # 25mm square-edge boards (Georgian)

# ── Ceiling construction ─────────────────────────────────────────

LATH_W = 0.025          # 25mm lath width
LATH_T = 0.006          # 6mm lath thickness
LATH_GAP = 0.008        # 8mm gap between laths (key for plaster)
LATH_LENGTH = 1.200     # 1200mm (4ft) standard lath length

PLASTER_COATS = 3       # Render, floating, setting coats
PLASTER_T = 0.015       # 15mm total plaster thickness
PLASTER_HAIR_COAT_T = 0.008  # 8mm scratch/render coat (with hair)
PLASTER_FLOAT_T = 0.005      # 5mm floating coat
PLASTER_SET_T = 0.002        # 2mm setting/finish coat

# ── Strutting ─────────────────────────────────────────────────────

HERRINGBONE_W = 0.038   # 38mm herringbone strut width
HERRINGBONE_D = 0.038   # 38mm depth
SOLID_STRUT_T = 0.038   # 38mm solid blocking thickness

# ── Skirting and architrave ───────────────────────────────────────

SKIRTING_H = 0.175      # 175mm Georgian skirting height (tall!)
SKIRTING_T = 0.019      # 19mm thickness
ARCHITRAVE_W = 0.075    # 75mm architrave width around doors
ARCHITRAVE_T = 0.019    # 19mm thickness

# ── Nails ─────────────────────────────────────────────────────────

CUT_NAIL_L = 0.065      # 65mm cut nail (floor to joist)
CUT_NAIL_D = 0.004      # 4mm diameter
LATH_NAIL_L = 0.032     # 32mm lath nail
NAILS_PER_BOARD_END = 2  # 2 nails per board at each joist


def build_detailed_floor(
    width: float,
    depth: float,
    floor_y: float,
    max_span: float,
    floor_idx: int,
    board_width: float = 0.150,
    joist_spacing: float = 0.400,
    is_ground_floor: bool = False,
    parent: str = "",
) -> list[Element]:
    """Build a complete floor assembly with every component.

    Components from top to bottom:
    1. Floorboards (T&G softwood, 22mm)
    2. Joists (structural, spanning shorter dimension)
    3. Herringbone strutting (mid-span bracing between joists)
    4. Ceiling laths (nailed to underside of joists)
    5. Lime plaster (3-coat on laths)
    6. Skirting boards (around perimeter)
    """
    elements = []

    # ── Size the joists based on span ──
    joist_depth = _select_joist_depth(max_span, joist_spacing)
    joist_width = 0.047  # 47mm standard

    # Joists span the shorter dimension
    if width <= depth:
        joist_span = width
        joist_dir = "x"  # Joists run along X
        num_joists = int(depth / joist_spacing) + 1
    else:
        joist_span = depth
        joist_dir = "z"  # Joists run along Z
        num_joists = int(width / joist_spacing) + 1

    # ── WALL PLATES (timber on top of walls, joists sit on these) ──
    if joist_dir == "x":
        # Wall plates on north and south walls
        for wz, name in [(0, "south"), (depth, "north")]:
            elements.append(Element(
                element_type=ElementType.WALL_PLATE,
                material_name="softwood_c24",
                x=width / 2, y=floor_y, z=wz,
                length=width, width=0.100, height=0.075,
                parent=f"{parent}_wallplate_{name}",
                floor_index=floor_idx,
            ))
    else:
        for wx, name in [(0, "west"), (width, "east")]:
            elements.append(Element(
                element_type=ElementType.WALL_PLATE,
                material_name="softwood_c24",
                x=wx, y=floor_y, z=depth / 2,
                length=0.100, width=depth, height=0.075,  # Swap: runs along Z
                parent=f"{parent}_wallplate_{name}",
                floor_index=floor_idx,
            ))

    # ── JOISTS ──
    joist_y = floor_y + 0.075 + joist_depth / 2  # Sits on wall plate

    # Calculate loads on each joist
    # Dead load: boards + plaster ceiling = ~0.8 kN/m²
    # Live load: 1.5 kN/m² (residential)
    # UDL on joist = (dead + live) * spacing
    w_udl = (0.8 + 1.5) * joist_spacing  # kN/m
    max_moment = w_udl * joist_span ** 2 / 8  # kN·m
    max_shear = w_udl * joist_span / 2  # kN
    # Deflection check: 5wL⁴/(384EI)
    # I = bh³/12

    for j in range(num_joists):
        if joist_dir == "x":
            jx = width / 2
            jz = j * joist_spacing
            if jz > depth:
                break
            # Joist runs along X: length=span, width=joist_width
            el_l, el_w = joist_span, joist_width
        else:
            jx = j * joist_spacing
            jz = depth / 2
            if jx > width:
                break
            # Joist runs along Z: swap length and width
            el_l, el_w = joist_width, joist_span

        elements.append(Element(
            element_type=ElementType.JOIST,
            material_name="softwood_c24",
            x=jx, y=joist_y, z=jz,
            length=el_l, width=el_w, height=joist_depth,
            parent=f"{parent}_joist_{j}",
            floor_index=floor_idx,
            bending_moment=max_moment,
            shear=max_shear,
        ))

    # ── HERRINGBONE STRUTTING (at mid-span, between joists) ──
    if joist_span > 2.5:
        strut_positions = [0.5]  # Mid-span
        if joist_span > 4.0:
            strut_positions = [0.33, 0.67]  # Third points for long spans

        for t in strut_positions:
            for j in range(num_joists - 1):
                if joist_dir == "x":
                    sx = width * t
                    sz = (j + 0.5) * joist_spacing
                    if sz > depth:
                        break
                else:
                    sx = (j + 0.5) * joist_spacing
                    sz = depth * t
                    if sx > width:
                        break

                # Two diagonal struts per bay (herringbone pattern)
                for diag in [-1, 1]:
                    elements.append(Element(
                        element_type=ElementType.STUD,
                        material_name="softwood_c16",
                        x=sx, y=joist_y, z=sz,
                        length=joist_spacing * 1.2,  # Diagonal length
                        width=HERRINGBONE_W, height=HERRINGBONE_D,
                        rotation=45 * diag,
                        parent=f"{parent}_strutting",
                        floor_index=floor_idx,
                    ))

    # ── FLOORBOARDS ──
    board_y = joist_y + joist_depth / 2 + BOARD_T_TG / 2

    if joist_dir == "x":
        # Boards run perpendicular to joists (along Z)
        # Each board: narrow in X (board_width), long in Z (depth)
        num_boards = int(width / board_width) + 1
        for b in range(num_boards):
            bx = b * board_width + board_width / 2
            if bx > width:
                break
            elements.append(Element(
                element_type=ElementType.FLOORBOARD,
                material_name="softwood_c16",
                x=bx, y=board_y, z=depth / 2,
                length=board_width, width=depth, height=BOARD_T_TG,
                parent=f"{parent}_board_{b}",
                floor_index=floor_idx,
            ))
    else:
        # Boards run along X (perpendicular to Z-spanning joists)
        num_boards = int(depth / board_width) + 1
        for b in range(num_boards):
            bz = b * board_width + board_width / 2
            if bz > depth:
                break
            elements.append(Element(
                element_type=ElementType.FLOORBOARD,
                material_name="softwood_c16",
                x=width / 2, y=board_y, z=bz,
                length=width, width=board_width, height=BOARD_T_TG,
                parent=f"{parent}_board_{b}",
                floor_index=floor_idx,
            ))

    # ── NAILS (fixing boards to joists) ──
    boards_placed = min(num_boards, int(width / board_width) + 1) if joist_dir == "x" else min(num_boards, int(depth / board_width) + 1)
    total_nails = boards_placed * num_joists * NAILS_PER_BOARD_END

    # Represent nails as a batch (individual nails would be millions)
    elements.append(Element(
        element_type=ElementType.NAIL,
        material_name="wrought_iron",
        x=width / 2, y=board_y, z=depth / 2,
        length=CUT_NAIL_L, width=CUT_NAIL_D, height=CUT_NAIL_D,
        parent=f"{parent}_floor_nails",
        floor_index=floor_idx,
    ))

    # ── CEILING (laths + plaster on underside of joists above) ──
    if floor_idx > 0 or not is_ground_floor:
        ceiling_elements = _build_ceiling(
            width, depth, floor_y - PLASTER_T,
            joist_dir, num_joists, joist_spacing,
            floor_idx, f"{parent}_ceiling",
        )
        elements.extend(ceiling_elements)

    # ── SKIRTING BOARDS (around perimeter) ──
    skirting_y = board_y + BOARD_T_TG / 2 + SKIRTING_H / 2
    # South/north skirting runs along X, east/west along Z
    for name, (sx, sz, sl_x, sl_z) in {
        "south": (width / 2, 0, width, SKIRTING_T),
        "north": (width / 2, depth, width, SKIRTING_T),
        "east": (width, depth / 2, SKIRTING_T, depth),
        "west": (0, depth / 2, SKIRTING_T, depth),
    }.items():
        elements.append(Element(
            element_type=ElementType.PLASTER,
            material_name="softwood_c16",
            x=sx, y=skirting_y, z=sz,
            length=sl_x, width=sl_z, height=SKIRTING_H,
            parent=f"{parent}_skirting_{name}",
            floor_index=floor_idx,
        ))

    return elements


def _build_ceiling(
    width, depth, ceiling_y,
    joist_dir, num_joists, joist_spacing,
    floor_idx, parent,
):
    """Build lath-and-plaster ceiling."""
    elements = []

    # ── LATHS (thin timber strips nailed across joists) ──
    # Laths run perpendicular to joists
    lath_pitch = LATH_W + LATH_GAP  # 33mm pitch

    if joist_dir == "x":
        # Laths run along Z (perpendicular to X-spanning joists)
        # Actually laths run PARALLEL to joists in traditional construction
        # so they run along X here. Each lath spans across several joist bays.
        num_laths = int(depth / lath_pitch)
        for li in range(num_laths):
            lz = li * lath_pitch + LATH_W / 2
            if lz > depth:
                break
            elements.append(Element(
                element_type=ElementType.CEILING_LATH,
                material_name="softwood_c16",
                x=width / 2, y=ceiling_y, z=lz,
                length=min(width, LATH_LENGTH),
                width=LATH_W, height=LATH_T,
                parent=f"{parent}_lath_{li}",
                floor_index=floor_idx,
            ))
    else:
        # Laths run along X (perpendicular to Z-spanning joists)
        num_laths = int(width / lath_pitch)
        for li in range(num_laths):
            lx = li * lath_pitch + LATH_W / 2
            if lx > width:
                break
            # Lath runs along Z — swap length/width
            elements.append(Element(
                element_type=ElementType.CEILING_LATH,
                material_name="softwood_c16",
                x=lx, y=ceiling_y, z=depth / 2,
                length=LATH_W, width=min(depth, LATH_LENGTH),
                height=LATH_T,
                parent=f"{parent}_lath_{li}",
                floor_index=floor_idx,
            ))

    # ── PLASTER (3-coat lime plaster) ──
    # Scratch coat (with horsehair reinforcement)
    elements.append(Element(
        element_type=ElementType.PLASTER,
        material_name="lime_plaster",
        x=width / 2, y=ceiling_y - LATH_T - PLASTER_HAIR_COAT_T / 2,
        z=depth / 2,
        length=width, width=depth, height=PLASTER_HAIR_COAT_T,
        parent=f"{parent}_plaster_scratch",
        floor_index=floor_idx,
    ))

    # Floating coat
    elements.append(Element(
        element_type=ElementType.PLASTER,
        material_name="lime_plaster",
        x=width / 2,
        y=ceiling_y - LATH_T - PLASTER_HAIR_COAT_T - PLASTER_FLOAT_T / 2,
        z=depth / 2,
        length=width, width=depth, height=PLASTER_FLOAT_T,
        parent=f"{parent}_plaster_float",
        floor_index=floor_idx,
    ))

    # Setting coat (fine lime putty finish)
    elements.append(Element(
        element_type=ElementType.PLASTER,
        material_name="lime_plaster",
        x=width / 2,
        y=ceiling_y - LATH_T - PLASTER_HAIR_COAT_T - PLASTER_FLOAT_T - PLASTER_SET_T / 2,
        z=depth / 2,
        length=width, width=depth, height=PLASTER_SET_T,
        parent=f"{parent}_plaster_setting",
        floor_index=floor_idx,
    ))

    return elements


def _select_joist_depth(span: float, spacing: float) -> float:
    """Select joist depth from span tables.

    Based on BS EN 1995 / TRADA span tables for C24 timber at
    residential loading (1.5 kN/m² imposed).

    Span table (C24, 400mm centres, 1.5 kN/m²):
        Span ≤ 2.5m: 47x150
        Span ≤ 3.2m: 47x175
        Span ≤ 3.9m: 47x200
        Span ≤ 4.5m: 47x225
        Span ≤ 5.0m: 47x250
        Span > 5.0m: 47x300 or double up
    """
    # Adjust for non-standard spacing
    factor = spacing / 0.400

    effective_span = span * (factor ** 0.5)

    if effective_span <= 2.5:
        return 0.150
    elif effective_span <= 3.2:
        return 0.175
    elif effective_span <= 3.9:
        return 0.200
    elif effective_span <= 4.5:
        return 0.225
    elif effective_span <= 5.0:
        return 0.250
    else:
        return 0.300
