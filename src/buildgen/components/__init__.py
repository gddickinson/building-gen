"""Shared building component library.

Standard building elements reusable across all building types.
Each component is defined with dimensions, variants, and period
applicability so the right version is selected for each style.

Public API:
    - DOORS: door type catalogue (panel, plank, glazed, etc.)
    - WINDOWS: window type catalogue (sash, casement, lancet, etc.)
    - WALLS: wall construction types (brick, stone, timber, etc.)
    - FIREPLACES: fireplace/hearth types by period
    - FURNITURE: standard furniture items with dimensions
    - APPLIANCES: kitchen/bathroom appliances
    - ROOF_FEATURES: dormers, chimneys, cupolas, etc.
    - ARCHITECTURAL_DETAILS: cornices, columns, arches, etc.
    - get_components_for_style: filter components by architectural style
"""

from .catalogue import (
    DOORS,
    WINDOWS,
    WALLS,
    FIREPLACES,
    FURNITURE,
    APPLIANCES,
    ROOF_FEATURES,
    ARCHITECTURAL_DETAILS,
    get_components_for_style,
)

__all__ = [
    "DOORS",
    "WINDOWS",
    "WALLS",
    "FIREPLACES",
    "FURNITURE",
    "APPLIANCES",
    "ROOF_FEATURES",
    "ARCHITECTURAL_DETAILS",
    "get_components_for_style",
]
