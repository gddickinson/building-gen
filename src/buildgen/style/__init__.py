"""Style and detail system (Pipeline Stage 4).

Manages architectural style parameters that control proportions,
materials, colors, roof types, and ornament across different
periods and regions.

Public API:
    - StyleLibrary: loads and provides StyleParams by name
    - StyleParams: complete set of style parameters for geometry generation
"""

from .models import StyleParams
from .library import StyleLibrary

__all__ = ["StyleLibrary", "StyleParams"]
