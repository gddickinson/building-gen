"""Structural engineering module.

Designs buildings from engineering first principles:
1. Define the building envelope (outer walls, foundation, roof)
2. Calculate structural loads (dead load, live load, roof thrust)
3. Size load-bearing walls, lintels, and foundations
4. Then subdivide the interior with non-load-bearing partitions

The building must stand up before rooms go inside it.

Public API:
    - StructuralModel: the complete structural model of a building
    - WallClassification: load-bearing vs partition designation
    - LoadCalculation: forces acting on each element
    - MaterialSpec: material strength and properties
    - design_structure: create a structural model from footprint + floors
    - validate_structure: check a building is structurally sound
"""

from .model import StructuralModel, WallClassification, LoadPath
from .loads import LoadCalculation, calculate_loads
from .design import design_structure

__all__ = [
    "StructuralModel",
    "WallClassification",
    "LoadPath",
    "LoadCalculation",
    "calculate_loads",
    "design_structure",
]
