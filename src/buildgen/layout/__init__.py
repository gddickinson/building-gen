"""Floor plan layout engine (Pipeline Stage 2).

Generates 2D floor plans from BuildingProgram specifications.
Uses BSP subdivision + simulated annealing to produce room layouts
that satisfy adjacency and sizing constraints.

Public API:
    - LayoutEngine: main class, takes BuildingProgram -> list[FloorPlan]
    - FloorPlan: complete floor plan with rooms, walls, doors, windows
    - RoomPolygon: single room with geometry and metadata
    - WallSegment: wall line with thickness and type
    - Opening: door or window placed on a wall
    - Fixture: interior fixture (toilet, bath, fireplace, etc.)
    - FixtureType: enum of fixture types
"""

from .models import FloorPlan, RoomPolygon, WallSegment, Opening, OpeningType
from .engine import LayoutEngine
from .fixtures import Fixture, FixtureType, place_fixtures_in_room

__all__ = [
    "LayoutEngine",
    "FloorPlan",
    "RoomPolygon",
    "WallSegment",
    "Opening",
    "OpeningType",
    "Fixture",
    "FixtureType",
    "place_fixtures_in_room",
]
