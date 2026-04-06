"""Structural model — the skeleton of a building.

A building is fundamentally:
1. A foundation transferring loads to the ground
2. Exterior walls defining the building envelope
3. Internal load-bearing walls supporting floors and roof
4. Floor structures spanning between walls
5. A roof structure creating the weather envelope

Every element has forces acting on it. The structure must transfer
all loads down to the foundation without exceeding material strength.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class WallClassification(str, Enum):
    """Structural role of a wall."""
    EXTERIOR_LOAD_BEARING = "exterior_load_bearing"
    INTERIOR_LOAD_BEARING = "interior_load_bearing"
    PARTITION = "partition"           # Non-load-bearing divider
    FOUNDATION = "foundation"         # Below ground
    RETAINING = "retaining"           # Holds back earth


@dataclass
class StructuralWall:
    """A wall with structural properties."""
    start: tuple[float, float]     # (x, y) start point
    end: tuple[float, float]       # (x, y) end point
    classification: WallClassification
    thickness: float               # metres
    height: float                  # metres (floor to floor)
    material: str                  # brick, stone, timber, etc.
    # Loads
    dead_load: float = 0.0         # kN/m — self-weight per unit length
    imposed_load: float = 0.0      # kN/m — load from floors/roof above
    total_load: float = 0.0        # kN/m — total vertical load
    # Openings
    max_opening_width: float = 0.0 # metres — max lintel span
    min_pier_width: float = 0.0    # metres — min wall between openings

    @property
    def length(self) -> float:
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        return (dx * dx + dy * dy) ** 0.5

    @property
    def load_per_metre(self) -> float:
        return self.total_load


@dataclass
class LoadPath:
    """A vertical load path from roof to foundation."""
    x: float                       # Position along building width
    y: float                       # Position along building depth
    loads_per_floor: list[float] = field(default_factory=list)  # kN per floor
    total_to_foundation: float = 0.0  # kN total at foundation
    foundation_type: str = ""       # strip, pad, raft


@dataclass
class FloorStructure:
    """A floor slab/structure between levels."""
    floor_index: int
    span_direction: str = "x"     # "x" or "y" — joists span this way
    max_span: float = 0.0         # metres — clear span between supports
    depth: float = 0.0            # metres — joist/slab depth
    dead_load: float = 0.0        # kN/m² — self-weight
    live_load: float = 0.0        # kN/m² — occupancy load
    total_load: float = 0.0       # kN/m²
    material: str = "timber"      # timber, concrete, steel


@dataclass
class RoofStructure:
    """The roof structure."""
    roof_type: str = "gable"      # gable, hip, flat, mansard
    pitch_degrees: float = 35.0   # Roof pitch angle
    span: float = 0.0             # metres — clear span
    # Forces
    dead_load: float = 0.0        # kN/m² on plan
    wind_load: float = 0.0        # kN/m² on slope
    snow_load: float = 0.0        # kN/m²
    thrust: float = 0.0           # kN/m — horizontal thrust at eaves
    vertical_reaction: float = 0.0 # kN/m — vertical load at eaves


@dataclass
class StructuralModel:
    """Complete structural model of a building."""
    # Geometry
    footprint_width: float = 0.0   # metres
    footprint_depth: float = 0.0   # metres
    num_floors: int = 1
    floor_height: float = 3.0      # metres

    # Materials
    wall_material: str = "brick"
    floor_material: str = "timber"
    roof_material: str = "timber"

    # Structure
    walls: list[StructuralWall] = field(default_factory=list)
    floors: list[FloorStructure] = field(default_factory=list)
    roof: RoofStructure = field(default_factory=RoofStructure)
    load_paths: list[LoadPath] = field(default_factory=list)

    # Foundation
    foundation_type: str = "strip"  # strip, pad, raft
    foundation_depth: float = 0.6   # metres below ground
    bearing_pressure: float = 100.0 # kN/m² — soil bearing capacity

    @property
    def total_building_weight(self) -> float:
        """Approximate total building weight in kN."""
        return sum(lp.total_to_foundation for lp in self.load_paths)

    @property
    def load_bearing_walls(self) -> list[StructuralWall]:
        return [w for w in self.walls
                if w.classification in (
                    WallClassification.EXTERIOR_LOAD_BEARING,
                    WallClassification.INTERIOR_LOAD_BEARING,
                )]

    @property
    def partitions(self) -> list[StructuralWall]:
        return [w for w in self.walls
                if w.classification == WallClassification.PARTITION]
