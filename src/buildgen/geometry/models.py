"""Data models for 3D building geometry."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import trimesh
import numpy as np


@dataclass
class Building3D:
    """Complete 3D building with mesh and metadata."""
    mesh: trimesh.Scene
    building_type: str = ""
    style: str = ""
    num_floors: int = 0
    footprint_area: float = 0.0
    total_floor_area: float = 0.0
    seed: int = 0

    def export(self, path: str | Path, file_type: str | None = None) -> None:
        """Export the building mesh to a file."""
        path = Path(path)
        if file_type is None:
            file_type = path.suffix.lstrip(".")
        self.mesh.export(str(path), file_type=file_type)

    @property
    def bounds(self) -> np.ndarray:
        """Bounding box as (min_point, max_point)."""
        return self.mesh.bounds
