"""Interior partition walls (non-load-bearing).

Partitions divide rooms within the structural envelope.
They carry no load from above — only their own weight.

Georgian partitions:
- Timber stud frame: 75x50mm studs at 400mm centres
- Lath and plaster both sides: 25mm laths + 15mm plaster each side
- Total thickness: ~100-120mm
- Sole plate (bottom) and head plate (top)
- Noggings (horizontal bracing between studs)

Partition walls should align with room boundaries from the floor plan.
They do NOT need foundations or lintels (not load-bearing),
but door openings need a timber lintel/head piece.
"""

from __future__ import annotations

import math

from .elements import Element, ElementType


STUD_W = 0.050          # 50mm stud width
STUD_D = 0.075          # 75mm stud depth (partition thickness)
STUD_SPACING = 0.400    # 400mm centres
PLATE_W = 0.075         # Sole/head plate width
PLATE_H = 0.050         # Sole/head plate height
NOGGING_W = 0.050       # Nogging width
NOGGING_H = 0.050       # Nogging height
LATH_T = 0.006          # 6mm lath
PLASTER_T = 0.015       # 15mm plaster each side

# Total partition thickness = stud + 2*(lath+plaster) = 75+2*(6+15) = 117mm


def build_partition_wall(
    x1: float, z1: float, x2: float, z2: float,
    base_y: float, wall_height: float,
    has_door: bool = False,
    door_width: float = 0.760,
    door_height: float = 2.000,
    door_position: float = 0.5,
    floor_idx: int = 0,
    parent: str = "partition",
) -> list[Element]:
    """Build a non-load-bearing timber stud partition wall.

    Creates individual studs, plates, noggings, and plaster.

    Args:
        x1, z1, x2, z2: Wall endpoints in plan
        base_y: Wall base height
        wall_height: Wall height (typically floor_height - slab)
        has_door: Whether to include a door opening
        door_width: Door opening width
        door_height: Door opening height
        door_position: 0.0-1.0, position along wall for door
    """
    elements = []

    wall_dx = x2 - x1
    wall_dz = z2 - z1
    wall_length = math.hypot(wall_dx, wall_dz)
    if wall_length < 0.3:
        return elements

    dir_x = wall_dx / wall_length
    dir_z = wall_dz / wall_length
    rotation = math.degrees(math.atan2(dir_z, dir_x))

    # ── SOLE PLATE (bottom horizontal timber) ──
    elements.append(Element(
        element_type=ElementType.SOLE_PLATE,
        material_name="softwood_c16",
        x=(x1 + x2) / 2, y=base_y + PLATE_H / 2, z=(z1 + z2) / 2,
        length=wall_length, width=STUD_D, height=PLATE_H,
        rotation=rotation, parent=f"{parent}_sole",
        floor_index=floor_idx,
    ))

    # ── HEAD PLATE (top horizontal timber) ──
    elements.append(Element(
        element_type=ElementType.HEAD_PLATE,
        material_name="softwood_c16",
        x=(x1 + x2) / 2,
        y=base_y + wall_height - PLATE_H / 2,
        z=(z1 + z2) / 2,
        length=wall_length, width=STUD_D, height=PLATE_H,
        rotation=rotation, parent=f"{parent}_head",
        floor_index=floor_idx,
    ))

    # ── STUDS (vertical timbers) ──
    num_studs = int(wall_length / STUD_SPACING) + 1
    stud_height = wall_height - PLATE_H * 2

    # Door opening position and bounds
    if has_door:
        door_centre = wall_length * door_position
        door_left = door_centre - door_width / 2
        door_right = door_centre + door_width / 2
    else:
        door_left = -1
        door_right = -1

    for si in range(num_studs):
        stud_pos = si * STUD_SPACING
        if stud_pos > wall_length:
            break

        t = stud_pos / wall_length
        sx = x1 + t * wall_dx
        sz = z1 + t * wall_dz

        # Skip studs in door opening (but add cripple studs above)
        if has_door and door_left < stud_pos < door_right:
            # Cripple stud above door
            cripple_h = wall_height - PLATE_H * 2 - door_height
            if cripple_h > 0.1:
                elements.append(Element(
                    element_type=ElementType.STUD,
                    material_name="softwood_c16",
                    x=sx,
                    y=base_y + door_height + PLATE_H + cripple_h / 2,
                    z=sz,
                    length=STUD_W, width=STUD_D, height=cripple_h,
                    rotation=rotation, parent=f"{parent}_cripple",
                    floor_index=floor_idx,
                ))
            continue

        # Full-height stud
        elements.append(Element(
            element_type=ElementType.STUD,
            material_name="softwood_c16",
            x=sx, y=base_y + PLATE_H + stud_height / 2, z=sz,
            length=STUD_W, width=STUD_D, height=stud_height,
            rotation=rotation, parent=f"{parent}_stud_{si}",
            floor_index=floor_idx,
        ))

    # ── DOOR HEAD (lintel over door opening) ──
    if has_door:
        dt = door_centre / wall_length
        dx = x1 + dt * wall_dx
        dz = z1 + dt * wall_dz

        elements.append(Element(
            element_type=ElementType.LINTEL,
            material_name="softwood_c16",
            x=dx,
            y=base_y + door_height + PLATE_H + 0.025,
            z=dz,
            length=door_width + 0.100,  # 50mm bearing each side
            width=STUD_D, height=0.050,
            rotation=rotation, parent=f"{parent}_door_head",
            floor_index=floor_idx,
        ))

    # ── NOGGINGS (horizontal bracing at mid-height) ──
    nogging_y = base_y + wall_height / 2
    for si in range(num_studs - 1):
        t = (si + 0.5) * STUD_SPACING / wall_length
        if t > 1.0:
            break
        nx = x1 + t * wall_dx
        nz = z1 + t * wall_dz

        elements.append(Element(
            element_type=ElementType.STUD,
            material_name="softwood_c16",
            x=nx, y=nogging_y, z=nz,
            length=STUD_SPACING - STUD_W, width=STUD_D, height=NOGGING_H,
            rotation=rotation, parent=f"{parent}_nogging",
            floor_index=floor_idx,
        ))

    # ── PLASTER (both sides of the partition) ──
    total_plaster_t = LATH_T + PLASTER_T

    for side_name, offset_sign in [("front", 1), ("back", -1)]:
        # Simplified: one panel per side
        elements.append(Element(
            element_type=ElementType.PLASTER,
            material_name="lime_plaster",
            x=(x1 + x2) / 2,
            y=base_y + wall_height / 2,
            z=(z1 + z2) / 2,
            length=wall_length, width=total_plaster_t,
            height=wall_height,
            rotation=rotation, parent=f"{parent}_plaster_{side_name}",
            floor_index=floor_idx,
        ))

    return elements
