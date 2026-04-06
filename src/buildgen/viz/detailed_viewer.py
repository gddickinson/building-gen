"""Detailed building viewer — renders granular element models.

Generates multiple diagnostic views of a building at the
individual element level:

1. Exterior views (4 elevations + perspective)
2. Floor-by-floor cutaway plans (top-down, one floor at a time)
3. Cross-section (cut through the building vertically)
4. Exploded view (floors separated vertically)
5. System views (structure only, roof only, windows only, etc.)

Each element is drawn as a colored rectangle/box based on its
material. Elements can be filtered by type, floor, or system.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import numpy as np

from ..engineering.elements import Element, ElementType, ElementCollection


# Material colors for 2D rendering
_COLORS: dict[str, str] = {
    "facing_brick": "#BE7850",
    "common_brick": "#AA6E4B",
    "engineering_brick": "#6E3C37",
    "mortar_lime": "#DCD7C8",
    "mortar_cement": "#C8C8C3",
    "limestone": "#DCD2B9",
    "sandstone": "#C8B48C",
    "granite": "#A0A0A5",
    "softwood_c16": "#D2B482",
    "softwood_c24": "#C8AA78",
    "oak": "#A07848",
    "mild_steel": "#B4B4BE",
    "cast_iron": "#555560",
    "wrought_iron": "#6E6964",
    "float_glass": "#B4D2F0",
    "lime_plaster": "#F0EBE1",
    "roofing_slate": "#505560",
    "clay_roof_tile": "#AF5F3C",
    "cob": "#B4A587",
}

# Which element types to show by default (skip mortar for clarity)
_SKIP_TYPES = {
    ElementType.MORTAR_JOINT,
    ElementType.NAIL,
}


def render_full_diagnostic(
    collection: ElementCollection,
    output_dir: str | Path,
    building_width: float,
    building_depth: float,
    num_floors: int,
    floor_height: float,
    title: str = "Building",
) -> list[Path]:
    """Render a complete set of diagnostic views.

    Returns list of saved file paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    # 1. Front elevation (XY plane, looking from south at z=0)
    p = _render_elevation(
        collection, output_dir / "elev_front.png",
        "x", "y", z_filter=0, z_range=0.5,
        title=f"{title} — Front Elevation",
        width=building_width, height=num_floors * floor_height,
    )
    saved.append(p)

    # 2. Side elevation (ZY plane, looking from west at x=0)
    p = _render_elevation(
        collection, output_dir / "elev_side.png",
        "z", "y", z_filter=0, z_range=0.5,
        title=f"{title} — Side Elevation (West)",
        width=building_depth, height=num_floors * floor_height,
        axis_name="x",
    )
    saved.append(p)

    # 3. Floor-by-floor cutaway (XZ plan view, one per floor)
    p = _render_floor_cutaways(
        collection, output_dir / "floor_cutaways.png",
        num_floors, floor_height,
        building_width, building_depth,
        title=f"{title} — Floor Cutaways",
    )
    saved.append(p)

    # 4. Cross-section (XY plane, cut through middle of building)
    p = _render_cross_section(
        collection, output_dir / "cross_section.png",
        cut_z=building_depth / 2, cut_width=1.5,
        building_width=building_width,
        total_height=num_floors * floor_height + 4,
        title=f"{title} — Cross Section",
    )
    saved.append(p)

    # 5. Exploded view (floors separated)
    p = _render_exploded(
        collection, output_dir / "exploded.png",
        num_floors, floor_height,
        building_width, building_depth,
        title=f"{title} — Exploded View",
    )
    saved.append(p)

    # 6. System views (structure, roof, windows)
    p = _render_systems(
        collection, output_dir / "systems.png",
        building_width, building_depth,
        num_floors, floor_height,
        title=f"{title} — Building Systems",
    )
    saved.append(p)

    return saved


def _render_elevation(
    coll: ElementCollection,
    output_path: Path,
    h_axis: str, v_axis: str,
    z_filter: float, z_range: float,
    title: str,
    width: float, height: float,
    axis_name: str = "z",
) -> Path:
    """Render an elevation view (front or side)."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    for e in coll.elements:
        if e.element_type in _SKIP_TYPES:
            continue

        # Filter to elements near the viewing plane
        if axis_name == "z":
            dist = abs(e.z - z_filter)
        else:
            dist = abs(e.x - z_filter)

        if dist > z_range and e.element_type not in (
            ElementType.SLATE, ElementType.TILE,
            ElementType.RIDGE_BOARD, ElementType.RAFTER,
        ):
            # Show all roof elements regardless of z
            if e.y < height * 0.8:
                continue

        # Map element position to 2D
        if h_axis == "x":
            ex, ey = e.x, e.y
            ew, eh = e.length, e.height
        else:
            ex, ey = e.z, e.y
            ew, eh = e.width, e.height

        if ew < 0.001 or eh < 0.001:
            continue

        color = _COLORS.get(e.material_name, "#AAAAAA")
        alpha = 0.9 if e.element_type != ElementType.GLASS_PANE else 0.4

        rect = patches.Rectangle(
            (ex - ew / 2, ey - eh / 2), ew, eh,
            facecolor=color, edgecolor="none",
            alpha=alpha, linewidth=0,
        )
        ax.add_patch(rect)

    # Draw ground line
    ax.axhline(y=0, color="#4a3728", linewidth=2)
    ax.fill_between([-1, width + 1], [-0.5, -0.5], [0, 0],
                     color="#6B8E4E", alpha=0.3)

    ax.set_xlim(-0.5, width + 0.5)
    ax.set_ylim(-0.5, height + 3)
    ax.set_aspect("equal")
    ax.set_xlabel("metres", fontsize=9)
    ax.set_ylabel("height (m)", fontsize=9)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.15, linestyle=":")

    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def _render_floor_cutaways(
    coll: ElementCollection,
    output_path: Path,
    num_floors: int,
    floor_height: float,
    width: float, depth: float,
    title: str,
) -> Path:
    """Render top-down plan view of each floor showing all elements."""
    fig, axes = plt.subplots(1, num_floors, figsize=(7 * num_floors, 8))
    if num_floors == 1:
        axes = [axes]

    for floor_idx, ax in enumerate(axes):
        y_min = floor_idx * floor_height
        y_max = y_min + floor_height
        # Cut at 1.2m above floor (through windows, above doors)
        cut_y = y_min + 1.2

        for e in coll.elements:
            if e.element_type in _SKIP_TYPES:
                continue

            # Only show elements that intersect this floor's height range
            e_bottom = e.y - e.height / 2
            e_top = e.y + e.height / 2

            if e_top < y_min or e_bottom > y_max:
                continue

            # For plan view: only show elements that the cut plane
            # passes through (walls, windows) or floor elements at this level
            is_wall_cut = (e_bottom <= cut_y <= e_top)
            is_floor_elem = e.element_type in (
                ElementType.JOIST, ElementType.FLOORBOARD,
                ElementType.WALL_PLATE, ElementType.STUD,
            )
            is_stair = e.element_type in (ElementType.BEAM, ElementType.COLUMN)

            # Show walls cut at the cut height, floors at floor level, stairs always
            if not is_wall_cut and not is_floor_elem and not is_stair:
                continue

            color = _COLORS.get(e.material_name, "#AAAAAA")

            # Plan view: X horizontal, Z vertical
            if e.element_type in (ElementType.BRICK, ElementType.STONE_BLOCK):
                # Cut bricks shown solid with hatching
                alpha = 0.9
                edge = "#222222"
                lw = 0.15
            elif e.element_type == ElementType.GLASS_PANE:
                alpha = 0.5
                edge = "#4472C4"
                lw = 0.8
                color = "#C0DCF5"
            elif e.element_type in (ElementType.JOIST,):
                alpha = 0.4
                edge = "#997755"
                lw = 0.3
            elif e.element_type == ElementType.FLOORBOARD:
                alpha = 0.2  # Very faint — just background
                edge = "none"
                lw = 0
            elif e.element_type in (ElementType.WINDOW_FRAME, ElementType.WINDOW_SASH,
                                     ElementType.DOOR_FRAME, ElementType.DOOR_LEAF):
                alpha = 0.7
                edge = "#666666"
                lw = 0.4
            elif e.element_type == ElementType.LINTEL:
                alpha = 0.8
                edge = "#665544"
                lw = 0.5
            else:
                alpha = 0.4
                edge = "none"
                lw = 0

            rect = patches.Rectangle(
                (e.x - e.length / 2, e.z - e.width / 2),
                e.length, e.width,
                facecolor=color, edgecolor=edge,
                alpha=alpha, linewidth=lw,
            )
            ax.add_patch(rect)

        ax.set_xlim(-0.3, width + 0.3)
        ax.set_ylim(-0.3, depth + 0.3)
        ax.set_aspect("equal")
        ax.set_title(f"Floor {floor_idx} (cut at {cut_y:.1f}m)",
                     fontsize=11, fontweight="bold")
        ax.set_xlabel("X (m)", fontsize=8)
        ax.set_ylabel("Z (m)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(True, alpha=0.1, linestyle=":")

    fig.suptitle(title, fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def _render_cross_section(
    coll: ElementCollection,
    output_path: Path,
    cut_z: float,
    cut_width: float,
    building_width: float,
    total_height: float,
    title: str,
) -> Path:
    """Render a vertical cross-section through the building."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    # Background (cut face)
    ax.fill_between(
        [0, building_width], [0, 0], [total_height, total_height],
        color="#FFF8F0", alpha=0.3,
    )

    for e in coll.elements:
        if e.element_type in _SKIP_TYPES:
            continue

        # Only show elements near the cut plane
        e_z_min = e.z - e.width / 2
        e_z_max = e.z + e.width / 2

        if e_z_min > cut_z + cut_width or e_z_max < cut_z - cut_width:
            # Exception: show roof elements everywhere
            if e.element_type not in (
                ElementType.RAFTER, ElementType.RIDGE_BOARD,
                ElementType.TIE_BEAM, ElementType.PURLIN,
                ElementType.SLATE, ElementType.TILE,
            ):
                continue

        color = _COLORS.get(e.material_name, "#AAAAAA")

        # Section view: X horizontal, Y vertical
        ew = e.length
        eh = e.height
        if ew < 0.001 or eh < 0.001:
            continue

        # Hatching for cut elements (walls cut through)
        is_cut = (e_z_min < cut_z < e_z_max)

        if e.element_type == ElementType.BRICK and is_cut:
            # Cross-hatched brick in section
            rect = patches.Rectangle(
                (e.x - ew / 2, e.y - eh / 2), ew, eh,
                facecolor=color, edgecolor="#444",
                alpha=0.9, linewidth=0.2,
                hatch="//",
            )
        elif e.element_type == ElementType.JOIST:
            rect = patches.Rectangle(
                (e.x - ew / 2, e.y - eh / 2), ew, eh,
                facecolor=color, edgecolor="#8B7355",
                alpha=0.8, linewidth=0.5,
            )
        elif e.element_type == ElementType.RAFTER:
            rect = patches.Rectangle(
                (e.x - ew / 2, e.y - eh / 2), ew, eh,
                facecolor=color, edgecolor="#8B7355",
                alpha=0.8, linewidth=0.5,
            )
        elif e.element_type == ElementType.GLASS_PANE:
            rect = patches.Rectangle(
                (e.x - ew / 2, e.y - eh / 2), ew, eh,
                facecolor="#CCE5FF", edgecolor="#4472C4",
                alpha=0.5, linewidth=0.8,
            )
        else:
            alpha = 0.7 if is_cut else 0.4
            rect = patches.Rectangle(
                (e.x - ew / 2, e.y - eh / 2), ew, eh,
                facecolor=color, edgecolor="none",
                alpha=alpha, linewidth=0,
            )

        ax.add_patch(rect)

    # Ground
    ax.axhline(y=0, color="#4a3728", linewidth=2)
    ax.fill_between([-1, building_width + 1], [-1, -1], [0, 0],
                     color="#8B7355", alpha=0.3)

    # Foundation
    ax.fill_between([-0.5, building_width + 0.5], [-0.8, -0.8], [0, 0],
                     color="#555555", alpha=0.2)

    ax.set_xlim(-1, building_width + 1)
    ax.set_ylim(-1, total_height)
    ax.set_aspect("equal")
    ax.set_xlabel("Width (m)", fontsize=10)
    ax.set_ylabel("Height (m)", fontsize=10)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.15, linestyle=":")

    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def _render_exploded(
    coll: ElementCollection,
    output_path: Path,
    num_floors: int,
    floor_height: float,
    width: float, depth: float,
    title: str,
) -> Path:
    """Render an exploded axonometric view with floors separated."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 16))

    gap = floor_height * 0.8  # Gap between exploded floors
    iso_angle = math.radians(30)

    for floor_idx in range(num_floors):
        y_min = floor_idx * floor_height
        y_max = y_min + floor_height
        y_offset = floor_idx * gap  # Extra vertical separation

        for e in coll.elements:
            if e.element_type in _SKIP_TYPES:
                continue
            if e.element_type in (ElementType.CEILING_LATH, ElementType.PLASTER):
                continue

            e_bottom = e.y - e.height / 2
            e_top = e.y + e.height / 2

            if e_top < y_min or e_bottom > y_max:
                continue

            color = _COLORS.get(e.material_name, "#AAAAAA")

            # Isometric projection: x' = x + z*cos(30), y' = y + z*sin(30)
            iso_x = e.x + e.z * math.cos(iso_angle) * 0.5
            iso_y = e.y + y_offset + e.z * math.sin(iso_angle) * 0.5

            ew = e.length + e.width * math.cos(iso_angle) * 0.3
            eh = e.height

            if ew < 0.005 or eh < 0.005:
                continue

            alpha = 0.8
            if e.element_type == ElementType.GLASS_PANE:
                alpha = 0.3
            elif e.element_type in (ElementType.FLOORBOARD, ElementType.JOIST):
                alpha = 0.5

            rect = patches.Rectangle(
                (iso_x - ew / 2, iso_y - eh / 2), ew, eh,
                facecolor=color, edgecolor="none",
                alpha=alpha, linewidth=0,
            )
            ax.add_patch(rect)

        # Floor label
        label_x = width * 0.5
        label_y = y_min + y_offset + floor_height / 2
        ax.text(
            -1, label_y, f"Floor {floor_idx}",
            fontsize=11, fontweight="bold", color="#333",
            ha="right", va="center",
        )

    # Roof elements (above top floor)
    roof_y_min = num_floors * floor_height
    roof_offset = num_floors * gap
    for e in coll.elements:
        if e.element_type in _SKIP_TYPES:
            continue
        if e.y < roof_y_min - 0.1:
            continue
        if e.element_type in (ElementType.CEILING_LATH, ElementType.PLASTER):
            continue

        color = _COLORS.get(e.material_name, "#AAAAAA")
        iso_x = e.x + e.z * math.cos(iso_angle) * 0.5
        iso_y = e.y + roof_offset + e.z * math.sin(iso_angle) * 0.5
        ew = max(e.length, e.width) * 0.8
        eh = max(e.height, 0.02)

        rect = patches.Rectangle(
            (iso_x - ew / 2, iso_y - eh / 2), ew, eh,
            facecolor=color, edgecolor="none",
            alpha=0.7, linewidth=0,
        )
        ax.add_patch(rect)

    ax.text(-1, roof_y_min + roof_offset, "Roof",
            fontsize=11, fontweight="bold", color="#333",
            ha="right", va="center")

    total_h = (num_floors + 1) * (floor_height + gap)
    ax.set_xlim(-2, width + depth * 0.5 + 1)
    ax.set_ylim(-1, total_h + 2)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.axis("off")

    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def _render_systems(
    coll: ElementCollection,
    output_path: Path,
    width: float, depth: float,
    num_floors: int, floor_height: float,
    title: str,
) -> Path:
    """Render building systems in isolation (structure, roof, windows, stairs)."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    systems = [
        ("Structure (Bricks)", {ElementType.BRICK, ElementType.STONE_BLOCK,
                                 ElementType.FOUNDATION}, "x", "y"),
        ("Roof Structure", {ElementType.RAFTER, ElementType.RIDGE_BOARD,
                            ElementType.PURLIN, ElementType.TIE_BEAM,
                            ElementType.WALL_PLATE}, "x", "y"),
        ("Roof Covering", {ElementType.SLATE, ElementType.TILE}, "x", "z"),
        ("Floor Structure", {ElementType.JOIST, ElementType.FLOORBOARD,
                             ElementType.STUD}, "x", "y"),
        ("Windows & Doors", {ElementType.WINDOW_FRAME, ElementType.WINDOW_SASH,
                             ElementType.GLAZING_BAR, ElementType.GLASS_PANE,
                             ElementType.DOOR_FRAME, ElementType.DOOR_LEAF,
                             ElementType.LINTEL}, "x", "y"),
        ("Stairs", {ElementType.BEAM, ElementType.COLUMN,
                    ElementType.FLOORBOARD}, "z", "y"),
    ]

    for idx, (sys_name, type_set, h_ax, v_ax) in enumerate(systems):
        ax = axes[idx // 3][idx % 3]

        for e in coll.elements:
            if e.element_type not in type_set:
                continue

            color = _COLORS.get(e.material_name, "#AAAAAA")

            if h_ax == "x":
                ex, ew = e.x, e.length
            else:
                ex, ew = e.z, e.width

            if v_ax == "y":
                ey, eh = e.y, e.height
            else:
                ey, eh = e.z, e.width

            if ew < 0.001 or eh < 0.001:
                continue

            alpha = 0.8
            if e.element_type == ElementType.GLASS_PANE:
                alpha = 0.4

            rect = patches.Rectangle(
                (ex - ew / 2, ey - eh / 2), ew, eh,
                facecolor=color, edgecolor="none",
                alpha=alpha, linewidth=0,
            )
            ax.add_patch(rect)

        count = len([e for e in coll.elements if e.element_type in type_set])
        ax.set_title(f"{sys_name} ({count:,})", fontsize=10, fontweight="bold")
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.1, linestyle=":")
        ax.tick_params(labelsize=6)

        if h_ax == "x":
            ax.set_xlim(-0.5, width + 0.5)
        else:
            ax.set_xlim(-0.5, depth + 0.5)

        if v_ax == "y":
            ax.set_ylim(-1, num_floors * floor_height + 5)
        else:
            ax.set_ylim(-0.5, depth + 0.5)

    fig.suptitle(title, fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path
