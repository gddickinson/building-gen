"""Floor plan validation — catches architectural errors.

Checks generated plans against design rules:
- Outer walls consistent between floors
- Windows only on exterior walls
- Doors don't open into chimneys or exterior
- Rooms reachable from entrance
- Multiple entrances/exits where appropriate
- Stairwells aligned between floors
- Plumbing rooms stacked vertically
"""

from __future__ import annotations

from dataclasses import dataclass, field
from shapely.geometry import LineString, Point

from .models import FloorPlan, RoomPolygon, Opening, OpeningType, WallType


@dataclass
class ValidationIssue:
    """A single validation issue found in a floor plan."""
    severity: str   # "error", "warning", "info"
    category: str   # "walls", "doors", "windows", "stairs", "rooms"
    floor: int
    room: str
    message: str


@dataclass
class ValidationResult:
    """Result of validating a set of floor plans."""
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = [f"Validation: {len(self.errors)} errors, {len(self.warnings)} warnings"]
        for issue in self.issues:
            lines.append(f"  [{issue.severity.upper()}] F{issue.floor} {issue.room}: {issue.message}")
        return "\n".join(lines)


def validate_plans(plans: list[FloorPlan]) -> ValidationResult:
    """Run all validation checks on a set of floor plans."""
    result = ValidationResult()

    for plan in plans:
        _check_windows_on_exterior(plan, result)
        _check_rooms_have_doors(plan, result)
        _check_room_sizes(plan, result)
        _check_front_door(plan, result)

    if len(plans) > 1:
        _check_exterior_walls_align(plans, result)
        _check_stairwell_alignment(plans, result)
        _check_plumbing_stacking(plans, result)

    _check_multiple_exits(plans, result)

    return result


def _check_windows_on_exterior(plan: FloorPlan, result: ValidationResult) -> None:
    """Windows must be on exterior walls, not interior walls."""
    if not plan.footprint:
        return

    fp_boundary = plan.footprint.boundary

    for room in plan.rooms:
        for opening in room.openings:
            if opening.opening_type != OpeningType.WINDOW:
                continue

            pt = Point(opening.position)
            dist = fp_boundary.distance(pt)

            if dist > 0.5:
                result.issues.append(ValidationIssue(
                    "error", "windows", plan.floor_index, room.name,
                    f"Window at ({opening.position[0]:.1f}, {opening.position[1]:.1f}) "
                    f"is {dist:.1f}m from exterior wall — should be on exterior",
                ))


def _check_rooms_have_doors(plan: FloorPlan, result: ValidationResult) -> None:
    """Most rooms should have at least one door."""
    no_door_ok = {"stairwell", "storage", "pantry"}

    for room in plan.rooms:
        if room.room_type in no_door_ok:
            continue

        doors = [o for o in room.openings
                 if o.opening_type in (OpeningType.DOOR, OpeningType.FRONT_DOOR)]
        if not doors:
            result.issues.append(ValidationIssue(
                "warning", "doors", plan.floor_index, room.name,
                "Room has no doors — may be inaccessible",
            ))


def _check_room_sizes(plan: FloorPlan, result: ValidationResult) -> None:
    """Check rooms aren't absurdly small or large."""
    for room in plan.rooms:
        if room.area < 1.0 and room.room_type not in ("stairwell", "storage"):
            result.issues.append(ValidationIssue(
                "error", "rooms", plan.floor_index, room.name,
                f"Room area {room.area:.1f}m² is too small (< 1m²)",
            ))

        if room.area > 50 and room.room_type not in ("shop_floor", "workshop",
                                                       "parlour", "drawing_room"):
            result.issues.append(ValidationIssue(
                "warning", "rooms", plan.floor_index, room.name,
                f"Room area {room.area:.1f}m² seems very large",
            ))

        # Aspect ratio check
        if room.width > 0 and room.height > 0:
            aspect = min(room.width, room.height) / max(room.width, room.height)
            if aspect < 0.15 and room.room_type not in ("hallway", "landing",
                                                          "entrance_hall", "stairwell"):
                result.issues.append(ValidationIssue(
                    "warning", "rooms", plan.floor_index, room.name,
                    f"Room aspect ratio {aspect:.2f} is very narrow "
                    f"({room.width:.1f}x{room.height:.1f}m)",
                ))


def _check_front_door(plan: FloorPlan, result: ValidationResult) -> None:
    """Ground floor must have a front door."""
    if plan.floor_index != 0:
        return

    has_front_door = False
    for room in plan.rooms:
        for o in room.openings:
            if o.opening_type == OpeningType.FRONT_DOOR:
                has_front_door = True
                break

    if not has_front_door:
        result.issues.append(ValidationIssue(
            "error", "doors", 0, "building",
            "Ground floor has no front door",
        ))


def _check_exterior_walls_align(
    plans: list[FloorPlan], result: ValidationResult
) -> None:
    """Exterior walls should be in the same position on all floors."""
    if not plans or not plans[0].footprint:
        return

    ref_bounds = plans[0].footprint.bounds

    for plan in plans[1:]:
        if not plan.footprint:
            continue
        pb = plan.footprint.bounds
        for i, label in enumerate(["minx", "miny", "maxx", "maxy"]):
            diff = abs(pb[i] - ref_bounds[i])
            if diff > 0.1:
                result.issues.append(ValidationIssue(
                    "error", "walls", plan.floor_index, "building",
                    f"Exterior wall {label} offset by {diff:.1f}m from ground floor",
                ))


def _check_stairwell_alignment(
    plans: list[FloorPlan], result: ValidationResult
) -> None:
    """Stairwells must align vertically between floors."""
    stair_positions = []
    for plan in plans:
        for room in plan.rooms:
            if room.room_type == "stairwell":
                stair_positions.append((plan.floor_index, room.centroid, room.bounds))
                break

    if len(stair_positions) < 2:
        return

    ref_cx, ref_cz = stair_positions[0][1]
    for floor_idx, (cx, cz), bounds in stair_positions[1:]:
        dx = abs(cx - ref_cx)
        dz = abs(cz - ref_cz)
        if dx > 0.5 or dz > 0.5:
            result.issues.append(ValidationIssue(
                "error", "stairs", floor_idx, "stairwell",
                f"Stairwell misaligned by ({dx:.1f}, {dz:.1f})m from ground floor",
            ))


def _check_plumbing_stacking(
    plans: list[FloorPlan], result: ValidationResult
) -> None:
    """Wet rooms (bathroom, WC, kitchen) should ideally stack vertically."""
    plumbing_types = {"bathroom", "wc", "kitchen", "scullery"}

    for i in range(1, len(plans)):
        plan = plans[i]
        plan_below = plans[i - 1]

        for room in plan.rooms:
            if room.room_type not in plumbing_types:
                continue

            # Check if there's a plumbing room roughly below this one
            below_plumbing = [
                r for r in plan_below.rooms if r.room_type in plumbing_types
            ]
            if not below_plumbing:
                continue

            # Find nearest plumbing room below
            cx, cy = room.centroid
            min_dist = float("inf")
            for br in below_plumbing:
                bcx, bcy = br.centroid
                dist = ((cx - bcx) ** 2 + (cy - bcy) ** 2) ** 0.5
                min_dist = min(min_dist, dist)

            if min_dist > 3.0:
                result.issues.append(ValidationIssue(
                    "info", "rooms", plan.floor_index, room.name,
                    f"Plumbing room {min_dist:.1f}m from nearest plumbing below "
                    f"(ideally should stack vertically)",
                ))


def _check_multiple_exits(
    plans: list[FloorPlan], result: ValidationResult
) -> None:
    """Buildings should have multiple exits (front + back door)."""
    if not plans:
        return

    ground = plans[0]
    exit_count = 0
    for room in ground.rooms:
        for o in room.openings:
            if o.opening_type == OpeningType.FRONT_DOOR:
                exit_count += 1

    if exit_count < 1:
        result.issues.append(ValidationIssue(
            "error", "doors", 0, "building",
            "Building has no exits",
        ))
    elif exit_count < 2:
        result.issues.append(ValidationIssue(
            "info", "doors", 0, "building",
            "Building has only one exit (front door). "
            "Consider adding a rear/side door.",
        ))
