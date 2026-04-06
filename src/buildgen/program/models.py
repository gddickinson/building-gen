"""Data models for building programs."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RoomType(str, Enum):
    """Functional type of a room."""
    # Residential
    ENTRANCE_HALL = "entrance_hall"
    HALLWAY = "hallway"
    PARLOUR = "parlour"
    DINING_ROOM = "dining_room"
    KITCHEN = "kitchen"
    SCULLERY = "scullery"
    PANTRY = "pantry"
    WC = "wc"
    BATHROOM = "bathroom"
    BEDROOM = "bedroom"
    MASTER_BEDROOM = "master_bedroom"
    DRESSING_ROOM = "dressing_room"
    NURSERY = "nursery"
    STUDY = "study"
    LIBRARY = "library"
    DRAWING_ROOM = "drawing_room"
    SERVANTS_QUARTERS = "servants_quarters"
    STORAGE = "storage"
    LANDING = "landing"
    STAIRWELL = "stairwell"
    # Commercial
    SHOP_FLOOR = "shop_floor"
    WORKSHOP = "workshop"
    OFFICE = "office"
    # Utility
    CELLAR = "cellar"
    ATTIC = "attic"
    # Generic
    GENERIC = "generic"


class AdjacencyType(str, Enum):
    """Strength of adjacency requirement."""
    MUST = "must"          # Rooms must share a wall
    SHOULD = "should"      # Preferred but not required
    MUST_NOT = "must_not"  # Rooms must not be adjacent


@dataclass
class RoomSpec:
    """Specification for a single room."""
    name: str
    room_type: RoomType
    min_area: float          # m²
    max_area: float          # m²
    min_aspect: float = 0.4  # min(w,h)/max(w,h), 1.0 = square
    max_aspect: float = 1.0
    needs_exterior_wall: bool = True   # Needs window / natural light
    needs_window: bool = True
    is_stairwell: bool = False
    floor: int = 0           # Which floor this room is on

    @property
    def target_area(self) -> float:
        return (self.min_area + self.max_area) / 2


@dataclass
class AdjacencyReq:
    """Adjacency requirement between two rooms."""
    room_a: str   # Room name
    room_b: str   # Room name
    adj_type: AdjacencyType = AdjacencyType.SHOULD


@dataclass
class FloorProgram:
    """Room program for a single floor."""
    floor_index: int
    rooms: list[RoomSpec] = field(default_factory=list)
    adjacencies: list[AdjacencyReq] = field(default_factory=list)

    @property
    def total_area(self) -> float:
        return sum(r.target_area for r in self.rooms)


@dataclass
class BuildingProgram:
    """Complete specification for a building."""
    building_type: str
    style: str
    floors: list[FloorProgram] = field(default_factory=list)
    footprint_width: float = 0.0   # metres, 0 = auto
    footprint_depth: float = 0.0   # metres, 0 = auto
    wall_thickness: float = 0.3    # metres
    seed: int = 0

    @property
    def num_floors(self) -> int:
        return len(self.floors)

    def all_rooms(self) -> list[RoomSpec]:
        result = []
        for floor in self.floors:
            result.extend(floor.rooms)
        return result
