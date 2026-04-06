"""Roof type selection rules.

Maps building_type + style + period to the correct roof type and pitch.
Based on ROOF_TYPES_REFERENCE.md research.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RoofSpec:
    """Specification for a building's roof."""
    roof_type: str        # hip, gable, mansard, flat, etc.
    pitch_deg: float      # Primary pitch angle
    has_parapet: bool = False
    parapet_height: float = 0.0  # metres above eaves
    covering: str = "slate"      # slate, tile, lead, thatch
    dormer_count: int = 0
    dormer_side: str = "rear"    # front, rear, both


# Period-specific defaults
_PERIOD_DEFAULTS = {
    "medieval": {"pitch": 50.0, "covering": "thatch"},
    "tudor": {"pitch": 50.0, "covering": "clay_tile"},
    "georgian": {"pitch": 30.0, "covering": "slate"},
    "regency": {"pitch": 28.0, "covering": "slate"},
    "victorian": {"pitch": 38.0, "covering": "slate"},
    "edwardian": {"pitch": 35.0, "covering": "clay_tile"},
    "modern": {"pitch": 30.0, "covering": "concrete_tile"},
}


def select_roof(
    building_type: str,
    style: str = "georgian",
    period: str = "georgian",
    form: str = "terraced",
    location: str = "london",
) -> RoofSpec:
    """Select the correct roof type for a building.

    Args:
        building_type: townhouse, cottage, tavern, church, barn, etc.
        style: architectural style
        period: historical period
        form: terraced, detached, semi_detached
        location: london, provincial, rural
    """
    defaults = _PERIOD_DEFAULTS.get(period, _PERIOD_DEFAULTS["georgian"])

    # ── Georgian residential ──
    if period == "georgian" and building_type in ("townhouse", "townhouse_reference"):
        spec = RoofSpec(
            roof_type="hip",
            pitch_deg=defaults["pitch"],
            covering="slate",
        )
        if location == "london" or form == "terraced":
            spec.has_parapet = True
            spec.parapet_height = 0.450  # 18 inches, 1707 Building Act
        return spec

    # ── Victorian terrace ──
    if period == "victorian" and building_type == "victorian_terrace":
        return RoofSpec(
            roof_type="gable",
            pitch_deg=38.0,
            covering="slate",
        )

    # ── Cottage ──
    if building_type == "cottage":
        if period in ("medieval", "tudor"):
            return RoofSpec(roof_type="gable", pitch_deg=50.0, covering="thatch")
        return RoofSpec(roof_type="gable", pitch_deg=40.0, covering="slate")

    # ── Tavern / inn ──
    if building_type == "tavern":
        if period in ("medieval", "tudor"):
            return RoofSpec(roof_type="gable", pitch_deg=48.0, covering="clay_tile")
        return RoofSpec(roof_type="gable", pitch_deg=38.0, covering="slate")

    # ── Church ──
    if building_type in ("church", "chapel"):
        if period in ("medieval", "tudor"):
            return RoofSpec(roof_type="gable", pitch_deg=55.0, covering="lead")
        if style == "gothic_revival":
            return RoofSpec(roof_type="gable", pitch_deg=60.0, covering="slate")
        return RoofSpec(roof_type="gable", pitch_deg=40.0, covering="slate")

    # ── Castle ──
    if building_type == "castle":
        return RoofSpec(roof_type="gable", pitch_deg=50.0, covering="lead")

    # ── Barn ──
    if building_type == "barn":
        return RoofSpec(roof_type="gable", pitch_deg=45.0, covering="clay_tile")

    # ── Industrial / warehouse ──
    if building_type in ("factory", "warehouse", "mill"):
        if period == "victorian":
            return RoofSpec(roof_type="gable", pitch_deg=25.0, covering="slate")
        return RoofSpec(roof_type="flat", pitch_deg=3.0, covering="felt")

    # ── Mansion / country house ──
    if building_type in ("mansion", "manor", "country_house"):
        if period == "georgian":
            return RoofSpec(
                roof_type="hip", pitch_deg=28.0,
                covering="slate", has_parapet=True, parapet_height=0.450,
            )
        return RoofSpec(roof_type="hip", pitch_deg=32.0, covering="slate")

    # ── Default ──
    return RoofSpec(
        roof_type=defaults.get("roof_type", "gable"),
        pitch_deg=defaults["pitch"],
        covering=defaults["covering"],
    )


# ── Structural members required per roof type ──

ROOF_MEMBERS = {
    "gable": {
        "common_rafters": True,
        "ridge_board": True,
        "hip_rafters": False,
        "jack_rafters": False,
        "valley_rafters": False,
        "purlins": True,  # If span > 3.4m
        "tie_beams": True,
        "collar_ties": True,
        "wall_plates": True,
        "gable_wall": True,  # Triangular brick wall at each end
    },
    "hip": {
        "common_rafters": True,
        "ridge_board": True,  # Shorter than building
        "hip_rafters": True,  # 4 diagonal from corners
        "jack_rafters": True,  # Shortened rafters in hip zones
        "valley_rafters": False,
        "purlins": True,
        "tie_beams": True,
        "collar_ties": False,
        "wall_plates": True,  # On all 4 walls
        "gable_wall": False,
    },
    "mansard": {
        "common_rafters": True,  # Two sets (steep lower, shallow upper)
        "ridge_board": True,
        "hip_rafters": True,  # If hipped mansard
        "jack_rafters": True,
        "valley_rafters": False,
        "purlins": True,
        "tie_beams": True,
        "collar_ties": False,
        "wall_plates": True,
        "gable_wall": False,
        "mansard_curb": True,  # Horizontal timber at pitch change
    },
    "flat": {
        "common_rafters": False,
        "ridge_board": False,
        "hip_rafters": False,
        "jack_rafters": False,
        "valley_rafters": False,
        "purlins": False,
        "tie_beams": False,
        "collar_ties": False,
        "wall_plates": True,
        "gable_wall": False,
        "flat_joists": True,  # Flat joists with slight fall
    },
    "lean_to": {
        "common_rafters": True,  # Single slope
        "ridge_board": False,
        "hip_rafters": False,
        "jack_rafters": False,
        "valley_rafters": False,
        "purlins": True,
        "tie_beams": False,
        "collar_ties": False,
        "wall_plates": True,
        "gable_wall": True,  # At each end
    },
}
