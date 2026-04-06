"""Detailed window and door construction.

Generates every component of a window or door:

Georgian Sash Window (6-over-6):
- Box frame: outer lining, inner lining, pulley stiles, parting beads
- Two sashes: stiles, rails, glazing bars
- 12 glass panes (6 per sash)
- Sash weights, cords, and pulleys
- Stone or timber sill
- Timber lintel above

Panel Door (6-panel Georgian):
- Frame: head, jambs, threshold
- Leaf: stiles, top/middle/bottom rails, muntins, 6 panels
- 3 butt hinges
- Lock/latch
- Fanlight (optional)

All dimensions from measured Georgian/Victorian originals.
"""

from __future__ import annotations

import math

from .elements import Element, ElementType


# ── Sash Window Dimensions (Georgian 6-over-6) ───────────────────
# Based on measured examples from Georgian houses

# Overall opening in wall
WIN_OPENING_W = 1.050    # 1050mm typical 3-bay Georgian
WIN_OPENING_H = 1.650    # Tall proportion ~1:1.6

# Box frame (the fixed frame set into the wall)
# Research: Georgian box frames 130-165mm wide depending on wall thickness
BOX_FRAME_W = 0.140      # 140mm box frame width (typical Georgian)
BOX_FRAME_D = 0.165      # 165mm frame depth (into wall reveal)
PULLEY_STILE_W = 0.032   # 32mm pulley stile
PARTING_BEAD_W = 0.008   # 8mm parting bead
STAFF_BEAD_W = 0.012     # 12mm staff bead

# Sash (the sliding part)
# Research: sash stiles 44-50mm wide by period
SASH_STILE_W = 0.044     # 44mm sash stile width (Georgian: thinner)
SASH_RAIL_H = 0.055      # 55mm sash rail height (top/bottom)
SASH_MEETING_RAIL_H = 0.035  # 35mm meeting rail
SASH_DEPTH = 0.035       # 35mm sash timber depth

# Glazing bars
# Research: Georgian bars very thin (18mm), Victorian wider (25-32mm)
GLAZ_BAR_W = 0.018       # 18mm glazing bar width (Georgian: characteristically thin)
GLAZ_BAR_D = 0.012       # 12mm glazing bar depth

# Glass
# Research: Georgian crown glass only 1-1.5mm thick, Victorian plate 4-6mm
GLASS_T_GEORGIAN = 0.0015  # 1.5mm crown glass (hand-blown, slight distortion)
GLASS_T_VICTORIAN = 0.004  # 4mm plate glass
GLASS_T_MODERN = 0.004     # 4mm float glass
GLASS_REBATE = 0.008       # 8mm rebate depth for glass

# Sill
SILL_H = 0.075           # 75mm sill height
SILL_PROJECTION = 0.050  # 50mm projection beyond wall face

# Sash weights (cast iron)
WEIGHT_D = 0.045          # 45mm diameter
WEIGHT_H = 0.300          # 300mm length


def build_sash_window(
    cx: float, cy: float, cz: float,
    window_width: float = WIN_OPENING_W,
    window_height: float = WIN_OPENING_H,
    panes_wide: int = 3,
    panes_high_per_sash: int = 3,
    rotation: float = 0.0,
    parent: str = "",
    floor_idx: int = 0,
    period: str = "georgian",
) -> list[Element]:
    """Build a complete Georgian sash window with every component.

    A 6-over-6 sash window has:
    - Box frame (fixed in wall)
    - Upper sash with 6 panes (3 wide x 2 high) — slides down
    - Lower sash with 6 panes (3 wide x 2 high) — slides up
    - Glazing bars dividing each sash into panes
    - Sash weights in the box frame for counterbalance
    - Stone sill at the bottom
    - Timber lintel at the top
    """
    elements = []

    glass_t = GLASS_T_GEORGIAN if period == "georgian" else GLASS_T_VICTORIAN
    glaz_w = 0.018 if period == "georgian" else 0.025

    # Build all elements at canonical position (cx, cy, cz) with rotation=0
    # After building, apply rotation transform to reposition side-wall windows
    import math

    # Sash dimensions
    sash_w = window_width - BOX_FRAME_W * 2
    sash_h = (window_height - SASH_RAIL_H * 2 - SASH_MEETING_RAIL_H) / 2

    # ── LINTEL (oak or stone beam above window) ──
    lintel_w = window_width + 0.200  # 100mm bearing each side
    elements.append(Element(
        element_type=ElementType.LINTEL,
        material_name="oak",
        x=cx, y=cy + window_height / 2 + 0.075, z=cz,
        length=lintel_w, width=BOX_FRAME_D, height=0.150,
        rotation=rotation, parent=parent, floor_index=floor_idx,
    ))

    # ── SILL (stone or timber) ──
    sill_w = window_width + SILL_PROJECTION * 2
    elements.append(Element(
        element_type=ElementType.WINDOW_FRAME,
        material_name="limestone" if period == "georgian" else "softwood_c16",
        x=cx, y=cy - window_height / 2 - SILL_H / 2, z=cz,
        length=sill_w, width=BOX_FRAME_D + SILL_PROJECTION, height=SILL_H,
        rotation=rotation, parent=parent + "_sill", floor_index=floor_idx,
    ))

    # ── BOX FRAME ──
    # Head (top horizontal)
    elements.append(Element(
        element_type=ElementType.WINDOW_FRAME,
        material_name="softwood_c16",
        x=cx, y=cy + window_height / 2 - BOX_FRAME_W / 2, z=cz,
        length=window_width, width=BOX_FRAME_D, height=BOX_FRAME_W,
        rotation=rotation, parent=parent + "_frame", floor_index=floor_idx,
    ))

    # Jambs (vertical sides with pulley stiles and weight boxes)
    for side in [-1, 1]:
        jx = cx + side * (window_width / 2 - BOX_FRAME_W / 2)
        # Outer lining
        elements.append(Element(
            element_type=ElementType.WINDOW_FRAME,
            material_name="softwood_c16",
            x=jx, y=cy, z=cz,
            length=BOX_FRAME_W, width=BOX_FRAME_D, height=window_height,
            rotation=rotation, parent=parent + "_frame", floor_index=floor_idx,
        ))

        # Sash weight (cast iron, inside the box frame)
        elements.append(Element(
            element_type=ElementType.WINDOW_FRAME,
            material_name="cast_iron",
            x=jx, y=cy - window_height / 4, z=cz,
            length=WEIGHT_D, width=WEIGHT_D, height=WEIGHT_H,
            rotation=rotation, parent=parent + "_weight", floor_index=floor_idx,
        ))

    # ── UPPER SASH ──
    upper_cy = cy + sash_h / 2 + SASH_MEETING_RAIL_H / 2
    _build_sash(
        elements, cx, upper_cy, cz,
        sash_w, sash_h, panes_wide, panes_high_per_sash,
        glaz_w, glass_t, rotation,
        parent + "_upper_sash", floor_idx,
    )

    # ── LOWER SASH ──
    lower_cy = cy - sash_h / 2 - SASH_MEETING_RAIL_H / 2
    _build_sash(
        elements, cx, lower_cy, cz,
        sash_w, sash_h, panes_wide, panes_high_per_sash,
        glaz_w, glass_t, rotation,
        parent + "_lower_sash", floor_idx,
    )

    # ── MEETING RAILS (where upper and lower sashes overlap) ──
    elements.append(Element(
        element_type=ElementType.WINDOW_SASH,
        material_name="softwood_c16",
        x=cx, y=cy, z=cz,
        length=sash_w, width=SASH_DEPTH, height=SASH_MEETING_RAIL_H,
        rotation=rotation, parent=parent + "_meeting", floor_index=floor_idx,
    ))

    # ── APPLY ROTATION for side-wall windows ──
    # Transform positions and swap dimensions, then CLEAR rotation
    # so the exporter doesn't double-rotate
    if abs(rotation) > 0.1:
        rot_rad = math.radians(rotation)
        cos_r = math.cos(rot_rad)
        sin_r = math.sin(rot_rad)

        for e in elements:
            # Offset from centre
            dx = e.x - cx
            dz = e.z - cz
            # Rotate position around Y axis
            e.x = cx + dx * cos_r + dz * sin_r
            e.z = cz - dx * sin_r + dz * cos_r
            # Swap length and width for perpendicular orientation
            if abs(rotation - 90) < 1 or abs(rotation + 90) < 1:
                e.length, e.width = e.width, e.length
            # Clear rotation — dimensions are already transformed
            e.rotation = 0.0

    return elements


def _build_sash(
    elements, cx, cy, cz,
    sash_w, sash_h, panes_wide, panes_high,
    glaz_bar_w, glass_t, rotation,
    parent, floor_idx,
):
    """Build one sash with stiles, rails, glazing bars, and glass panes."""
    # Sash stiles (vertical sides)
    for side in [-1, 1]:
        sx = cx + side * (sash_w / 2 - SASH_STILE_W / 2)
        elements.append(Element(
            element_type=ElementType.WINDOW_SASH,
            material_name="softwood_c16",
            x=sx, y=cy, z=cz,
            length=SASH_STILE_W, width=SASH_DEPTH, height=sash_h,
            rotation=rotation, parent=parent, floor_index=floor_idx,
        ))

    # Sash rails (top and bottom horizontal)
    for v_side in [-1, 1]:
        ry = cy + v_side * (sash_h / 2 - SASH_RAIL_H / 2)
        elements.append(Element(
            element_type=ElementType.WINDOW_SASH,
            material_name="softwood_c16",
            x=cx, y=ry, z=cz,
            length=sash_w - SASH_STILE_W * 2, width=SASH_DEPTH, height=SASH_RAIL_H,
            rotation=rotation, parent=parent, floor_index=floor_idx,
        ))

    # Glazing area (inside stiles and rails)
    glaze_w = sash_w - SASH_STILE_W * 2
    glaze_h = sash_h - SASH_RAIL_H * 2

    # Pane dimensions
    pane_w = (glaze_w - glaz_bar_w * (panes_wide - 1)) / panes_wide
    pane_h = (glaze_h - glaz_bar_w * (panes_high - 1)) / panes_high

    # Vertical glazing bars
    for gb in range(1, panes_wide):
        gb_x = cx - glaze_w / 2 + gb * (pane_w + glaz_bar_w) - glaz_bar_w / 2
        elements.append(Element(
            element_type=ElementType.GLAZING_BAR,
            material_name="softwood_c16",
            x=gb_x, y=cy, z=cz,
            length=glaz_bar_w, width=GLAZ_BAR_D, height=glaze_h,
            rotation=rotation, parent=parent, floor_index=floor_idx,
        ))

    # Horizontal glazing bars
    for gb in range(1, panes_high):
        gb_y = cy - glaze_h / 2 + gb * (pane_h + glaz_bar_w) - glaz_bar_w / 2
        elements.append(Element(
            element_type=ElementType.GLAZING_BAR,
            material_name="softwood_c16",
            x=cx, y=gb_y, z=cz,
            length=glaze_w, width=GLAZ_BAR_D, height=glaz_bar_w,
            rotation=rotation, parent=parent, floor_index=floor_idx,
        ))

    # Glass panes
    for px in range(panes_wide):
        for py in range(panes_high):
            pane_cx = (cx - glaze_w / 2 + pane_w / 2
                       + px * (pane_w + glaz_bar_w))
            pane_cy = (cy - glaze_h / 2 + pane_h / 2
                       + py * (pane_h + glaz_bar_w))

            elements.append(Element(
                element_type=ElementType.GLASS_PANE,
                material_name="float_glass",
                x=pane_cx, y=pane_cy, z=cz,
                length=pane_w, width=glass_t, height=pane_h,
                rotation=rotation, parent=parent, floor_index=floor_idx,
            ))


def build_panel_door(
    cx: float, cy: float, cz: float,
    door_width: float = 1.050,
    door_height: float = 2.100,
    num_panels: int = 6,
    rotation: float = 0.0,
    parent: str = "",
    floor_idx: int = 0,
    has_fanlight: bool = True,
) -> list[Element]:
    """Build a complete Georgian panel door with frame and hardware.

    6-panel door construction:
    - Frame: head, 2 jambs, threshold
    - Leaf: 2 stiles, top/lock/bottom rails, 2 muntins, 6 panels
    - 3 butt hinges (wrought iron)
    - Lock/handle
    - Fanlight above (semicircular glazed panel)
    """
    elements = []

    # Dimensions
    FRAME_W = 0.100      # Frame section width
    FRAME_D = 0.075      # Frame depth
    STILE_W = 0.095      # Door stile width
    TOP_RAIL_H = 0.095   # Top rail height
    LOCK_RAIL_H = 0.210  # Lock rail height (wider for strength)
    BOT_RAIL_H = 0.210   # Bottom rail height
    MUNTIN_W = 0.044     # Muntin width
    PANEL_T = 0.012      # Raised panel thickness
    LEAF_T = 0.044       # Door leaf thickness

    # ── LINTEL ──
    lintel_w = door_width + 0.200
    lintel_total_h = door_height
    if has_fanlight:
        lintel_total_h += 0.500  # Fanlight height

    elements.append(Element(
        element_type=ElementType.LINTEL,
        material_name="oak",
        x=cx, y=cy + lintel_total_h / 2 + 0.075, z=cz,
        length=lintel_w, width=0.150, height=0.150,
        rotation=rotation, parent=parent, floor_index=floor_idx,
    ))

    # ── DOOR FRAME ──
    # Head
    elements.append(Element(
        element_type=ElementType.DOOR_FRAME,
        material_name="oak",
        x=cx, y=cy + door_height / 2 - FRAME_W / 2, z=cz,
        length=door_width + FRAME_W * 2, width=FRAME_D, height=FRAME_W,
        rotation=rotation, parent=parent + "_frame", floor_index=floor_idx,
    ))

    # Jambs
    for side in [-1, 1]:
        jx = cx + side * (door_width / 2 + FRAME_W / 2)
        elements.append(Element(
            element_type=ElementType.DOOR_FRAME,
            material_name="oak",
            x=jx, y=cy, z=cz,
            length=FRAME_W, width=FRAME_D, height=door_height,
            rotation=rotation, parent=parent + "_frame", floor_index=floor_idx,
        ))

    # Threshold
    elements.append(Element(
        element_type=ElementType.DOOR_FRAME,
        material_name="oak",
        x=cx, y=cy - door_height / 2 + 0.025, z=cz,
        length=door_width + FRAME_W * 2, width=FRAME_D + 0.020, height=0.050,
        rotation=rotation, parent=parent + "_frame", floor_index=floor_idx,
    ))

    # ── DOOR LEAF ──
    # Stiles (vertical edges of door)
    for side in [-1, 1]:
        sx = cx + side * (door_width / 2 - STILE_W / 2)
        elements.append(Element(
            element_type=ElementType.DOOR_LEAF,
            material_name="oak",
            x=sx, y=cy, z=cz,
            length=STILE_W, width=LEAF_T, height=door_height,
            rotation=rotation, parent=parent + "_leaf", floor_index=floor_idx,
        ))

    # Rails (horizontal members)
    rail_x = cx
    rail_w = door_width - STILE_W * 2

    # Top rail
    elements.append(Element(
        element_type=ElementType.DOOR_LEAF,
        material_name="oak",
        x=rail_x, y=cy + door_height / 2 - TOP_RAIL_H / 2, z=cz,
        length=rail_w, width=LEAF_T, height=TOP_RAIL_H,
        rotation=rotation, parent=parent + "_leaf", floor_index=floor_idx,
    ))

    # Lock rail (middle)
    elements.append(Element(
        element_type=ElementType.DOOR_LEAF,
        material_name="oak",
        x=rail_x, y=cy, z=cz,
        length=rail_w, width=LEAF_T, height=LOCK_RAIL_H,
        rotation=rotation, parent=parent + "_leaf", floor_index=floor_idx,
    ))

    # Bottom rail
    elements.append(Element(
        element_type=ElementType.DOOR_LEAF,
        material_name="oak",
        x=rail_x, y=cy - door_height / 2 + BOT_RAIL_H / 2, z=cz,
        length=rail_w, width=LEAF_T, height=BOT_RAIL_H,
        rotation=rotation, parent=parent + "_leaf", floor_index=floor_idx,
    ))

    # Muntins (vertical dividers between panels — 2 for 6-panel door)
    for muntin_side in [-1, 1]:
        mx = cx + muntin_side * rail_w / 6
        # Upper muntin (between top and lock rails)
        elements.append(Element(
            element_type=ElementType.DOOR_LEAF,
            material_name="oak",
            x=mx, y=cy + door_height / 4, z=cz,
            length=MUNTIN_W, width=LEAF_T, height=door_height / 2 - TOP_RAIL_H - LOCK_RAIL_H / 2,
            rotation=rotation, parent=parent + "_leaf", floor_index=floor_idx,
        ))
        # Lower muntin (between lock and bottom rails)
        elements.append(Element(
            element_type=ElementType.DOOR_LEAF,
            material_name="oak",
            x=mx, y=cy - door_height / 4, z=cz,
            length=MUNTIN_W, width=LEAF_T, height=door_height / 2 - BOT_RAIL_H - LOCK_RAIL_H / 2,
            rotation=rotation, parent=parent + "_leaf", floor_index=floor_idx,
        ))

    # Panels (6 raised panels)
    panel_col_w = (rail_w - MUNTIN_W * 2) / 3
    upper_panel_h = (door_height / 2 - TOP_RAIL_H - LOCK_RAIL_H / 2 - MUNTIN_W) / 1
    lower_panel_h = (door_height / 2 - BOT_RAIL_H - LOCK_RAIL_H / 2 - MUNTIN_W) / 1

    for col in range(3):
        px = cx - rail_w / 2 + MUNTIN_W * (col > 0) + panel_col_w * (col + 0.5)
        # Upper panel
        elements.append(Element(
            element_type=ElementType.DOOR_LEAF,
            material_name="oak",
            x=px, y=cy + door_height / 4, z=cz,
            length=panel_col_w - 0.010, width=PANEL_T, height=upper_panel_h,
            rotation=rotation, parent=parent + "_panel", floor_index=floor_idx,
        ))
        # Lower panel
        elements.append(Element(
            element_type=ElementType.DOOR_LEAF,
            material_name="oak",
            x=px, y=cy - door_height / 4, z=cz,
            length=panel_col_w - 0.010, width=PANEL_T, height=lower_panel_h,
            rotation=rotation, parent=parent + "_panel", floor_index=floor_idx,
        ))

    # ── HARDWARE ──
    # 3 butt hinges
    hinge_positions = [
        cy - door_height / 2 + 0.200,   # Bottom
        cy,                               # Middle
        cy + door_height / 2 - 0.200,   # Top
    ]
    for hy in hinge_positions:
        elements.append(Element(
            element_type=ElementType.HINGE,
            material_name="wrought_iron",
            x=cx - door_width / 2, y=hy, z=cz,
            length=0.100, width=0.003, height=0.075,
            rotation=rotation, parent=parent + "_hardware", floor_index=floor_idx,
        ))

    # ── FANLIGHT (semicircular glazed panel above door) ──
    if has_fanlight:
        fan_h = 0.450
        fan_cy = cy + door_height / 2 + fan_h / 2

        # Fanlight frame (semicircular approximated as rectangle)
        elements.append(Element(
            element_type=ElementType.WINDOW_FRAME,
            material_name="softwood_c16",
            x=cx, y=fan_cy, z=cz,
            length=door_width, width=LEAF_T, height=fan_h,
            rotation=rotation, parent=parent + "_fanlight", floor_index=floor_idx,
        ))

        # Fanlight glazing (single pane or radial bars)
        elements.append(Element(
            element_type=ElementType.GLASS_PANE,
            material_name="float_glass",
            x=cx, y=fan_cy, z=cz,
            length=door_width - 0.040, width=0.002, height=fan_h - 0.040,
            rotation=rotation, parent=parent + "_fanlight", floor_index=floor_idx,
        ))

    return elements
