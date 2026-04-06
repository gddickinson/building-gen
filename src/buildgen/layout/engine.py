"""Layout engine — generates floor plans from building programs."""

from __future__ import annotations

import random

from shapely.geometry import Polygon, box

from ..program.models import (
    AdjacencyType,
    BuildingProgram,
    FloorProgram,
    RoomSpec,
)
from .models import (
    FloorPlan,
    Opening,
    OpeningType,
    RoomPolygon,
    WallSegment,
    WallType,
)
from .subdivide import subdivide_floor
from .fixtures import place_fixtures_in_room


class LayoutEngine:
    """Generates 2D floor plans from a BuildingProgram.

    Usage:
        engine = LayoutEngine()
        floor_plans = engine.generate(program)
    """

    def generate(self, program: BuildingProgram) -> list[FloorPlan]:
        """Generate floor plans for all floors in the program."""
        rng = random.Random(program.seed)
        footprint = box(
            0, 0, program.footprint_width, program.footprint_depth
        )

        floor_plans = []
        stairwell_rect = None

        # Determine stairwell position (consistent across floors)
        stair_rooms = [
            r for f in program.floors for r in f.rooms if r.is_stairwell
        ]
        if stair_rooms:
            sw = stair_rooms[0]
            # Stairwell: ~1.0m wide x 2.5m deep, fits within hall column
            sw_w = 1.0
            sw_d = max(sw.min_area / sw_w, 2.5)
            # Place stairwell centrally, behind the entrance hall
            sx = (program.footprint_width - sw_w) / 2 + rng.uniform(-0.3, 0.3)
            sy = program.footprint_depth * 0.35 + rng.uniform(-0.3, 0.3)
            sx = max(0.3, min(sx, program.footprint_width - sw_w - 0.3))
            sy = max(0.3, min(sy, program.footprint_depth - sw_d - 0.3))
            stairwell_rect = (sx, sy, sx + sw_w, sy + sw_d)

        for floor_prog in program.floors:
            plan = self._generate_floor(
                floor_prog, footprint, stairwell_rect, program, rng
            )
            floor_plans.append(plan)

        return floor_plans

    def _generate_floor(
        self,
        floor_prog: FloorProgram,
        footprint: Polygon,
        stairwell_rect: tuple[float, float, float, float] | None,
        program: BuildingProgram,
        rng: random.Random,
    ) -> FloorPlan:
        """Generate a single floor plan."""
        # Separate stairwell from other rooms
        stair_rooms = [r for r in floor_prog.rooms if r.is_stairwell]
        normal_rooms = [r for r in floor_prog.rooms if not r.is_stairwell]

        # Subdivide the footprint into rooms
        room_polygons = subdivide_floor(
            footprint, normal_rooms, stairwell_rect, rng
        )

        # Add stairwell
        if stairwell_rect and stair_rooms:
            sw_poly = box(*stairwell_rect)
            sr = stair_rooms[0]
            room_polygons.append(RoomPolygon(
                name=sr.name,
                room_type=sr.room_type.value,
                polygon=sw_poly,
                floor=floor_prog.floor_index,
            ))

        plan = FloorPlan(
            floor_index=floor_prog.floor_index,
            rooms=room_polygons,
            footprint=footprint,
        )

        # Extract walls
        plan.walls = self._extract_walls(plan, program.wall_thickness)

        # Place openings
        self._place_doors(plan, floor_prog, rng)
        self._place_windows(plan, floor_prog, program, rng)

        # Place fixtures in rooms
        for room in plan.rooms:
            fixtures = place_fixtures_in_room(
                room.bounds, room.room_type, rng
            )
            room._fixtures = fixtures

        return plan

    def _extract_walls(
        self, plan: FloorPlan, thickness: float
    ) -> list[WallSegment]:
        """Extract wall segments from room polygons."""
        walls: list[WallSegment] = []
        fp_boundary = plan.footprint.boundary if plan.footprint else None

        for room in plan.rooms:
            coords = list(room.polygon.exterior.coords)
            for i in range(len(coords) - 1):
                start = (round(coords[i][0], 4), round(coords[i][1], 4))
                end = (round(coords[i + 1][0], 4), round(coords[i + 1][1], 4))

                # Check if this edge is on the footprint boundary
                from shapely.geometry import LineString
                edge = LineString([start, end])
                is_exterior = False
                if fp_boundary and edge.length > 0.01:
                    is_exterior = fp_boundary.distance(edge) < 0.01

                # Avoid duplicate walls
                already_exists = False
                for w in walls:
                    if _edges_match(w.start, w.end, start, end):
                        already_exists = True
                        break

                if not already_exists:
                    walls.append(WallSegment(
                        start=start,
                        end=end,
                        wall_type=(
                            WallType.EXTERIOR if is_exterior
                            else WallType.INTERIOR
                        ),
                        thickness=thickness,
                    ))

        return walls

    def _place_doors(
        self,
        plan: FloorPlan,
        floor_prog: FloorProgram,
        rng: random.Random,
    ) -> None:
        """Place doors between adjacent rooms."""
        placed_doors: set[tuple[str, str]] = set()

        for adj in floor_prog.adjacencies:
            if adj.adj_type == AdjacencyType.MUST_NOT:
                continue

            room_a = plan.room_by_name(adj.room_a)
            room_b = plan.room_by_name(adj.room_b)
            if not room_a or not room_b:
                continue

            # Find shared wall
            shared = _find_shared_edge(room_a, room_b)
            if not shared:
                continue

            key = tuple(sorted([adj.room_a, adj.room_b]))
            if key in placed_doors:
                continue
            placed_doors.add(key)

            mid = ((shared[0][0] + shared[1][0]) / 2,
                   (shared[0][1] + shared[1][1]) / 2)

            door = Opening(
                opening_type=OpeningType.DOOR,
                position=mid,
                width=0.9,
                height=2.1,
            )
            room_a.openings.append(door)

        # Front door — centred on the building facade (Georgian convention)
        if plan.floor_index == 0:
            entrance = plan.room_by_name("entrance_hall")
            if entrance and plan.footprint:
                fb = plan.footprint.bounds
                facade_centre_x = (fb[0] + fb[2]) / 2.0
                # Place front door at facade centre, on the y=0 (front) edge
                front_y = fb[1]

                # Ensure the door position is on the entrance hall's front edge
                eb = entrance.bounds
                door_x = facade_centre_x
                # Clamp to entrance hall's x range
                door_x = max(eb[0] + 0.5, min(door_x, eb[2] - 0.5))

                entrance.openings.append(Opening(
                    opening_type=OpeningType.FRONT_DOOR,
                    position=(door_x, front_y),
                    width=1.1,
                    height=2.4,
                ))

    def _place_windows(
        self,
        plan: FloorPlan,
        floor_prog: FloorProgram,
        program: BuildingProgram,
        rng: random.Random,
    ) -> None:
        """Place windows on exterior walls of rooms that need them."""
        if not plan.footprint:
            return

        fp_boundary = plan.footprint.boundary

        for room in plan.rooms:
            # Find room spec
            spec = None
            for r in floor_prog.rooms:
                if r.name == room.name:
                    spec = r
                    break

            if spec and not spec.needs_window:
                continue

            coords = list(room.polygon.exterior.coords)
            for i in range(len(coords) - 1):
                from shapely.geometry import LineString
                edge = LineString([coords[i], coords[i + 1]])

                if edge.length < 1.0:
                    continue

                if fp_boundary.distance(edge) > 0.01:
                    continue

                # Place windows along this exterior edge
                num_windows = max(1, int(edge.length / 2.0))
                for wi in range(num_windows):
                    t = (wi + 0.5) / num_windows
                    pt = edge.interpolate(t, normalized=True)
                    room.openings.append(Opening(
                        opening_type=OpeningType.WINDOW,
                        position=(pt.x, pt.y),
                        width=1.0,
                        height=1.4,
                        sill_height=0.9,
                    ))


def _edges_match(
    s1: tuple, e1: tuple, s2: tuple, e2: tuple, tol: float = 0.05
) -> bool:
    """Check if two edges are the same (possibly reversed)."""
    def close(a: tuple, b: tuple) -> bool:
        return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol
    return (close(s1, s2) and close(e1, e2)) or (
        close(s1, e2) and close(e1, s2)
    )


def _find_shared_edge(
    room_a: RoomPolygon, room_b: RoomPolygon, tol: float = 0.05
) -> tuple | None:
    """Find a shared edge between two room polygons."""
    coords_a = list(room_a.polygon.exterior.coords)
    coords_b = list(room_b.polygon.exterior.coords)

    for i in range(len(coords_a) - 1):
        for j in range(len(coords_b) - 1):
            if _edges_match(
                coords_a[i], coords_a[i + 1],
                coords_b[j], coords_b[j + 1],
                tol,
            ):
                return (coords_a[i], coords_a[i + 1])

    # Check for partial overlap
    from shapely.geometry import LineString
    for i in range(len(coords_a) - 1):
        edge_a = LineString([coords_a[i], coords_a[i + 1]])
        for j in range(len(coords_b) - 1):
            edge_b = LineString([coords_b[j], coords_b[j + 1]])
            if edge_a.distance(edge_b) < tol:
                overlap = edge_a.intersection(edge_b.buffer(tol))
                if overlap and not overlap.is_empty:
                    mid = overlap.centroid
                    return (coords_a[i], coords_a[i + 1])

    return None
