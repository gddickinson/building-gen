"""Individual structural elements — the atoms of a building.

Every physical piece of a building is an Element with:
- Exact position (x, y, z) and rotation
- Material with engineering properties
- Dimensions (length, width, height)
- Forces acting on it (compression, tension, bending, shear)
- Stress check results (pass/fail against material limits)

Element types:
- Brick: individual masonry unit with mortar joints
- MortarJoint: mortar between bricks
- Joist: timber/steel floor beam
- Rafter: timber roof beam
- Beam/Lintel: spanning element over openings
- Column: vertical compression member
- WindowFrame: timber/metal window components
- DoorFrame: timber door frame components
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

from .materials.properties import Material, MATERIALS_DB


class ElementType(str, Enum):
    BRICK = "brick"
    MORTAR_JOINT = "mortar_joint"
    STONE_BLOCK = "stone_block"
    JOIST = "joist"
    BEAM = "beam"
    LINTEL = "lintel"
    RAFTER = "rafter"
    RIDGE_BOARD = "ridge_board"
    PURLIN = "purlin"
    TIE_BEAM = "tie_beam"
    WALL_PLATE = "wall_plate"
    COLUMN = "column"
    STUD = "stud"           # Timber frame vertical
    SOLE_PLATE = "sole_plate"
    HEAD_PLATE = "head_plate"
    FLOORBOARD = "floorboard"
    CEILING_LATH = "ceiling_lath"
    WINDOW_FRAME = "window_frame"
    WINDOW_SASH = "window_sash"
    GLAZING_BAR = "glazing_bar"
    GLASS_PANE = "glass_pane"
    DOOR_FRAME = "door_frame"
    DOOR_LEAF = "door_leaf"
    SLATE = "slate"
    TILE = "tile"
    FOUNDATION = "foundation"
    PLASTER = "plaster"
    NAIL = "nail"
    HINGE = "hinge"


@dataclass
class Element:
    """A single physical building element."""
    element_type: ElementType
    material_name: str

    # Position (centre point, in metres from building origin)
    x: float = 0.0
    y: float = 0.0      # Height (vertical axis)
    z: float = 0.0

    # Dimensions (metres)
    length: float = 0.0  # Along primary axis
    width: float = 0.0   # Across primary axis
    height: float = 0.0  # Vertical (or thickness for horizontal elements)

    # Rotation (degrees around Y axis)
    rotation: float = 0.0

    # Which wall/floor/component this belongs to
    parent: str = ""     # e.g., "wall_north", "floor_1", "window_0_3"
    floor_index: int = 0

    # Forces acting on this element (kN unless noted)
    compression: float = 0.0   # kN — vertical compression
    tension: float = 0.0       # kN — vertical tension
    shear: float = 0.0         # kN — horizontal shear
    bending_moment: float = 0.0  # kN·m — bending moment

    # Stress check results
    stress_ok: bool = True
    stress_ratio: float = 0.0   # actual/allowable (< 1.0 is OK)
    stress_notes: str = ""

    @property
    def material(self) -> Material:
        return MATERIALS_DB[self.material_name]

    @property
    def volume(self) -> float:
        """Volume in m³."""
        return self.length * self.width * self.height

    @property
    def mass(self) -> float:
        """Mass in kg."""
        return self.volume * self.material.density

    @property
    def weight(self) -> float:
        """Weight in kN."""
        return self.mass * 9.81 / 1000

    @property
    def cross_section_area(self) -> float:
        """Cross-section area in m² (width * height)."""
        return self.width * self.height

    def check_stresses(self) -> None:
        """Check all stresses against material limits."""
        mat = self.material
        max_ratio = 0.0
        notes = []

        # Compressive stress
        if self.compression > 0 and self.cross_section_area > 0:
            actual = (self.compression * 1e3) / (self.cross_section_area * 1e6)
            allowable = mat.design_compressive
            ratio = actual / allowable if allowable > 0 else 999
            max_ratio = max(max_ratio, ratio)
            if ratio > 1.0:
                notes.append(f"COMP {actual:.2f}/{allowable:.2f} MPa")

        # Bending stress (for beams/joists/lintels)
        if self.bending_moment > 0 and self.width > 0 and self.height > 0:
            # Section modulus Z = bh²/6
            z_mod = self.width * self.height ** 2 / 6  # m³
            actual = (self.bending_moment * 1e3) / (z_mod * 1e9)
            allowable = mat.design_flexural
            ratio = actual / allowable if allowable > 0 else 999
            max_ratio = max(max_ratio, ratio)
            if ratio > 1.0:
                notes.append(f"BEND {actual:.2f}/{allowable:.2f} MPa")

        # Shear stress
        if self.shear > 0 and self.cross_section_area > 0:
            actual = (self.shear * 1e3) / (self.cross_section_area * 1e6)
            allowable = mat.shear_strength / mat.gamma_m
            ratio = actual / allowable if allowable > 0 else 999
            max_ratio = max(max_ratio, ratio)
            if ratio > 1.0:
                notes.append(f"SHEAR {actual:.2f}/{allowable:.2f} MPa")

        self.stress_ratio = max_ratio
        self.stress_ok = max_ratio <= 1.0
        self.stress_notes = "; ".join(notes) if notes else "OK"


@dataclass
class ElementCollection:
    """A collection of all elements in a building."""
    elements: list[Element] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return len(self.elements)

    @property
    def total_mass(self) -> float:
        """Total mass in kg."""
        return sum(e.mass for e in self.elements)

    @property
    def total_weight(self) -> float:
        """Total weight in kN."""
        return sum(e.weight for e in self.elements)

    def by_type(self, element_type: ElementType) -> list[Element]:
        return [e for e in self.elements if e.element_type == element_type]

    def by_floor(self, floor_index: int) -> list[Element]:
        return [e for e in self.elements if e.floor_index == floor_index]

    def by_parent(self, parent: str) -> list[Element]:
        return [e for e in self.elements if e.parent == parent]

    def count_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self.elements:
            t = e.element_type.value
            counts[t] = counts.get(t, 0) + 1
        return counts

    def mass_by_material(self) -> dict[str, float]:
        masses: dict[str, float] = {}
        for e in self.elements:
            masses[e.material_name] = masses.get(e.material_name, 0) + e.mass
        return masses

    def check_all_stresses(self) -> list[Element]:
        """Check stresses on all elements. Returns failed elements."""
        failed = []
        for e in self.elements:
            e.check_stresses()
            if not e.stress_ok:
                failed.append(e)
        return failed

    def summary(self) -> str:
        counts = self.count_by_type()
        masses = self.mass_by_material()
        lines = [
            f"Building Elements: {self.total_count:,} total",
            f"Total mass: {self.total_mass:,.0f} kg ({self.total_weight:,.0f} kN)",
            "",
            "By type:",
        ]
        for t, c in sorted(counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {t:20s}: {c:,}")
        lines.append("")
        lines.append("By material (kg):")
        for m, kg in sorted(masses.items(), key=lambda x: -x[1]):
            lines.append(f"  {m:20s}: {kg:,.0f} kg")
        return "\n".join(lines)
