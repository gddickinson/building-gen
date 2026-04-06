"""Plumbing system construction.

Models the complete plumbing system:

Drainage (waste going out):
- Soil stack: 110mm vertical pipe, carries WC waste to drain
- Waste pipes: 40mm (basin/bath) or 50mm (sink) horizontal runs
- Traps: U-bend under each fixture (water seal prevents gas)
- Underground drain: 110mm pipe to public sewer

Water supply (clean water coming in):
- Rising main: 15mm copper pipe from street
- Cold water storage tank (in roof space for older buildings)
- Distribution pipes: 15mm (hot/cold) to each fixture
- Hot water cylinder (airing cupboard)

Rules (Building Regulations Part H / BS EN 12056):
- Soil stack must extend 900mm above any window within 3m
- WC must connect to soil stack (not waste pipe)
- Maximum horizontal waste pipe runs: 1.7m for 32mm, 3.0m for 40mm
- Minimum gradient: 1:40 for 110mm soil, 1:20 for 40mm waste
- Traps: 75mm seal for WC, 50mm for others
- Soil stack should be internal or external on back wall
- Bathrooms/WCs should stack vertically to share the soil stack

Dimensions from BS EN 12056, Building Regs Part H.
"""

from __future__ import annotations

from .elements import Element, ElementType


# ── Pipe dimensions ───────────────────────────────────────────────

SOIL_STACK_DIA = 0.110    # 110mm soil stack (WC waste)
WASTE_40_DIA = 0.040      # 40mm waste pipe (basin, bath)
WASTE_50_DIA = 0.050      # 50mm waste pipe (kitchen sink)
SUPPLY_15_DIA = 0.015     # 15mm supply pipe (hot/cold)
SUPPLY_22_DIA = 0.022     # 22mm supply pipe (main feeds)
RISING_MAIN_DIA = 0.022   # 22mm rising main from street

# ── Fixture connection requirements ───────────────────────────────

FIXTURE_WASTE = {
    "toilet": SOIL_STACK_DIA,    # Must connect to soil stack
    "bath": WASTE_40_DIA,
    "shower": WASTE_40_DIA,
    "basin": WASTE_40_DIA,
    "sink": WASTE_50_DIA,        # Kitchen sink is 50mm
    "washing_machine": WASTE_40_DIA,
    "dishwasher": WASTE_40_DIA,
}

FIXTURE_SUPPLY = {
    "toilet": [("cold", SUPPLY_15_DIA)],
    "bath": [("hot", SUPPLY_15_DIA), ("cold", SUPPLY_15_DIA)],
    "shower": [("hot", SUPPLY_15_DIA), ("cold", SUPPLY_15_DIA)],
    "basin": [("hot", SUPPLY_15_DIA), ("cold", SUPPLY_15_DIA)],
    "sink": [("hot", SUPPLY_15_DIA), ("cold", SUPPLY_15_DIA)],
    "washing_machine": [("cold", SUPPLY_15_DIA)],
    "boiler": [("cold", SUPPLY_22_DIA)],
}

# Trap depths (water seal)
TRAP_DEPTHS = {
    "toilet": 0.075,     # 75mm seal
    "bath": 0.050,       # 50mm seal
    "shower": 0.050,
    "basin": 0.050,
    "sink": 0.050,
}

# Maximum horizontal waste pipe run (metres)
MAX_WASTE_RUN = {
    WASTE_40_DIA: 3.0,
    WASTE_50_DIA: 4.0,
    SOIL_STACK_DIA: 6.0,
}


def build_plumbing_system(
    soil_stack_x: float,
    soil_stack_z: float,
    base_y: float,
    num_floors: int,
    floor_height: float,
    roof_height: float,
    fixtures_per_floor: list[list[dict]],
    parent: str = "plumbing",
) -> list[Element]:
    """Build the complete plumbing system.

    Args:
        soil_stack_x, soil_stack_z: Position of the main soil stack
        base_y: Ground floor level
        num_floors: Number of floors
        floor_height: Height per floor
        roof_height: Height above top floor to roof peak
        fixtures_per_floor: List of fixture dicts per floor, each with
            {"type": "toilet", "x": 5.0, "z": 8.0, "floor": 0}

    Returns:
        List of Element objects for all plumbing components.
    """
    elements = []

    total_height = num_floors * floor_height + roof_height

    # ── SOIL STACK (vertical, full height + 900mm above roof) ──
    stack_top = total_height + 0.900  # 900mm above highest point
    stack_height = stack_top + 0.600  # Below ground to above roof

    elements.append(Element(
        element_type=ElementType.COLUMN,  # Using column for pipe
        material_name="cast_iron",
        x=soil_stack_x, y=base_y + stack_height / 2 - 0.6,
        z=soil_stack_z,
        length=SOIL_STACK_DIA, width=SOIL_STACK_DIA,
        height=stack_height,
        parent=f"{parent}_soil_stack",
    ))

    # ── UNDERGROUND DRAIN (from soil stack base to boundary) ──
    elements.append(Element(
        element_type=ElementType.BEAM,  # Using beam for horizontal pipe
        material_name="engineering_brick",  # Vitrified clay pipe
        x=soil_stack_x / 2, y=base_y - 0.600,
        z=soil_stack_z,
        length=soil_stack_x, width=SOIL_STACK_DIA,
        height=SOIL_STACK_DIA,
        parent=f"{parent}_drain",
    ))

    # ── RISING MAIN (cold water supply from street) ──
    elements.append(Element(
        element_type=ElementType.COLUMN,
        material_name="wrought_iron",  # Copper pipe, using iron as proxy
        x=soil_stack_x - 0.300, y=base_y + num_floors * floor_height / 2,
        z=soil_stack_z,
        length=RISING_MAIN_DIA, width=RISING_MAIN_DIA,
        height=num_floors * floor_height,
        parent=f"{parent}_rising_main",
    ))

    # ── FIXTURE CONNECTIONS (per floor) ──
    for floor_idx, fixtures in enumerate(fixtures_per_floor):
        fy = base_y + floor_idx * floor_height

        for fix in fixtures:
            fix_type = fix.get("type", "basin")
            fx = fix.get("x", soil_stack_x)
            fz = fix.get("z", soil_stack_z)

            # Waste pipe from fixture to soil stack
            waste_dia = FIXTURE_WASTE.get(fix_type, WASTE_40_DIA)
            waste_run = ((fx - soil_stack_x) ** 2 + (fz - soil_stack_z) ** 2) ** 0.5

            if waste_run > 0.1:
                # Horizontal waste pipe
                mid_x = (fx + soil_stack_x) / 2
                mid_z = (fz + soil_stack_z) / 2

                elements.append(Element(
                    element_type=ElementType.BEAM,
                    material_name="cast_iron",
                    x=mid_x, y=fy + 0.100, z=mid_z,
                    length=waste_run, width=waste_dia, height=waste_dia,
                    parent=f"{parent}_waste_{floor_idx}_{fix_type}",
                    floor_index=floor_idx,
                ))

            # Trap under the fixture
            trap_depth = TRAP_DEPTHS.get(fix_type, 0.050)
            elements.append(Element(
                element_type=ElementType.BEAM,
                material_name="cast_iron",
                x=fx, y=fy + 0.050, z=fz,
                length=waste_dia * 2, width=waste_dia,
                height=trap_depth,
                parent=f"{parent}_trap_{floor_idx}_{fix_type}",
                floor_index=floor_idx,
            ))

            # Supply pipes (hot and cold)
            supplies = FIXTURE_SUPPLY.get(fix_type, [])
            for si, (temp, pipe_dia) in enumerate(supplies):
                supply_run = waste_run  # Roughly same path

                if supply_run > 0.1:
                    offset = 0.050 * (si + 1)  # Offset hot/cold
                    elements.append(Element(
                        element_type=ElementType.BEAM,
                        material_name="wrought_iron",
                        x=(fx + soil_stack_x) / 2,
                        y=fy + floor_height - 0.200 - offset,
                        z=(fz + soil_stack_z) / 2,
                        length=supply_run, width=pipe_dia, height=pipe_dia,
                        parent=f"{parent}_supply_{temp}_{floor_idx}_{fix_type}",
                        floor_index=floor_idx,
                    ))

    # ── HOT WATER CYLINDER (usually on first floor, airing cupboard) ──
    elements.append(Element(
        element_type=ElementType.COLUMN,
        material_name="wrought_iron",  # Copper cylinder
        x=soil_stack_x - 0.400, y=base_y + floor_height + 0.600,
        z=soil_stack_z - 0.300,
        length=0.450, width=0.450, height=1.200,
        parent=f"{parent}_hot_water_cylinder",
        floor_index=1,
    ))

    return elements
