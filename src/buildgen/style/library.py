"""Style library — loads and provides style parameters."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import StyleParams


# Built-in styles that don't require YAML files
_BUILTIN_STYLES: dict[str, dict] = {
    "georgian": {
        "name": "georgian",
        "floor_height": 3.2,
        "slab_thickness": 0.25,
        "wall_thickness": 0.35,
        "window_width": 1.05,
        "window_height": 1.6,
        "window_sill_height": 0.85,
        "door_width": 0.9,
        "door_height": 2.1,
        "front_door_width": 1.2,
        "front_door_height": 2.5,
        "roof_type": "hip",
        "roof_pitch": 0.4,
        "roof_overhang": 0.25,
        "stair_riser": 0.19,
        "exterior_wall_color": [190, 130, 85, 255],
        "interior_wall_color": [240, 235, 225, 255],
        "roof_color": [70, 65, 60, 255],
        "stair_color": [150, 110, 70, 255],
        "window_bay_spacing": 2.4,
        "has_attic": True,
        "attic_usable": False,
        "num_dormers": 2,
        "dormer_width": 1.2,
        "dormer_type": "gable",
        "has_porch": True,
        "porch_depth": 1.2,
        "porch_width": 2.4,
        "porch_columns": 2,
        "has_chimney": True,
        "chimney_width": 0.8,
        "chimney_depth": 0.6,
        "symmetrical_facade": True,
        "ornament_level": 0.6,
        "exterior_wall_pattern": "brick",
    },
}


class StyleLibrary:
    """Loads and provides StyleParams by name.

    Usage:
        lib = StyleLibrary()
        style = lib.get("georgian")
    """

    def __init__(self, style_dir: Path | None = None):
        if style_dir is None:
            style_dir = Path(__file__).parent / "styles"
        self.style_dir = style_dir
        self._cache: dict[str, StyleParams] = {}

    def available_styles(self) -> list[str]:
        """List available style names."""
        names = list(_BUILTIN_STYLES.keys())
        if self.style_dir.exists():
            names.extend(p.stem for p in self.style_dir.glob("*.yaml"))
        return sorted(set(names))

    def get(self, name: str) -> StyleParams:
        """Get StyleParams by name."""
        if name in self._cache:
            return self._cache[name]

        params = self._load(name)
        self._cache[name] = params
        return params

    def _load(self, name: str) -> StyleParams:
        """Load a style by name."""
        # Check built-in styles first
        if name in _BUILTIN_STYLES:
            return StyleParams(**_BUILTIN_STYLES[name])

        # Try YAML file
        yaml_path = self.style_dir / f"{name}.yaml"
        if yaml_path.exists():
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            return StyleParams(**data)

        raise ValueError(
            f"Unknown style '{name}'. "
            f"Available: {self.available_styles()}"
        )
