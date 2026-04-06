"""3D geometry generator (Pipeline Stage 3).

Extrudes 2D floor plans into 3D building meshes with walls,
floors, roofs, windows, doors, and stairs.

Public API:
    - GeometryBuilder: main class, takes floor plans + style -> Building3D
    - Building3D: complete 3D building mesh with metadata
"""

from .builder import GeometryBuilder
from .models import Building3D

__all__ = ["GeometryBuilder", "Building3D"]
