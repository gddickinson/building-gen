"""Data models for architectural style parameters."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StyleParams:
    """Complete style parameters for building generation."""
    name: str = "default"

    # Dimensions
    floor_height: float = 3.0          # metres
    slab_thickness: float = 0.25       # metres
    wall_thickness: float = 0.3        # metres
    window_width: float = 1.0          # metres
    window_height: float = 1.4         # metres
    window_sill_height: float = 0.9    # metres
    door_width: float = 0.9            # metres
    door_height: float = 2.1           # metres
    front_door_width: float = 1.1      # metres
    front_door_height: float = 2.4     # metres

    # Roof
    roof_type: str = "gable"           # gable, hip, flat
    roof_pitch: float = 0.45           # rise/run ratio
    roof_overhang: float = 0.3         # metres beyond walls

    # Stairs
    stair_riser: float = 0.18          # metres per step
    stair_tread: float = 0.28          # metres depth

    # Colors (RGBA 0-255)
    exterior_wall_color: list[int] = field(
        default_factory=lambda: [180, 120, 80, 255]  # Brick
    )
    interior_wall_color: list[int] = field(
        default_factory=lambda: [240, 235, 220, 255]  # Plaster
    )
    roof_color: list[int] = field(
        default_factory=lambda: [80, 60, 50, 255]  # Dark slate
    )
    floor_color: list[int] = field(
        default_factory=lambda: [200, 200, 200, 255]  # Grey
    )
    stair_color: list[int] = field(
        default_factory=lambda: [160, 120, 80, 255]  # Wood
    )
    window_color: list[int] = field(
        default_factory=lambda: [150, 180, 220, 200]  # Glass blue
    )
    door_color: list[int] = field(
        default_factory=lambda: [100, 70, 50, 255]  # Dark wood
    )

    # Window rhythm
    window_bay_spacing: float = 2.0    # metres between window centres
    min_window_edge_dist: float = 0.5  # min distance from wall corner

    # Attic / Dormers
    has_attic: bool = False
    attic_usable: bool = False         # Can attic be used as rooms
    num_dormers: int = 0               # Number of dormer windows
    dormer_width: float = 1.2          # metres
    dormer_height: float = 1.6         # metres
    dormer_type: str = "gable"         # gable, hip, shed

    # Porch / Entry
    has_porch: bool = False
    porch_depth: float = 1.5           # metres
    porch_width: float = 2.0           # metres
    porch_columns: int = 2             # Number of porch columns

    # Chimney
    has_chimney: bool = True
    chimney_width: float = 0.8         # metres
    chimney_depth: float = 0.6         # metres

    # Facade
    symmetrical_facade: bool = True
    ornament_level: float = 0.5        # 0.0 = plain, 1.0 = ornate

    # Exterior wall pattern
    exterior_wall_pattern: str = "brick"  # brick, stone, timber, stucco, clapboard
