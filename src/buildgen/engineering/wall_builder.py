"""Detailed wall construction generator.

Builds walls at the individual component level, supporting:
- Solid brick walls (stretcher, Flemish, English bond)
- Cavity walls (inner leaf + cavity + outer leaf)
- Stone masonry walls (ashlar, rubble, coursed rubble)
- Timber frame walls (studs, sole plate, head plate, bracing)
- Composite walls with render/plaster finishes

Each wall knows its construction type, thickness, and the position
of every individual brick/block/stone/stud within it.
"""

from __future__ import annotations

import math

from .elements import Element, ElementType, ElementCollection
from .materials.properties import MATERIALS_DB

# ── UK Standard Dimensions ────────────────────────────────────────

# Standard metric brick (BS EN 771-1)
BRICK_L = 0.215    # 215mm length
BRICK_W = 0.1025   # 102.5mm width (half-brick = single leaf)
BRICK_H = 0.065    # 65mm height
MORTAR_J = 0.010   # 10mm mortar joint
COURSE_H = BRICK_H + MORTAR_J  # 75mm per course

# Concrete block (BS EN 771-3)
BLOCK_L = 0.440    # 440mm length
BLOCK_W = 0.100    # 100mm width (inner leaf)
BLOCK_H = 0.215    # 215mm height
BLOCK_COURSE_H = BLOCK_H + MORTAR_J  # 225mm per course

# Stone masonry
ASHLAR_L = 0.400   # Typical dressed stone length
ASHLAR_H = 0.200   # Typical course height
ASHLAR_W = 0.300   # Typical depth

# Cavity wall
CAVITY_WIDTH = 0.050   # 50mm (can be 75mm or 100mm)
WALL_TIE_SPACING_H = 0.900   # 900mm horizontal
WALL_TIE_SPACING_V = 0.450   # 450mm vertical

# Timber frame
STUD_W = 0.038     # 38mm (or 47mm)
STUD_D = 0.089     # 89mm (or 140mm for external)
STUD_SPACING = 0.400  # 400mm centres

# DPC
DPC_THICKNESS = 0.003  # Polythene DPC
DPC_HEIGHT = 0.150     # 150mm above ground level


def build_solid_brick_wall(
    x1: float, z1: float, x2: float, z2: float,
    base_y: float, wall_height: float,
    bond: str = "flemish",
    thickness_bricks: int = 2,  # 1 = half-brick, 2 = one-brick, 3 = 1.5-brick
    brick_material: str = "facing_brick",
    mortar_material: str = "mortar_lime",
    load_per_m: float = 0.0,
    floor_idx: int = 0,
    parent: str = "",
) -> list[Element]:
    """Build a solid brick wall laying every individual brick.

    Args:
        x1, z1, x2, z2: Wall start and end points in plan
        base_y: Height of wall base
        wall_height: Height of wall
        bond: "stretcher", "flemish", or "english"
        thickness_bricks: Number of brick widths (1=102.5mm, 2=215mm, 3=327.5mm)
        brick_material: Material for bricks
        mortar_material: Material for mortar joints
        load_per_m: Vertical load in kN/m at base
        floor_idx: Floor index
        parent: Parent identifier

    Returns:
        List of Element objects (bricks + mortar joints)
    """
    elements = []

    wall_dx = x2 - x1
    wall_dz = z2 - z1
    wall_length = math.hypot(wall_dx, wall_dz)
    if wall_length < 0.1:
        return elements

    # Direction along wall and perpendicular (into wall)
    dir_x = wall_dx / wall_length
    dir_z = wall_dz / wall_length
    norm_x = -dir_z  # Perpendicular (wall thickness direction)
    norm_z = dir_x

    rotation = math.degrees(math.atan2(dir_z, dir_x))
    wall_thickness = thickness_bricks * BRICK_W + (thickness_bricks - 1) * MORTAR_J

    num_courses = int(wall_height / COURSE_H)

    for course in range(num_courses):
        y = base_y + course * COURSE_H + BRICK_H / 2

        # Load diminishes from bottom to top
        courses_above = num_courses - course - 1
        load_factor = courses_above / num_courses if num_courses > 0 else 0
        brick_load = load_per_m * (BRICK_L + MORTAR_J) * load_factor

        # DPC course (usually 2 courses above ground)
        if course == 2 and base_y < 0.01:
            # Use actual X and Z extents (no rotation needed)
            dpc_lx = abs(wall_dx) if abs(wall_dx) > 0.1 else wall_thickness
            dpc_lz = abs(wall_dz) if abs(wall_dz) > 0.1 else wall_thickness
            elements.append(Element(
                element_type=ElementType.PLASTER,
                material_name="engineering_brick",
                x=(x1 + x2) / 2, y=y, z=(z1 + z2) / 2,
                length=dpc_lx, width=dpc_lz, height=0.003,
                parent=parent + "_dpc",
                floor_index=floor_idx,
            ))

        if bond == "flemish":
            _lay_flemish_course(
                elements, course, x1, z1, dir_x, dir_z, norm_x, norm_z,
                wall_length, thickness_bricks, y, rotation,
                brick_material, mortar_material, brick_load,
                floor_idx, parent,
            )
        elif bond == "english":
            _lay_english_course(
                elements, course, x1, z1, dir_x, dir_z, norm_x, norm_z,
                wall_length, thickness_bricks, y, rotation,
                brick_material, mortar_material, brick_load,
                floor_idx, parent,
            )
        else:
            _lay_stretcher_course(
                elements, course, x1, z1, dir_x, dir_z, norm_x, norm_z,
                wall_length, thickness_bricks, y, rotation,
                brick_material, mortar_material, brick_load,
                floor_idx, parent,
            )

    return elements


def build_cavity_wall(
    x1: float, z1: float, x2: float, z2: float,
    base_y: float, wall_height: float,
    outer_material: str = "facing_brick",
    inner_material: str = "common_brick",
    cavity_width: float = CAVITY_WIDTH,
    insulated: bool = False,
    load_per_m: float = 0.0,
    floor_idx: int = 0,
    parent: str = "",
) -> list[Element]:
    """Build a cavity wall with inner and outer leaves.

    Cavity wall construction:
    - Outer leaf: half-brick (102.5mm) facing brick
    - Cavity: 50-100mm air gap (optionally insulated)
    - Inner leaf: half-brick or concrete block (100mm)
    - Wall ties at standard spacing connecting leaves

    Total thickness: 102.5 + 50 + 100 = 252.5mm minimum
    """
    elements = []

    wall_dx = x2 - x1
    wall_dz = z2 - z1
    wall_length = math.hypot(wall_dx, wall_dz)
    if wall_length < 0.1:
        return elements

    dir_x = wall_dx / wall_length
    dir_z = wall_dz / wall_length
    norm_x = -dir_z
    norm_z = dir_x

    # Outer leaf offset (towards outside)
    outer_offset = (BRICK_W + cavity_width + BLOCK_W) / 2 - BRICK_W / 2
    inner_offset = -(BRICK_W + cavity_width + BLOCK_W) / 2 + BLOCK_W / 2

    # Outer leaf (facing brick, stretcher bond)
    outer_x1 = x1 + norm_x * outer_offset
    outer_z1 = z1 + norm_z * outer_offset
    outer_x2 = x2 + norm_x * outer_offset
    outer_z2 = z2 + norm_z * outer_offset

    outer_elems = build_solid_brick_wall(
        outer_x1, outer_z1, outer_x2, outer_z2,
        base_y, wall_height,
        bond="stretcher", thickness_bricks=1,
        brick_material=outer_material,
        load_per_m=load_per_m * 0.3,  # Outer leaf takes ~30% of load
        floor_idx=floor_idx, parent=parent + "_outer",
    )
    elements.extend(outer_elems)

    # Inner leaf (blocks or brick)
    inner_x1 = x1 + norm_x * inner_offset
    inner_z1 = z1 + norm_z * inner_offset
    inner_x2 = x2 + norm_x * inner_offset
    inner_z2 = z2 + norm_z * inner_offset

    inner_elems = _build_block_leaf(
        inner_x1, inner_z1, inner_x2, inner_z2,
        base_y, wall_height,
        inner_material,
        load_per_m=load_per_m * 0.7,  # Inner leaf takes ~70%
        floor_idx=floor_idx, parent=parent + "_inner",
    )
    elements.extend(inner_elems)

    # Wall ties
    rotation = math.degrees(math.atan2(dir_z, dir_x))
    num_ties_h = int(wall_length / WALL_TIE_SPACING_H)
    num_ties_v = int(wall_height / WALL_TIE_SPACING_V)

    for th in range(num_ties_h):
        for tv in range(num_ties_v):
            t = (th + 0.5) / max(1, num_ties_h)
            ty = base_y + (tv + 0.5) * WALL_TIE_SPACING_V
            tx = x1 + t * wall_dx
            tz = z1 + t * wall_dz

            elements.append(Element(
                element_type=ElementType.NAIL,  # Using nail type for ties
                material_name="mild_steel",
                x=tx, y=ty, z=tz,
                length=BRICK_W + cavity_width + BLOCK_W,
                width=0.003, height=0.003,
                rotation=rotation + 90,
                parent=parent + "_ties",
                floor_index=floor_idx,
            ))

    return elements


def build_stone_wall(
    x1: float, z1: float, x2: float, z2: float,
    base_y: float, wall_height: float,
    stone_type: str = "ashlar",
    stone_material: str = "limestone",
    wall_thickness: float = 0.600,
    load_per_m: float = 0.0,
    floor_idx: int = 0,
    parent: str = "",
) -> list[Element]:
    """Build a stone masonry wall.

    Stone types:
    - "ashlar": Regular dressed blocks in even courses
    - "rubble": Irregular stones with thick mortar
    - "coursed_rubble": Roughly shaped stones in approximate courses
    """
    elements = []

    wall_dx = x2 - x1
    wall_dz = z2 - z1
    wall_length = math.hypot(wall_dx, wall_dz)
    if wall_length < 0.1:
        return elements

    dir_x = wall_dx / wall_length
    dir_z = wall_dz / wall_length
    rotation = math.degrees(math.atan2(dir_z, dir_x))

    if stone_type == "ashlar":
        course_h = ASHLAR_H + MORTAR_J
        block_l = ASHLAR_L
    elif stone_type == "coursed_rubble":
        course_h = 0.250  # Rougher courses
        block_l = 0.350   # Varied
    else:  # rubble
        course_h = 0.300
        block_l = 0.300

    num_courses = int(wall_height / course_h)

    for course in range(num_courses):
        y = base_y + course * course_h + (course_h - MORTAR_J) / 2

        offset = (block_l * 0.3) if course % 2 == 1 else 0
        num_blocks = int((wall_length - offset) / (block_l + MORTAR_J))

        courses_above = num_courses - course - 1
        load_factor = courses_above / num_courses if num_courses > 0 else 0
        block_load = load_per_m * (block_l + MORTAR_J) * load_factor

        for b in range(num_blocks):
            t = (offset + b * (block_l + MORTAR_J) + block_l / 2) / wall_length
            if t > 1.0:
                break

            bx = x1 + t * wall_dx
            bz = z1 + t * wall_dz

            elements.append(Element(
                element_type=ElementType.STONE_BLOCK,
                material_name=stone_material,
                x=bx, y=y, z=bz,
                length=block_l, width=wall_thickness, height=course_h - MORTAR_J,
                rotation=rotation,
                parent=parent, floor_index=floor_idx,
                compression=block_load,
            ))

            # Mortar joint
            if course > 0:
                elements.append(Element(
                    element_type=ElementType.MORTAR_JOINT,
                    material_name="mortar_lime",
                    x=bx, y=y - (course_h - MORTAR_J) / 2 - MORTAR_J / 2, z=bz,
                    length=block_l, width=wall_thickness, height=MORTAR_J,
                    rotation=rotation,
                    parent=parent, floor_index=floor_idx,
                ))

    return elements


def _lay_flemish_course(
    elements, course, x1, z1, dir_x, dir_z, norm_x, norm_z,
    wall_length, thickness_bricks, y, rotation,
    brick_mat, mortar_mat, brick_load, floor_idx, parent,
):
    """Lay one course of Flemish bond (alternating stretchers and headers)."""
    offset = (BRICK_L / 2) if course % 2 == 1 else 0
    pos = offset

    is_header = course % 2 == 0  # Start with header on even courses

    while pos < wall_length:
        if is_header and thickness_bricks >= 2:
            # Header brick (turned 90°, shows short face)
            brick_len = BRICK_W
            t = (pos + brick_len / 2) / wall_length
            if t > 1.0:
                break
            bx = x1 + t * dir_x * wall_length
            bz = z1 + t * dir_z * wall_length
            elements.append(Element(
                element_type=ElementType.BRICK, material_name=brick_mat,
                x=bx, y=y, z=bz,
                length=BRICK_W, width=BRICK_L, height=BRICK_H,
                rotation=rotation, parent=parent, floor_index=floor_idx,
                compression=brick_load,
            ))
            pos += brick_len + MORTAR_J
        else:
            # Stretcher brick (shows long face)
            t = (pos + BRICK_L / 2) / wall_length
            if t > 1.0:
                break
            bx = x1 + t * dir_x * wall_length
            bz = z1 + t * dir_z * wall_length
            elements.append(Element(
                element_type=ElementType.BRICK, material_name=brick_mat,
                x=bx, y=y, z=bz,
                length=BRICK_L, width=BRICK_W, height=BRICK_H,
                rotation=rotation, parent=parent, floor_index=floor_idx,
                compression=brick_load,
            ))
            pos += BRICK_L + MORTAR_J

        # Mortar perpend joint
        elements.append(Element(
            element_type=ElementType.MORTAR_JOINT, material_name=mortar_mat,
            x=x1 + (pos / wall_length) * dir_x * wall_length,
            y=y,
            z=z1 + (pos / wall_length) * dir_z * wall_length,
            length=MORTAR_J, width=BRICK_W, height=BRICK_H,
            rotation=rotation, parent=parent, floor_index=floor_idx,
        ))

        is_header = not is_header


def _lay_english_course(
    elements, course, x1, z1, dir_x, dir_z, norm_x, norm_z,
    wall_length, thickness_bricks, y, rotation,
    brick_mat, mortar_mat, brick_load, floor_idx, parent,
):
    """Lay one course of English bond (alternating stretcher/header courses)."""
    is_header_course = course % 2 == 1

    if is_header_course and thickness_bricks >= 2:
        # All headers
        pos = 0
        while pos + BRICK_W < wall_length:
            t = (pos + BRICK_W / 2) / wall_length
            bx = x1 + t * dir_x * wall_length
            bz = z1 + t * dir_z * wall_length
            elements.append(Element(
                element_type=ElementType.BRICK, material_name=brick_mat,
                x=bx, y=y, z=bz,
                length=BRICK_W, width=BRICK_L, height=BRICK_H,
                rotation=rotation, parent=parent, floor_index=floor_idx,
                compression=brick_load,
            ))
            pos += BRICK_W + MORTAR_J
    else:
        # All stretchers
        _lay_stretcher_course(
            elements, course, x1, z1, dir_x, dir_z, norm_x, norm_z,
            wall_length, thickness_bricks, y, rotation,
            brick_mat, mortar_mat, brick_load, floor_idx, parent,
        )


def _lay_stretcher_course(
    elements, course, x1, z1, dir_x, dir_z, norm_x, norm_z,
    wall_length, thickness_bricks, y, rotation,
    brick_mat, mortar_mat, brick_load, floor_idx, parent,
):
    """Lay one course of stretcher bond (all stretchers, offset half-brick)."""
    offset = (BRICK_L / 2 + MORTAR_J / 2) if course % 2 == 1 else 0
    pos = offset

    while pos + BRICK_L <= wall_length + 0.01:
        t = (pos + BRICK_L / 2) / wall_length
        if t > 1.02:
            break
        bx = x1 + min(t, 1.0) * dir_x * wall_length
        bz = z1 + min(t, 1.0) * dir_z * wall_length

        elements.append(Element(
            element_type=ElementType.BRICK, material_name=brick_mat,
            x=bx, y=y, z=bz,
            length=BRICK_L, width=BRICK_W, height=BRICK_H,
            rotation=rotation, parent=parent, floor_index=floor_idx,
            compression=brick_load,
        ))

        # Bed joint (horizontal mortar)
        if course > 0:
            elements.append(Element(
                element_type=ElementType.MORTAR_JOINT, material_name=mortar_mat,
                x=bx, y=y - BRICK_H / 2 - MORTAR_J / 2, z=bz,
                length=BRICK_L, width=BRICK_W, height=MORTAR_J,
                rotation=rotation, parent=parent, floor_index=floor_idx,
            ))

        pos += BRICK_L + MORTAR_J


def _build_block_leaf(
    x1, z1, x2, z2, base_y, wall_height,
    material_name, load_per_m, floor_idx, parent,
):
    """Build an inner leaf of concrete blocks."""
    elements = []
    wall_dx = x2 - x1
    wall_dz = z2 - z1
    wall_length = math.hypot(wall_dx, wall_dz)
    if wall_length < 0.1:
        return elements

    dir_x = wall_dx / wall_length
    dir_z = wall_dz / wall_length
    rotation = math.degrees(math.atan2(dir_z, dir_x))

    num_courses = int(wall_height / BLOCK_COURSE_H)

    for course in range(num_courses):
        y = base_y + course * BLOCK_COURSE_H + BLOCK_H / 2
        offset = (BLOCK_L / 2) if course % 2 == 1 else 0
        num_blocks = int((wall_length - offset) / (BLOCK_L + MORTAR_J))

        courses_above = num_courses - course - 1
        load_factor = courses_above / num_courses if num_courses > 0 else 0
        block_load = load_per_m * (BLOCK_L + MORTAR_J) * load_factor

        for b in range(num_blocks):
            t = (offset + b * (BLOCK_L + MORTAR_J) + BLOCK_L / 2) / wall_length
            if t > 1.0:
                break

            bx = x1 + t * wall_dx
            bz = z1 + t * wall_dz

            elements.append(Element(
                element_type=ElementType.BRICK,  # Reuse brick type for blocks
                material_name=material_name,
                x=bx, y=y, z=bz,
                length=BLOCK_L, width=BLOCK_W, height=BLOCK_H,
                rotation=rotation, parent=parent, floor_index=floor_idx,
                compression=block_load,
            ))

    return elements
