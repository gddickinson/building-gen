"""Structural load calculations from first principles.

All loads in kN (kilonewtons) and kN/m² (kilonewtons per square metre).

Sources:
    BS EN 1991 (Eurocode 1): Actions on structures
    UK National Annex to Eurocode 1

Load types:
    Dead load (Gk): self-weight of structure and finishes
    Live/imposed load (Qk): people, furniture, storage
    Wind load (Wk): lateral and uplift forces
    Snow load (Sk): on roof

Design load = 1.35 * Gk + 1.5 * Qk (ULS combination)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .model import StructuralModel, RoofStructure, FloorStructure


# ── Material densities (kN/m³) ────────────────────────────────────

DENSITIES = {
    "brick": 19.0,          # Common brickwork
    "stone": 24.0,          # Natural stone
    "stone_rubble": 22.0,   # Rubble stone
    "concrete": 24.0,       # Reinforced concrete
    "timber": 3.7,          # Softwood structural timber (C16: 370 kg/m³ = 3.6 kN/m³)
    "timber_hardwood": 8.0,
    "steel": 78.5,
    "cob": 17.0,            # Earth/cob
    "plaster": 17.0,        # Lime plaster
    "slate": 28.0,          # Roofing slate
    "clay_tile": 20.0,      # Roofing tile
    "lead": 114.0,          # Lead sheet roofing
}

# ── Imposed loads (kN/m²) — BS EN 1991-1-1 ───────────────────────

IMPOSED_LOADS = {
    "residential": 1.5,         # Category A: domestic
    "residential_stairs": 2.0,  # Stairs in residential
    "office": 2.5,              # Category B: office
    "congregation": 4.0,        # Category C: churches, halls
    "shopping": 4.0,            # Category D: retail
    "storage": 7.5,             # Category E: storage/warehouse
    "industrial_light": 5.0,    # Light industrial
    "industrial_heavy": 10.0,   # Heavy industrial
    "roof_access": 0.6,         # Roof not accessible except maintenance
    "roof_no_access": 0.4,      # Roof with no access
    "balcony": 2.5,             # Balcony
    "garage": 2.5,              # Garage for cars
}

# ── Floor dead loads (kN/m²) ──────────────────────────────────────

FLOOR_DEAD_LOADS = {
    "timber_joists": 0.5,       # 200mm timber joists + boards
    "timber_with_plaster": 0.8, # Joists + boards + lath/plaster ceiling
    "concrete_150mm": 3.6,      # 150mm RC slab
    "concrete_200mm": 4.8,      # 200mm RC slab
    "stone_flags": 1.2,         # Stone flag floor on joists
}

# ── Roof dead loads (kN/m² on slope) ──────────────────────────────

ROOF_DEAD_LOADS = {
    "slate_on_timber": 0.8,     # Natural slate on battens on rafters
    "clay_tile_on_timber": 0.7, # Clay tiles on battens on rafters
    "concrete_tile": 0.55,      # Concrete interlocking tiles
    "thatch": 0.35,             # Thatched roof
    "lead_on_timber": 0.55,     # Lead sheet on boarding
    "flat_felt": 0.25,          # Flat roof with felt
}


@dataclass
class LoadCalculation:
    """Complete load calculation for a building."""
    # Per-floor loads
    floor_dead_loads: list[float]    # kN/m² per floor
    floor_live_loads: list[float]    # kN/m² per floor
    floor_total_loads: list[float]   # kN/m² per floor (factored)

    # Roof loads
    roof_dead_load: float = 0.0      # kN/m² on plan
    roof_live_load: float = 0.0
    roof_snow_load: float = 0.0
    roof_total_load: float = 0.0

    # Wall loads
    wall_self_weight_per_m: float = 0.0  # kN/m per metre height
    total_wall_load: float = 0.0         # kN/m at foundation

    # Foundation
    foundation_load_per_m: float = 0.0   # kN/m along foundation
    required_foundation_width: float = 0.0  # metres

    # Roof thrust
    roof_thrust: float = 0.0            # kN/m horizontal at eaves


def calculate_loads(model: StructuralModel) -> LoadCalculation:
    """Calculate all structural loads for a building."""
    w = model.footprint_width
    d = model.footprint_depth
    n = model.num_floors
    h = model.floor_height

    # Floor dead load
    floor_dl = FLOOR_DEAD_LOADS.get(
        "timber_with_plaster" if model.floor_material == "timber" else "concrete_150mm",
        0.8,
    )

    # Floor live load
    floor_ll = IMPOSED_LOADS.get("residential", 1.5)

    # Factored floor load (ULS)
    floor_factored = 1.35 * floor_dl + 1.5 * floor_ll

    floor_dead_loads = [floor_dl] * n
    floor_live_loads = [floor_ll] * n
    floor_total_loads = [floor_factored] * n

    # Roof loads
    roof_dl = ROOF_DEAD_LOADS.get("slate_on_timber", 0.8)
    roof_ll = IMPOSED_LOADS.get("roof_no_access", 0.4)
    roof_snow = 0.5  # kN/m², typical UK

    # Convert from slope area to plan area
    pitch_rad = math.radians(model.roof.pitch_degrees)
    cos_pitch = math.cos(pitch_rad)
    roof_dl_plan = roof_dl / cos_pitch if cos_pitch > 0.1 else roof_dl

    roof_total = 1.35 * roof_dl_plan + 1.5 * max(roof_ll, roof_snow)

    # Roof thrust (horizontal force at eaves from pitched roof)
    # For a simple rafter: thrust = w_roof * span / (2 * tan(pitch))
    # This assumes no tie beam — worst case
    half_span = w / 2
    tan_pitch = math.tan(pitch_rad) if pitch_rad > 0.05 else 1.0
    roof_thrust = roof_total * half_span / (2 * tan_pitch) if tan_pitch > 0.1 else 0.0

    # If roof has a tie beam (most do), thrust is zero
    # But we calculate it to know what the tie beam must resist
    if model.roof.roof_type in ("gable", "hip"):
        # Assume tie beam present — thrust transferred to ties
        effective_thrust = roof_thrust * 0.1  # Residual
    else:
        effective_thrust = 0.0  # Flat roof, no thrust

    # Wall self-weight
    wall_density = DENSITIES.get(model.wall_material, 19.0)
    wall_thickness = 0.35  # Default, should come from model
    for wall in model.walls:
        if wall.thickness > 0:
            wall_thickness = wall.thickness
            break

    wall_self_weight = wall_density * wall_thickness  # kN/m per metre height
    wall_total_self = wall_self_weight * h * n  # kN/m total height

    # Total load at foundation (per metre of wall)
    # = wall self-weight + floors bearing on this wall + roof
    tributary_width = d / 2  # Each long wall supports half the floor
    floor_load_on_wall = floor_factored * tributary_width * n
    roof_load_on_wall = roof_total * tributary_width

    foundation_load = wall_total_self + floor_load_on_wall + roof_load_on_wall

    # Required foundation width
    bearing_capacity = model.bearing_pressure  # kN/m²
    required_width = foundation_load / bearing_capacity if bearing_capacity > 0 else 1.0
    required_width = max(0.45, required_width)  # Minimum 450mm

    return LoadCalculation(
        floor_dead_loads=floor_dead_loads,
        floor_live_loads=floor_live_loads,
        floor_total_loads=floor_total_loads,
        roof_dead_load=roof_dl_plan,
        roof_live_load=roof_ll,
        roof_snow_load=roof_snow,
        roof_total_load=roof_total,
        wall_self_weight_per_m=wall_self_weight,
        total_wall_load=wall_total_self,
        foundation_load_per_m=foundation_load,
        required_foundation_width=required_width,
        roof_thrust=effective_thrust,
    )
