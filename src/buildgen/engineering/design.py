"""Structural design — creates a sound structural model.

Designs from first principles:
1. Start with the building footprint and desired floors
2. Create the building envelope (exterior walls around full perimeter)
3. Determine load-bearing wall positions (every floor spans between them)
4. Size walls, lintels, and foundations based on calculated loads
5. Interior partitions are added AFTER the structure is sound

The key principle: STRUCTURE FIRST, ROOMS SECOND.
"""

from __future__ import annotations

import math

from .model import (
    FloorStructure,
    LoadPath,
    RoofStructure,
    StructuralModel,
    StructuralWall,
    WallClassification,
)
from .loads import DENSITIES, calculate_loads
from ..program.constraints import MATERIALS


def design_structure(
    width: float,
    depth: float,
    num_floors: int,
    floor_height: float = 3.0,
    wall_material: str = "brick",
    roof_type: str = "gable",
    roof_pitch: float = 35.0,
) -> StructuralModel:
    """Design a structurally sound building from first principles.

    Returns a StructuralModel with all walls, floors, and roof
    sized to carry the required loads.
    """
    # Get material properties
    mat = MATERIALS.get(wall_material)
    if mat:
        wall_thickness = mat.wall_thickness_exterior
        max_span = mat.max_span
        max_opening = mat.max_opening_width
        min_pier = mat.min_pier_width
        int_thickness = mat.wall_thickness_interior
    else:
        wall_thickness = 0.35
        max_span = 5.0
        max_opening = 2.5
        min_pier = 0.45
        int_thickness = 0.12

    model = StructuralModel(
        footprint_width=width,
        footprint_depth=depth,
        num_floors=num_floors,
        floor_height=floor_height,
        wall_material=wall_material,
    )

    # ── 1. EXTERIOR WALLS — complete perimeter on every floor ──
    # Four walls forming a closed rectangle
    corners = [
        (0, 0), (width, 0), (width, depth), (0, depth),
    ]
    for i in range(4):
        j = (i + 1) % 4
        model.walls.append(StructuralWall(
            start=corners[i],
            end=corners[j],
            classification=WallClassification.EXTERIOR_LOAD_BEARING,
            thickness=wall_thickness,
            height=floor_height * num_floors,
            material=wall_material,
            max_opening_width=max_opening,
            min_pier_width=min_pier,
        ))

    # ── 2. INTERNAL LOAD-BEARING WALLS ──
    # Floor joists need intermediate support if span > max_span
    # Joists typically span the shorter dimension
    joist_span_dir = "x" if width <= depth else "y"

    if joist_span_dir == "x":
        clear_span = width
    else:
        clear_span = depth

    # If span exceeds material limit, add internal load-bearing wall(s)
    num_internal_lb = 0
    if clear_span > max_span:
        num_internal_lb = math.ceil(clear_span / max_span) - 1

    actual_span = clear_span / (num_internal_lb + 1)

    # Place internal load-bearing walls evenly
    for i in range(1, num_internal_lb + 1):
        pos = clear_span * i / (num_internal_lb + 1)
        if joist_span_dir == "x":
            # Wall runs along Y (depth), at X = pos
            model.walls.append(StructuralWall(
                start=(pos, 0),
                end=(pos, depth),
                classification=WallClassification.INTERIOR_LOAD_BEARING,
                thickness=int_thickness,
                height=floor_height * num_floors,
                material=wall_material,
            ))
        else:
            # Wall runs along X (width), at Y = pos
            model.walls.append(StructuralWall(
                start=(0, pos),
                end=(width, pos),
                classification=WallClassification.INTERIOR_LOAD_BEARING,
                thickness=int_thickness,
                height=floor_height * num_floors,
                material=wall_material,
            ))

    # ── 3. FLOOR STRUCTURES ──
    for f in range(num_floors):
        floor = FloorStructure(
            floor_index=f,
            span_direction=joist_span_dir,
            max_span=actual_span,
            depth=_size_joist(actual_span),
            dead_load=0.8,   # timber floor + plaster ceiling
            live_load=1.5,   # residential
            total_load=0.8 + 1.5,
            material="timber",
        )
        model.floors.append(floor)

    # ── 4. ROOF STRUCTURE ──
    roof_span = width if roof_type in ("gable",) else min(width, depth)
    pitch_rad = math.radians(roof_pitch)

    rafter_length = (roof_span / 2) / math.cos(pitch_rad) if math.cos(pitch_rad) > 0.1 else roof_span
    ridge_height = (roof_span / 2) * math.tan(pitch_rad)

    model.roof = RoofStructure(
        roof_type=roof_type,
        pitch_degrees=roof_pitch,
        span=roof_span,
        dead_load=0.8,
        wind_load=0.5,
        snow_load=0.5,
    )

    # ── 5. CALCULATE LOADS ──
    loads = calculate_loads(model)

    # Update wall loads
    for wall in model.walls:
        if wall.classification in (WallClassification.EXTERIOR_LOAD_BEARING,
                                    WallClassification.INTERIOR_LOAD_BEARING):
            wall.dead_load = loads.wall_self_weight_per_m * wall.height / model.floor_height
            wall.total_load = loads.foundation_load_per_m

    model.roof.thrust = loads.roof_thrust
    model.roof.vertical_reaction = loads.roof_total_load * width / 2

    # ── 6. LOAD PATHS ──
    # Trace loads from roof to foundation at each wall position
    for wall in model.load_bearing_walls:
        mid = ((wall.start[0] + wall.end[0]) / 2,
               (wall.start[1] + wall.end[1]) / 2)
        lp = LoadPath(
            x=mid[0], y=mid[1],
            loads_per_floor=[loads.floor_total_loads[0]] * num_floors,
            total_to_foundation=loads.foundation_load_per_m * wall.length,
        )
        # Determine foundation type
        if loads.foundation_load_per_m < 50:
            lp.foundation_type = "strip"
        elif loads.foundation_load_per_m < 150:
            lp.foundation_type = "strip_reinforced"
        else:
            lp.foundation_type = "raft"

        model.load_paths.append(lp)

    model.foundation_type = model.load_paths[0].foundation_type if model.load_paths else "strip"

    # ── 7. FOUNDATION SIZING ──
    model.foundation_depth = max(
        0.45,  # Minimum depth
        0.6 + 0.1 * (num_floors - 1),  # Deeper for taller buildings
    )

    return model


def _size_joist(span: float) -> float:
    """Size a timber floor joist for a given span.

    Rule of thumb: joist depth (mm) = span (mm) / 24 + 50
    Returns depth in metres.
    """
    depth_mm = span * 1000 / 24 + 50
    # Round up to standard sizes: 150, 175, 200, 225, 250mm
    standard_sizes = [0.150, 0.175, 0.200, 0.225, 0.250, 0.300]
    for s in standard_sizes:
        if s >= depth_mm / 1000:
            return s
    return 0.300
