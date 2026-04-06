"""Material science database with real engineering properties.

Every material has measured physical properties that determine what
you can build with it. These are not approximations — they come from
BS EN standards, engineering handbooks, and material test data.

Public API:
    - Material: complete material specification
    - BRICK, MORTAR, STONE, TIMBER, STEEL, etc.: material instances
    - get_material: look up a material by name
    - check_stress: verify an element isn't overstressed
"""

from .properties import (
    Material,
    MATERIALS_DB,
    get_material,
    check_compressive_stress,
    check_tensile_stress,
    check_bending_stress,
    check_shear_stress,
)

__all__ = [
    "Material",
    "MATERIALS_DB",
    "get_material",
    "check_compressive_stress",
    "check_tensile_stress",
    "check_bending_stress",
    "check_shear_stress",
]
