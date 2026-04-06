"""Building program generator (Pipeline Stage 1).

Generates a BuildingProgram from a building type, era, and constraints.
A program specifies which rooms exist on each floor, how they connect,
and what size/feature constraints they have.

Public API:
    - ProgramGenerator: loads templates, produces BuildingProgram instances
    - BuildingProgram: complete specification for a building
    - FloorProgram: rooms and adjacency for a single floor
    - RoomSpec: specification for a single room
    - AdjacencyReq: required/preferred adjacency between rooms
    - ROOM_CONSTRAINTS: minimum dimensions per room type
    - MATERIALS: material properties affecting structure
    - STAIR_TYPES: staircase configurations and requirements
    - SiteConstraints: site/environment factors
"""

from .models import BuildingProgram, FloorProgram, RoomSpec, AdjacencyReq
from .generator import ProgramGenerator
from .constraints import (
    ROOM_CONSTRAINTS,
    MATERIALS,
    STAIR_TYPES,
    SiteConstraints,
    CLIMATE_IMPACTS,
)

__all__ = [
    "ProgramGenerator",
    "BuildingProgram",
    "FloorProgram",
    "RoomSpec",
    "AdjacencyReq",
    "ROOM_CONSTRAINTS",
    "MATERIALS",
    "STAIR_TYPES",
    "SiteConstraints",
    "CLIMATE_IMPACTS",
]
