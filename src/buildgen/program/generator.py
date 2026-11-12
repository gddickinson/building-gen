"""Building program generator — creates BuildingProgram from templates."""

from __future__ import annotations

import random
from pathlib import Path

import yaml

from .models import (
    AdjacencyReq,
    AdjacencyType,
    BuildingProgram,
    FloorProgram,
    RoomSpec,
    RoomType,
)


class ProgramGenerator:
    """Generates BuildingProgram instances from YAML templates.

    Usage:
        gen = ProgramGenerator()
        program = gen.generate("townhouse", style="georgian", seed=42)
    """

    def __init__(self, template_dir: Path | None = None):
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        self.template_dir = template_dir

    def available_types(self) -> list[str]:
        """List available building type templates.

        Only YAML files that define floors (BSP templates) or a grid (reference templates) are building types;
        other YAML files in the folder (e.g. building_type_rules.yaml, a design-rules reference) are not.
        """
        return [p.stem for p in self.template_dir.glob("*.yaml") if is_building_template(p)]

    def generate(
        self,
        building_type: str,
        style: str = "georgian",
        seed: int = 0,
    ) -> BuildingProgram:
        """Generate a BuildingProgram from a template with random variation."""
        rng = random.Random(seed)
        template_path = self.template_dir / f"{building_type}.yaml"

        if not template_path.exists():
            raise FileNotFoundError(
                f"No template for '{building_type}'. "
                f"Available: {self.available_types()}"
            )

        with open(template_path) as f:
            tmpl = yaml.safe_load(f)
        if not _is_template_dict(tmpl):
            raise ValueError(
                f"'{building_type}' is not a building type template. "
                f"Available: {self.available_types()}"
            )

        program = BuildingProgram(
            building_type=building_type,
            style=style,
            seed=seed,
        )

        # Parse footprint
        fp = tmpl.get("footprint", {})
        program.footprint_width = _vary(
            fp.get("width", 8.0), fp.get("width_var", 1.0), rng
        )
        program.footprint_depth = _vary(
            fp.get("depth", 12.0), fp.get("depth_var", 1.5), rng
        )
        program.wall_thickness = fp.get("wall_thickness", 0.3)

        # Parse floors
        for floor_def in tmpl.get("floors", []):
            floor_idx = floor_def["index"]
            floor = FloorProgram(floor_index=floor_idx)

            # Decide which optional rooms to include
            for room_def in floor_def.get("rooms", []):
                if room_def.get("optional", False):
                    prob = room_def.get("probability", 0.5)
                    if rng.random() > prob:
                        continue

                # Apply variation to areas
                min_area = room_def.get("min_area", 8.0)
                max_area = room_def.get("max_area", 16.0)
                area_var = room_def.get("area_var", 1.0)
                min_area = max(4.0, min_area + rng.uniform(-area_var, area_var))
                max_area = max(min_area + 1.0, max_area + rng.uniform(-area_var, area_var))

                room = RoomSpec(
                    name=room_def["name"],
                    room_type=RoomType(room_def.get("type", "generic")),
                    min_area=min_area,
                    max_area=max_area,
                    min_aspect=room_def.get("min_aspect", 0.4),
                    max_aspect=room_def.get("max_aspect", 1.0),
                    needs_exterior_wall=room_def.get("needs_exterior_wall", True),
                    needs_window=room_def.get("needs_window", True),
                    is_stairwell=room_def.get("is_stairwell", False),
                    floor=floor_idx,
                )
                floor.rooms.append(room)

            # Parse adjacency requirements
            for adj_def in floor_def.get("adjacencies", []):
                # Only add adjacency if both rooms exist
                room_names = {r.name for r in floor.rooms}
                if adj_def["a"] in room_names and adj_def["b"] in room_names:
                    floor.adjacencies.append(AdjacencyReq(
                        room_a=adj_def["a"],
                        room_b=adj_def["b"],
                        adj_type=AdjacencyType(adj_def.get("type", "should")),
                    ))

            # Always add stairwell if there are multiple floors
            if len(tmpl.get("floors", [])) > 1:
                has_stair = any(r.is_stairwell for r in floor.rooms)
                if not has_stair:
                    floor.rooms.append(RoomSpec(
                        name=f"stairs_{floor_idx}",
                        room_type=RoomType.STAIRWELL,
                        min_area=3.0,
                        max_area=5.0,
                        needs_exterior_wall=False,
                        needs_window=False,
                        is_stairwell=True,
                        floor=floor_idx,
                    ))

            program.floors.append(floor)

        return program


def _is_template_dict(tmpl) -> bool:
    """True for a building template: a BSP template (has floors) or a grid template."""
    return isinstance(tmpl, dict) and (
        tmpl.get("layout_type") == "grid" or bool(tmpl.get("floors"))
    )


def is_building_template(path: Path) -> bool:
    """True if the YAML file at path is a building type template."""
    with open(path) as f:
        return _is_template_dict(yaml.safe_load(f))


def _vary(base: float, var: float, rng: random.Random) -> float:
    """Apply random variation to a base value."""
    return base + rng.uniform(-var, var)
