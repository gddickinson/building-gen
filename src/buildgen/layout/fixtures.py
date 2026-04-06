"""Room fixture placement — furniture, appliances, sanitary ware."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum


class FixtureType(str, Enum):
    # Kitchen
    SINK = "sink"
    COOKER = "cooker"
    FRIDGE = "fridge"
    WORKTOP = "worktop"
    # Bathroom / WC
    TOILET = "toilet"
    BATH = "bath"
    SHOWER = "shower"
    BASIN = "basin"
    # Living
    FIREPLACE = "fireplace"
    SOFA = "sofa"
    DINING_TABLE = "dining_table"
    DESK = "desk"
    # Bedroom
    BED_SINGLE = "bed_single"
    BED_DOUBLE = "bed_double"
    WARDROBE = "wardrobe"
    # Utility
    WASHING_MACHINE = "washing_machine"
    BOILER = "boiler"


@dataclass
class Fixture:
    """A fixture placed within a room."""
    fixture_type: FixtureType
    x: float                   # centre position in room coords
    y: float
    width: float               # metres
    depth: float               # metres
    rotation: float = 0.0      # degrees, 0 = facing +y
    against_wall: str = ""     # "north", "south", "east", "west", or ""

    @property
    def label(self) -> str:
        return self.fixture_type.value.replace("_", " ").title()


# Standard fixture sizes (width, depth) in metres
_FIXTURE_SIZES: dict[FixtureType, tuple[float, float]] = {
    FixtureType.SINK: (0.6, 0.5),
    FixtureType.COOKER: (0.6, 0.6),
    FixtureType.FRIDGE: (0.6, 0.6),
    FixtureType.WORKTOP: (2.0, 0.6),
    FixtureType.TOILET: (0.4, 0.7),
    FixtureType.BATH: (0.7, 1.7),
    FixtureType.SHOWER: (0.9, 0.9),
    FixtureType.BASIN: (0.5, 0.4),
    FixtureType.FIREPLACE: (1.2, 0.4),
    FixtureType.SOFA: (2.0, 0.9),
    FixtureType.DINING_TABLE: (1.4, 0.9),
    FixtureType.DESK: (1.2, 0.6),
    FixtureType.BED_SINGLE: (0.9, 2.0),
    FixtureType.BED_DOUBLE: (1.4, 2.0),
    FixtureType.WARDROBE: (1.2, 0.6),
    FixtureType.WASHING_MACHINE: (0.6, 0.6),
    FixtureType.BOILER: (0.5, 0.5),
}

# Which fixtures go in which room types
_ROOM_FIXTURES: dict[str, list[FixtureType]] = {
    "kitchen": [
        FixtureType.SINK, FixtureType.COOKER,
        FixtureType.FRIDGE, FixtureType.WORKTOP,
    ],
    "scullery": [FixtureType.SINK, FixtureType.WASHING_MACHINE],
    "wc": [FixtureType.TOILET, FixtureType.BASIN],
    "bathroom": [
        FixtureType.TOILET, FixtureType.BATH, FixtureType.BASIN,
    ],
    "parlour": [FixtureType.FIREPLACE, FixtureType.SOFA],
    "drawing_room": [FixtureType.FIREPLACE, FixtureType.SOFA],
    "dining_room": [FixtureType.DINING_TABLE, FixtureType.FIREPLACE],
    "study": [FixtureType.DESK, FixtureType.FIREPLACE],
    "library": [FixtureType.DESK, FixtureType.FIREPLACE],
    "master_bedroom": [FixtureType.BED_DOUBLE, FixtureType.WARDROBE],
    "bedroom": [FixtureType.BED_SINGLE, FixtureType.WARDROBE],
    "dressing_room": [FixtureType.WARDROBE],
    "nursery": [FixtureType.BED_SINGLE],
    "servants_quarters": [FixtureType.BED_SINGLE],
}

# Wall preference for fixtures ("north" = top of plan, etc.)
_WALL_PREF: dict[FixtureType, str] = {
    FixtureType.TOILET: "north",
    FixtureType.BATH: "east",
    FixtureType.BASIN: "north",
    FixtureType.SINK: "north",
    FixtureType.COOKER: "east",
    FixtureType.FRIDGE: "west",
    FixtureType.WORKTOP: "south",
    FixtureType.FIREPLACE: "north",
    FixtureType.WARDROBE: "west",
    FixtureType.BED_SINGLE: "east",
    FixtureType.BED_DOUBLE: "north",
}


def place_fixtures_in_room(
    room_bounds: tuple[float, float, float, float],
    room_type: str,
    rng: random.Random,
) -> list[Fixture]:
    """Place appropriate fixtures within a room.

    Args:
        room_bounds: (minx, miny, maxx, maxy) of the room
        room_type: room type string
        rng: random number generator

    Returns:
        list of placed Fixture objects
    """
    fixture_types = _ROOM_FIXTURES.get(room_type, [])
    if not fixture_types:
        return []

    minx, miny, maxx, maxy = room_bounds
    rw = maxx - minx
    rh = maxy - miny

    placed: list[Fixture] = []
    occupied: list[tuple[float, float, float, float]] = []

    for ft in fixture_types:
        fw, fd = _FIXTURE_SIZES.get(ft, (0.5, 0.5))

        # Skip if fixture won't fit
        if fw > rw - 0.2 or fd > rh - 0.2:
            continue

        # Determine placement against wall
        wall = _WALL_PREF.get(ft, "")
        x, y, rot = _place_against_wall(
            wall, minx, miny, maxx, maxy, fw, fd, rng
        )

        # Check for overlap with already-placed fixtures
        rect = (x - fw / 2, y - fd / 2, x + fw / 2, y + fd / 2)
        if _overlaps_any(rect, occupied):
            # Try alternative positions
            for alt_wall in ["north", "south", "east", "west"]:
                if alt_wall == wall:
                    continue
                x, y, rot = _place_against_wall(
                    alt_wall, minx, miny, maxx, maxy, fw, fd, rng
                )
                rect = (x - fw / 2, y - fd / 2, x + fw / 2, y + fd / 2)
                if not _overlaps_any(rect, occupied):
                    wall = alt_wall
                    break
            else:
                continue  # Skip this fixture if no position works

        occupied.append(rect)
        placed.append(Fixture(
            fixture_type=ft,
            x=x, y=y,
            width=fw, depth=fd,
            rotation=rot,
            against_wall=wall,
        ))

    return placed


def _place_against_wall(
    wall: str,
    minx: float, miny: float, maxx: float, maxy: float,
    fw: float, fd: float,
    rng: random.Random,
) -> tuple[float, float, float]:
    """Calculate position for a fixture against a wall.

    Returns (x, y, rotation_degrees).
    """
    margin = 0.15
    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2
    jitter = 0.3

    if wall == "north":
        x = cx + rng.uniform(-jitter, jitter)
        y = maxy - fd / 2 - margin
        rot = 0
    elif wall == "south":
        x = cx + rng.uniform(-jitter, jitter)
        y = miny + fd / 2 + margin
        rot = 180
    elif wall == "east":
        x = maxx - fd / 2 - margin
        y = cy + rng.uniform(-jitter, jitter)
        rot = 90
    elif wall == "west":
        x = minx + fd / 2 + margin
        y = cy + rng.uniform(-jitter, jitter)
        rot = 270
    else:
        x = cx + rng.uniform(-0.5, 0.5)
        y = cy + rng.uniform(-0.5, 0.5)
        rot = 0

    # Clamp to room
    x = max(minx + fw / 2 + margin, min(x, maxx - fw / 2 - margin))
    y = max(miny + fd / 2 + margin, min(y, maxy - fd / 2 - margin))

    return x, y, rot


def _overlaps_any(
    rect: tuple[float, float, float, float],
    others: list[tuple[float, float, float, float]],
    margin: float = 0.1,
) -> bool:
    """Check if a rectangle overlaps any in the list."""
    for other in others:
        if (rect[0] - margin < other[2] and rect[2] + margin > other[0] and
                rect[1] - margin < other[3] and rect[3] + margin > other[1]):
            return True
    return False
