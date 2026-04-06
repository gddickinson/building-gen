"""Data models for floor plans."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from shapely.geometry import Polygon, LineString


class OpeningType(str, Enum):
    DOOR = "door"
    WINDOW = "window"
    FRONT_DOOR = "front_door"


class WallType(str, Enum):
    EXTERIOR = "exterior"
    INTERIOR = "interior"
    PARTY = "party"  # Shared with adjacent building


@dataclass
class Opening:
    """A door or window placed on a wall."""
    opening_type: OpeningType
    position: tuple[float, float]   # Centre point (x, y)
    width: float                     # metres
    height: float                    # metres (for 3D)
    sill_height: float = 0.0        # metres above floor (for 3D)
    wall_index: int = 0             # Which wall segment this belongs to


@dataclass
class WallSegment:
    """A wall line with metadata."""
    start: tuple[float, float]
    end: tuple[float, float]
    wall_type: WallType = WallType.INTERIOR
    thickness: float = 0.3

    @property
    def line(self) -> LineString:
        return LineString([self.start, self.end])

    @property
    def length(self) -> float:
        return self.line.length

    @property
    def midpoint(self) -> tuple[float, float]:
        mp = self.line.interpolate(0.5, normalized=True)
        return (mp.x, mp.y)


@dataclass
class RoomPolygon:
    """A room with its geometry and metadata."""
    name: str
    room_type: str
    polygon: Polygon
    floor: int = 0
    openings: list[Opening] = field(default_factory=list)

    @property
    def area(self) -> float:
        return self.polygon.area

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return self.polygon.bounds  # (minx, miny, maxx, maxy)

    @property
    def centroid(self) -> tuple[float, float]:
        c = self.polygon.centroid
        return (c.x, c.y)

    @property
    def width(self) -> float:
        b = self.bounds
        return b[2] - b[0]

    @property
    def height(self) -> float:
        b = self.bounds
        return b[3] - b[1]


@dataclass
class FloorPlan:
    """Complete floor plan for one level."""
    floor_index: int
    rooms: list[RoomPolygon] = field(default_factory=list)
    walls: list[WallSegment] = field(default_factory=list)
    footprint: Polygon | None = None

    @property
    def total_area(self) -> float:
        return sum(r.area for r in self.rooms)

    def room_by_name(self, name: str) -> RoomPolygon | None:
        for r in self.rooms:
            if r.name == name:
                return r
        return None
