"""Chimney and fireplace construction at component level.

Georgian chimney construction:
- Fireplace opening: ~900mm wide x 750mm high x 400mm deep
- Chimney breast: 900-1200mm wide, 300-450mm deep projection into room
- Flue: 225x225mm (9"x9") clay liner or 185mm diameter
- Chimney stack: rises above roof, minimum 1m above ridge within 600mm
- Multiple flues gathered into one stack on party/end walls
- Chimney pot: clay pot on top of each flue

Each fireplace needs:
- Fireback (fire-resistant lining)
- Hearth (non-combustible floor area in front)
- Lintel/arch over opening
- Throat (narrowing above fire)
- Smoke shelf and damper
- Flue (straight or angled run to stack)

Dimensions from Approved Document J, BS EN 15287, and measured examples.
"""

from __future__ import annotations

import math

from .elements import Element, ElementType


# ── Fireplace dimensions (Approved Document J) ───────────────────

OPENING_W = 0.900       # 900mm fireplace opening width
OPENING_H = 0.750       # 750mm opening height
OPENING_D = 0.400       # 400mm firebox depth

BREAST_W = 1.050        # 1050mm chimney breast width
BREAST_D = 0.350        # 350mm breast projection into room

HEARTH_W = 1.200        # 1200mm hearth width (150mm each side of opening)
HEARTH_D = 0.500        # 500mm hearth projection from breast
HEARTH_T = 0.050        # 50mm hearth thickness (non-combustible)

LINTEL_W = OPENING_W + 0.200   # 200mm bearing
LINTEL_H = 0.150        # 150mm lintel depth

# ── Flue dimensions ──────────────────────────────────────────────

FLUE_W = 0.225          # 225mm square flue (9"x9")
FLUE_LINER_T = 0.015    # 15mm clay liner thickness
FLUE_MIN_HEIGHT = 4.5   # 4.5m minimum flue height for draught

# ── Chimney stack ─────────────────────────────────────────────────

STACK_W = 0.450          # 450mm stack width (for single flue)
STACK_D = 0.450          # 450mm stack depth
STACK_MIN_ABOVE_RIDGE = 0.600  # 600mm above roof slope intersection (Approved Document J)
STACK_COURSES_ABOVE = 8  # ~8 brick courses above roof line

POT_DIAMETER = 0.200     # 200mm clay chimney pot
POT_HEIGHT = 0.450       # 450mm pot height

# ── Fuel types and flue requirements ──────────────────────────────

FUEL_FLUE_SIZES = {
    "coal": (0.225, 0.225),    # 225x225mm minimum
    "wood": (0.200, 0.200),    # 200x200mm for wood-burning
    "gas": (0.125, 0.125),     # 125mm diameter (can be smaller)
    "oil": (0.150, 0.150),     # 150mm minimum
}


def build_chimney_stack(
    cx: float, cz: float,
    base_y: float,
    num_floors: int,
    floor_height: float,
    roof_ridge_height: float,
    fuel_type: str = "coal",
    num_flues: int = 2,
    wall_side: str = "east",
    parent: str = "chimney",
) -> list[Element]:
    """Build a complete chimney stack with fireplaces on each floor.

    Creates:
    - Fireplace opening + hearth on each floor
    - Chimney breast running vertically through the building
    - Flue liners (one per fireplace, gathered into stack)
    - Chimney stack above roof with pots

    Args:
        cx, cz: Centre position in plan
        base_y: Height of ground floor
        num_floors: Number of floors with fireplaces
        floor_height: Height per floor
        roof_ridge_height: Height of roof ridge above base
        fuel_type: "coal", "wood", "gas", "oil"
        num_flues: Number of flues in the stack
        wall_side: Which wall the chimney is on
    """
    elements = []

    flue_w, flue_d = FUEL_FLUE_SIZES.get(fuel_type, (0.225, 0.225))
    # roof_ridge_height is the height of the ridge ABOVE the eaves
    # (NOT the absolute height from ground — that would double count floors)
    eaves_height = num_floors * floor_height + base_y
    total_height = eaves_height + roof_ridge_height

    # ── CHIMNEY BREAST (runs full height of building) ──
    # The breast is a rectangular brick column built into the wall
    breast_height = num_floors * floor_height

    elements.append(Element(
        element_type=ElementType.BRICK,
        material_name="engineering_brick",
        x=cx, y=base_y + breast_height / 2, z=cz,
        length=BREAST_W, width=BREAST_D, height=breast_height,
        parent=f"{parent}_breast",
    ))

    # ── FIREPLACES (one per floor) ──
    for floor in range(num_floors):
        fy = floor * floor_height + base_y
        fp_elements = _build_fireplace(
            cx, cz, fy, fuel_type, floor, parent,
        )
        elements.extend(fp_elements)

    # ── FLUE LINERS (clay tubes running up through the breast) ──
    for fi in range(min(num_flues, num_floors)):
        # Offset each flue slightly within the breast
        flue_offset = (fi - (num_flues - 1) / 2) * (flue_w + 0.030)

        flue_base = (fi + 1) * floor_height + base_y  # Starts above fireplace
        flue_top = total_height + STACK_MIN_ABOVE_RIDGE

        elements.append(Element(
            element_type=ElementType.BRICK,  # Clay liner
            material_name="engineering_brick",
            x=cx + flue_offset, y=(flue_base + flue_top) / 2, z=cz,
            length=flue_w, width=flue_d, height=flue_top - flue_base,
            parent=f"{parent}_flue_{fi}",
        ))

    # ── CHIMNEY STACK (above roof, brickwork around flues) ──
    stack_base = num_floors * floor_height + base_y
    stack_top = total_height + STACK_MIN_ABOVE_RIDGE
    stack_w = STACK_W + (num_flues - 1) * (flue_w + 0.030)

    # Stack brickwork
    elements.append(Element(
        element_type=ElementType.BRICK,
        material_name="facing_brick",
        x=cx, y=(stack_base + stack_top) / 2, z=cz,
        length=stack_w, width=STACK_D, height=stack_top - stack_base,
        parent=f"{parent}_stack",
    ))

    # ── CHIMNEY POTS (one per flue) ──
    for fi in range(num_flues):
        flue_offset = (fi - (num_flues - 1) / 2) * (flue_w + 0.030)
        elements.append(Element(
            element_type=ElementType.BRICK,  # Clay pot
            material_name="clay_roof_tile",
            x=cx + flue_offset, y=stack_top + POT_HEIGHT / 2, z=cz,
            length=POT_DIAMETER, width=POT_DIAMETER, height=POT_HEIGHT,
            parent=f"{parent}_pot_{fi}",
        ))

    return elements


def _build_fireplace(
    cx: float, cz: float,
    floor_y: float,
    fuel_type: str,
    floor_idx: int,
    parent: str,
) -> list[Element]:
    """Build a single fireplace with hearth, opening, and lintel."""
    elements = []

    # Hearth (stone slab on the floor in front of the fireplace)
    elements.append(Element(
        element_type=ElementType.STONE_BLOCK,
        material_name="limestone",
        x=cx, y=floor_y + HEARTH_T / 2, z=cz + BREAST_D / 2 + HEARTH_D / 2,
        length=HEARTH_W, width=HEARTH_D, height=HEARTH_T,
        parent=f"{parent}_hearth_f{floor_idx}",
        floor_index=floor_idx,
    ))

    # Fireback (fire-resistant brick lining inside the opening)
    elements.append(Element(
        element_type=ElementType.BRICK,
        material_name="engineering_brick",
        x=cx, y=floor_y + OPENING_H / 2, z=cz - OPENING_D / 2,
        length=OPENING_W - 0.100, width=0.060, height=OPENING_H,
        parent=f"{parent}_fireback_f{floor_idx}",
        floor_index=floor_idx,
    ))

    # Lintel over the opening (stone or iron)
    elements.append(Element(
        element_type=ElementType.LINTEL,
        material_name="cast_iron" if fuel_type == "coal" else "oak",
        x=cx, y=floor_y + OPENING_H + LINTEL_H / 2, z=cz,
        length=LINTEL_W, width=BREAST_D, height=LINTEL_H,
        parent=f"{parent}_lintel_f{floor_idx}",
        floor_index=floor_idx,
    ))

    # Mantelpiece / surround (decorative)
    # Mantel shelf
    elements.append(Element(
        element_type=ElementType.STONE_BLOCK,
        material_name="limestone",
        x=cx,
        y=floor_y + OPENING_H + LINTEL_H + 0.030,
        z=cz + BREAST_D / 2,
        length=OPENING_W + 0.300, width=0.200, height=0.060,
        parent=f"{parent}_mantel_f{floor_idx}",
        floor_index=floor_idx,
    ))

    # Mantel legs (pilasters either side)
    for side in [-1, 1]:
        mx = cx + side * (OPENING_W / 2 + 0.050)
        elements.append(Element(
            element_type=ElementType.STONE_BLOCK,
            material_name="limestone",
            x=mx, y=floor_y + OPENING_H / 2, z=cz + BREAST_D / 2,
            length=0.080, width=0.060, height=OPENING_H,
            parent=f"{parent}_mantel_leg_f{floor_idx}",
            floor_index=floor_idx,
        ))

    return elements
