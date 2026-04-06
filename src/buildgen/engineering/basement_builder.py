"""Basement/cellar construction.

Georgian townhouses commonly have basements used as:
- Kitchen and service areas (below street level)
- Wine/beer cellar
- Coal cellar
- Servants' hall

Construction:
- Walls: thicker than above (450-600mm brick or stone)
- Floor: flagstone on compacted earth, or brick paviours
- Ceiling: brick vaulted or timber joists
- Light wells: areas dug out at front to allow windows
- Steps down from ground floor via internal stair or area steps
- Damp proofing: none (Georgian), bitumen (Victorian)

Building Regulations:
- Minimum ceiling height: 2.0m (habitable), 1.8m (storage)
- Ventilation required (air bricks)
- Drainage: sump if below water table
"""

from __future__ import annotations

from .elements import Element, ElementType


# Basement dimensions
BASEMENT_HEIGHT = 2.400       # 2.4m floor to ceiling (Georgian)
BASEMENT_WALL_T = 0.450       # 450mm (thicker than above for earth pressure)
LIGHT_WELL_W = 1.200          # 1.2m light well width
LIGHT_WELL_D = 1.000          # 1.0m depth from street level
FLAG_T = 0.050                # 50mm flagstone thickness
FLAG_W = 0.600                # 600mm square flagstones
AIR_BRICK_W = 0.215           # Standard air brick
AIR_BRICK_H = 0.065
COAL_CHUTE_W = 0.300          # Coal chute opening


def build_basement(
    width: float,
    depth: float,
    basement_height: float = BASEMENT_HEIGHT,
    wall_material: str = "engineering_brick",
    parent: str = "basement",
) -> list[Element]:
    """Build a complete basement/cellar under the building.

    Creates:
    - Basement walls (thicker than above-ground)
    - Flagstone floor
    - Light well at front (for windows)
    - Air bricks for ventilation
    - Internal steps down from ground floor
    """
    elements = []
    base_y = -basement_height  # Below ground level

    # ── BASEMENT WALLS (thicker, engineering brick) ──
    from .wall_builder import build_solid_brick_wall

    for name, x1, z1, x2, z2 in [
        ("south", 0, 0, width, 0),
        ("east", width, 0, width, depth),
        ("north", width, depth, 0, depth),
        ("west", 0, depth, 0, 0),
    ]:
        elems = build_solid_brick_wall(
            x1, z1, x2, z2, base_y, basement_height,
            bond="english",  # English bond for strength (below ground)
            thickness_bricks=2,
            brick_material=wall_material,
            mortar_material="mortar_cement",
            load_per_m=50.0,
            floor_idx=-1,
            parent=f"{parent}_{name}",
        )
        elements.extend(elems)

    # ── FLAGSTONE FLOOR ──
    num_flags_x = int(width / FLAG_W)
    num_flags_z = int(depth / FLAG_W)

    for fx in range(num_flags_x):
        for fz in range(num_flags_z):
            x = fx * FLAG_W + FLAG_W / 2
            z = fz * FLAG_W + FLAG_W / 2
            if x > width or z > depth:
                continue

            elements.append(Element(
                element_type=ElementType.STONE_BLOCK,
                material_name="limestone",
                x=x, y=base_y + FLAG_T / 2, z=z,
                length=FLAG_W - 0.005,
                width=FLAG_W - 0.005,
                height=FLAG_T,
                parent=f"{parent}_floor",
                floor_index=-1,
            ))

    # ── LIGHT WELL (excavation at front for basement windows) ──
    # Retaining walls of the light well
    well_x1 = width * 0.2
    well_x2 = width * 0.45
    for wx, wz, wl, wd in [
        (well_x1, -LIGHT_WELL_D / 2, 0.225, LIGHT_WELL_D),  # Left wall
        (well_x2, -LIGHT_WELL_D / 2, 0.225, LIGHT_WELL_D),  # Right wall
        ((well_x1 + well_x2) / 2, -LIGHT_WELL_D, well_x2 - well_x1, 0.225),  # Front
    ]:
        elements.append(Element(
            element_type=ElementType.BRICK,
            material_name=wall_material,
            x=wx, y=base_y + basement_height / 2, z=wz,
            length=wl, width=wd, height=basement_height,
            parent=f"{parent}_lightwell",
            floor_index=-1,
        ))

    # Light well window
    elements.append(Element(
        element_type=ElementType.WINDOW_FRAME,
        material_name="softwood_c16",
        x=(well_x1 + well_x2) / 2,
        y=base_y + basement_height * 0.65,
        z=0,
        length=well_x2 - well_x1 - 0.200,
        width=0.050, height=0.600,
        parent=f"{parent}_lightwell_window",
        floor_index=-1,
    ))
    elements.append(Element(
        element_type=ElementType.GLASS_PANE,
        material_name="float_glass",
        x=(well_x1 + well_x2) / 2,
        y=base_y + basement_height * 0.65,
        z=0,
        length=well_x2 - well_x1 - 0.260,
        width=0.003, height=0.540,
        parent=f"{parent}_lightwell_window",
        floor_index=-1,
    ))

    # ── AIR BRICKS (ventilation, at top of basement walls) ──
    air_y = base_y + basement_height - AIR_BRICK_H / 2 - 0.075  # Just below DPC
    for name, wall_len, x_start, z_pos, along_x in [
        ("south", width, 0, 0, True),
        ("north", width, 0, depth, True),
    ]:
        num_airbricks = max(2, int(wall_len / 2.0))
        for ai in range(num_airbricks):
            ax = x_start + (ai + 0.5) * wall_len / num_airbricks if along_x else x_start
            az = z_pos

            elements.append(Element(
                element_type=ElementType.BRICK,
                material_name="engineering_brick",
                x=ax, y=air_y, z=az,
                length=AIR_BRICK_W, width=BASEMENT_WALL_T * 0.5,
                height=AIR_BRICK_H,
                parent=f"{parent}_airbrick",
                floor_index=-1,
            ))

    # ── INTERNAL STEPS (from ground floor down to basement) ──
    from .stair_builder import build_detailed_staircase

    stair_elems = build_detailed_staircase(
        x=width * 0.35, z=depth * 0.4,
        base_y=base_y,
        total_rise=basement_height,
        stair_width=0.76,  # Narrower service stair
        stair_depth=2.0,
        direction="z",
        stair_type="straight",
        parent=f"{parent}_stairs",
        floor_idx=-1,
    )
    elements.extend(stair_elems)

    # ── COAL CELLAR CHUTE (cast iron frame in pavement) ──
    elements.append(Element(
        element_type=ElementType.DOOR_FRAME,
        material_name="cast_iron",
        x=width * 0.8, y=-0.025, z=-0.100,
        length=COAL_CHUTE_W, width=COAL_CHUTE_W, height=0.050,
        parent=f"{parent}_coal_chute",
        floor_index=-1,
    ))

    return elements
