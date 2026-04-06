"""Heating system construction.

Models a complete wet central heating system:

Components:
- Boiler (in kitchen or basement): heats water
- Hot water cylinder (airing cupboard): stores hot water
- Cold water cistern (roof space): feeds the system
- Feed and expansion tank (roof space): accommodates expansion
- Radiators: one per habitable room, sized by room volume
- Flow and return pipes: copper, connecting boiler to radiators
- Pump: circulates water through the system

Pipe sizing (BS EN 12828):
- Main flow/return: 22mm or 28mm copper
- Branch to radiator: 15mm copper
- Radiator valves: lockshield + TRV

Radiator sizing:
- Approximately 40-60 W/m³ room volume (depending on insulation)
- Georgian houses (poor insulation): ~80 W/m³
- Each radiator section ~120W at delta-T 50°C

Historical note: Georgian houses originally heated by fireplaces only.
Central heating retrofitted from ~1960s onwards. For period accuracy,
a Georgian house should have fireplaces; heating system is optional.
"""

from __future__ import annotations

import math

from .elements import Element, ElementType


# ── Boiler ────────────────────────────────────────────────────────

BOILER_W = 0.600         # 600mm wide
BOILER_D = 0.400         # 400mm deep
BOILER_H = 0.850         # 850mm high (wall-hung)
BOILER_FLUE_DIA = 0.100  # 100mm flue

# ── Hot water cylinder ────────────────────────────────────────────

CYLINDER_DIA = 0.450     # 450mm diameter
CYLINDER_H = 1.050       # 1050mm height (140 litre)

# ── Cold water cistern (in roof space) ────────────────────────────

CISTERN_W = 0.600        # 600mm
CISTERN_D = 0.450        # 450mm
CISTERN_H = 0.450        # 450mm (227 litre)

# ── Feed and expansion tank ───────────────────────────────────────

FE_TANK_W = 0.350
FE_TANK_D = 0.250
FE_TANK_H = 0.250

# ── Pipes ─────────────────────────────────────────────────────────

MAIN_PIPE_DIA = 0.022    # 22mm main flow/return
BRANCH_PIPE_DIA = 0.015  # 15mm branch to each radiator
PIPE_WALL_T = 0.001      # 1mm copper pipe wall

# ── Radiators ─────────────────────────────────────────────────────

# Standard panel radiator dimensions
RAD_HEIGHTS = [0.300, 0.450, 0.600, 0.700]  # Standard heights
RAD_DEPTH = 0.065        # 65mm single panel
RAD_SECTION_W = 0.060    # 60mm per section
RAD_BRACKET_H = 0.150    # 150mm above floor

# Output per section at delta-T 50°C
WATTS_PER_SECTION = 120  # Approximate

# Heat loss for Georgian house (poor insulation)
WATTS_PER_M3_GEORGIAN = 80
WATTS_PER_M3_VICTORIAN = 65
WATTS_PER_M3_MODERN = 40

# Rooms that need radiators
HEATED_ROOMS = {
    "parlour", "drawing_room", "dining_room", "kitchen",
    "bedroom", "master_bedroom", "nursery", "study",
    "library", "bathroom", "dressing_room", "entrance_hall",
    "landing", "hallway",
}

# Rooms that DON'T need radiators
UNHEATED_ROOMS = {
    "stairwell", "storage", "pantry", "scullery", "wc",
    "cellar", "attic",
}


def build_heating_system(
    boiler_x: float, boiler_z: float,
    cylinder_x: float, cylinder_z: float,
    base_y: float,
    num_floors: int,
    floor_height: float,
    rooms_per_floor: list[list[dict]],
    building_width: float,
    building_depth: float,
    period: str = "georgian",
    parent: str = "heating",
) -> list[Element]:
    """Build a complete central heating system.

    Args:
        boiler_x, boiler_z: Boiler position (usually kitchen)
        cylinder_x, cylinder_z: Hot water cylinder (usually 1st floor)
        rooms_per_floor: List of room dicts per floor with
            {"name": str, "x": float, "z": float, "width": float, "depth": float}
    """
    elements = []

    watts_per_m3 = {
        "georgian": WATTS_PER_M3_GEORGIAN,
        "victorian": WATTS_PER_M3_VICTORIAN,
    }.get(period, WATTS_PER_M3_MODERN)

    # ── BOILER (in kitchen or basement) ──
    elements.append(Element(
        element_type=ElementType.COLUMN,
        material_name="mild_steel",
        x=boiler_x, y=base_y + BOILER_H / 2 + 0.300, z=boiler_z,
        length=BOILER_W, width=BOILER_D, height=BOILER_H,
        parent=f"{parent}_boiler",
        floor_index=0,
    ))

    # Boiler flue (through wall)
    elements.append(Element(
        element_type=ElementType.COLUMN,
        material_name="mild_steel",
        x=boiler_x, y=base_y + BOILER_H + 0.300, z=boiler_z,
        length=BOILER_FLUE_DIA, width=0.500, height=BOILER_FLUE_DIA,
        parent=f"{parent}_boiler_flue",
        floor_index=0,
    ))

    # ── HOT WATER CYLINDER (usually 1st floor airing cupboard) ──
    elements.append(Element(
        element_type=ElementType.COLUMN,
        material_name="wrought_iron",
        x=cylinder_x, y=base_y + floor_height + CYLINDER_H / 2 + 0.100,
        z=cylinder_z,
        length=CYLINDER_DIA, width=CYLINDER_DIA, height=CYLINDER_H,
        parent=f"{parent}_cylinder",
        floor_index=1,
    ))

    # ── COLD WATER CISTERN (in roof space, sitting on ceiling joists) ──
    roof_y = base_y + num_floors * floor_height
    # Cistern sits just above the top floor ceiling, inside the roof space
    cistern_y = roof_y + 0.15 + CISTERN_H / 2  # Just above the ceiling
    elements.append(Element(
        element_type=ElementType.COLUMN,  # Tank, not foundation
        material_name="mild_steel",
        x=building_width * 0.3,
        y=cistern_y,
        z=building_depth * 0.4,
        length=CISTERN_W, width=CISTERN_D, height=CISTERN_H,
        parent=f"{parent}_cistern",
    ))

    # ── FEED AND EXPANSION TANK (in roof space, next to cistern) ──
    elements.append(Element(
        element_type=ElementType.COLUMN,
        material_name="mild_steel",
        x=building_width * 0.3 + 0.800,
        y=roof_y + 0.15 + FE_TANK_H / 2,
        z=building_depth * 0.4,
        length=FE_TANK_W, width=FE_TANK_D, height=FE_TANK_H,
        parent=f"{parent}_fe_tank",
    ))

    # ── MAIN FLOW AND RETURN PIPES (vertical risers) ──
    total_pipe_height = num_floors * floor_height + 1.0
    for pipe_name, offset in [("flow", -0.050), ("return", 0.050)]:
        elements.append(Element(
            element_type=ElementType.COLUMN,
            material_name="wrought_iron",
            x=boiler_x + offset,
            y=base_y + total_pipe_height / 2,
            z=boiler_z + 0.200,
            length=MAIN_PIPE_DIA, width=MAIN_PIPE_DIA,
            height=total_pipe_height,
            parent=f"{parent}_{pipe_name}_riser",
        ))

    # ── RADIATORS (one per heated room, sized by room volume) ──
    for floor_idx, rooms in enumerate(rooms_per_floor):
        fy = base_y + floor_idx * floor_height

        for room in rooms:
            room_name = room.get("name", "")
            room_type = room.get("type", room_name)
            rx = room.get("x", 0)
            rz = room.get("z", 0)
            rw = room.get("width", 3.0)
            rd = room.get("depth", 3.0)

            if room_type in UNHEATED_ROOMS:
                continue
            if room_type not in HEATED_ROOMS:
                continue

            # Size the radiator
            room_volume = rw * rd * (floor_height - 0.25)
            watts_needed = room_volume * watts_per_m3
            num_sections = max(4, math.ceil(watts_needed / WATTS_PER_SECTION))
            rad_width = num_sections * RAD_SECTION_W
            rad_width = min(rad_width, rw - 0.400)

            # Radiator height based on window sill (under window)
            rad_height = 0.600

            # Position under window (on exterior wall)
            rad_y = fy + RAD_BRACKET_H + rad_height / 2

            elements.append(Element(
                element_type=ElementType.BEAM,
                material_name="mild_steel",
                x=rx, y=rad_y, z=rz,
                length=rad_width, width=RAD_DEPTH, height=rad_height,
                parent=f"{parent}_rad_{floor_idx}_{room_name}",
                floor_index=floor_idx,
            ))

            # Radiator brackets (2 per radiator)
            for bracket_x in [rx - rad_width / 3, rx + rad_width / 3]:
                elements.append(Element(
                    element_type=ElementType.HINGE,
                    material_name="mild_steel",
                    x=bracket_x, y=rad_y, z=rz,
                    length=0.030, width=0.150, height=0.050,
                    parent=f"{parent}_bracket",
                    floor_index=floor_idx,
                ))

            # Branch pipes to radiator (flow + return)
            pipe_run = ((rx - boiler_x) ** 2 + (rz - boiler_z) ** 2) ** 0.5
            if pipe_run > 0.5:
                for pname, py_off in [("flow", 0.050), ("return", -0.050)]:
                    elements.append(Element(
                        element_type=ElementType.BEAM,
                        material_name="wrought_iron",
                        x=(rx + boiler_x) / 2,
                        y=fy + 0.100 + py_off,
                        z=(rz + boiler_z) / 2,
                        length=pipe_run, width=BRANCH_PIPE_DIA,
                        height=BRANCH_PIPE_DIA,
                        parent=f"{parent}_pipe_{pname}_{floor_idx}",
                        floor_index=floor_idx,
                    ))

    return elements
