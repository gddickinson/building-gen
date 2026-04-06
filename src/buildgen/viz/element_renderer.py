"""Render individual building elements to 3D mesh or 2D diagram.

Converts an ElementCollection into a trimesh Scene where every
brick, joist, slate, glass pane etc. is a visible mesh with
appropriate color based on material.

For performance, small elements (nails, mortar joints) can be
filtered out, and elements can be shown by type or floor.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from ..engineering.elements import Element, ElementType, ElementCollection
from ..engineering.materials.properties import MATERIALS_DB


# Material colors (RGBA 0-255)
_MAT_COLORS: dict[str, list[int]] = {
    "facing_brick": [190, 120, 80, 255],
    "common_brick": [170, 110, 75, 255],
    "engineering_brick": [100, 60, 55, 255],
    "mortar_lime": [220, 215, 200, 255],
    "mortar_cement": [200, 200, 195, 255],
    "limestone": [220, 210, 185, 255],
    "sandstone": [200, 180, 145, 255],
    "granite": [160, 160, 170, 255],
    "softwood_c16": [210, 180, 130, 255],
    "softwood_c24": [200, 170, 120, 255],
    "oak": [160, 120, 75, 255],
    "mild_steel": [180, 180, 190, 255],
    "cast_iron": [85, 85, 90, 255],
    "wrought_iron": [110, 105, 100, 255],
    "float_glass": [180, 210, 240, 120],
    "cob": [180, 165, 135, 255],
    "lime_plaster": [240, 235, 225, 255],
    "roofing_slate": [80, 85, 95, 255],
    "clay_roof_tile": [175, 95, 60, 255],
}


def elements_to_scene(
    collection: ElementCollection,
    skip_mortar: bool = True,
    skip_nails: bool = True,
    skip_plaster: bool = False,
    max_elements: int = 0,
    floor_filter: int = -1,
    type_filter: str = "",
) -> trimesh.Scene:
    """Convert an ElementCollection to a viewable 3D scene.

    Args:
        collection: The element collection to render
        skip_mortar: Skip mortar joints (saves geometry)
        skip_nails: Skip nails and small fixings
        skip_plaster: Skip plaster surfaces
        max_elements: Limit elements (0 = no limit)
        floor_filter: Only show elements on this floor (-1 = all)
        type_filter: Only show elements of this type ("" = all)

    Returns:
        trimesh.Scene with all visible elements
    """
    scene = trimesh.Scene()
    count = 0

    for element in collection.elements:
        # Apply filters
        if skip_mortar and element.element_type == ElementType.MORTAR_JOINT:
            continue
        if skip_nails and element.element_type == ElementType.NAIL:
            continue
        if skip_plaster and element.element_type == ElementType.PLASTER:
            continue
        if floor_filter >= 0 and element.floor_index != floor_filter:
            continue
        if type_filter and element.element_type.value != type_filter:
            continue

        mesh = _element_to_mesh(element)
        if mesh is not None:
            scene.add_geometry(mesh, node_name=f"e_{count}")
            count += 1

        if max_elements > 0 and count >= max_elements:
            break

    return scene


def render_element_summary(
    collection: ElementCollection,
    output_path: str | Path,
) -> Path:
    """Render a summary diagram of the building's elements.

    Shows element counts, material breakdown, and structural checks
    as a matplotlib figure.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(18, 8))

    # Panel 1: Element counts by type (bar chart)
    counts = collection.count_by_type()
    # Filter to top 15
    sorted_counts = sorted(counts.items(), key=lambda x: -x[1])[:15]
    types = [t for t, c in sorted_counts]
    vals = [c for t, c in sorted_counts]

    ax1 = axes[0]
    bars = ax1.barh(range(len(types)), vals, color="#5B8C5A")
    ax1.set_yticks(range(len(types)))
    ax1.set_yticklabels(types, fontsize=8)
    ax1.set_xlabel("Count")
    ax1.set_title(f"Elements by Type ({collection.total_count:,} total)", fontweight="bold")
    for i, v in enumerate(vals):
        ax1.text(v + max(vals) * 0.01, i, f"{v:,}", va="center", fontsize=7)
    ax1.invert_yaxis()

    # Panel 2: Material mass breakdown (pie chart)
    masses = collection.mass_by_material()
    sorted_masses = sorted(masses.items(), key=lambda x: -x[1])
    # Combine small entries
    top_n = 8
    labels = [m for m, kg in sorted_masses[:top_n]]
    sizes = [kg for m, kg in sorted_masses[:top_n]]
    other = sum(kg for m, kg in sorted_masses[top_n:])
    if other > 0:
        labels.append("other")
        sizes.append(other)

    ax2 = axes[1]
    colors = [_get_pie_color(l) for l in labels]
    wedges, texts, autotexts = ax2.pie(
        sizes, labels=None, autopct="%1.0f%%",
        colors=colors, pctdistance=0.8,
        textprops={"fontsize": 7},
    )
    ax2.legend(
        labels, loc="lower left", fontsize=7,
        title="Material", title_fontsize=8,
    )
    ax2.set_title(
        f"Mass by Material ({collection.total_mass/1000:.1f}t)",
        fontweight="bold",
    )

    # Panel 3: Structural summary text
    ax3 = axes[2]
    ax3.axis("off")

    failed = collection.check_all_stresses()

    summary_text = (
        f"STRUCTURAL SUMMARY\n"
        f"{'=' * 35}\n\n"
        f"Total elements: {collection.total_count:,}\n"
        f"Total mass: {collection.total_mass:,.0f} kg\n"
        f"Total weight: {collection.total_weight:,.0f} kN\n"
        f"  ({collection.total_mass/1000:.1f} tonnes)\n\n"
        f"Stress checks:\n"
        f"  Passed: {collection.total_count - len(failed):,}\n"
        f"  Failed: {len(failed)}\n"
        f"  Status: {'PASS' if not failed else 'FAIL'}\n\n"
        f"Elements per floor:\n"
    )

    floor_counts: dict[int, int] = {}
    floor_masses: dict[int, float] = {}
    for e in collection.elements:
        f = e.floor_index
        floor_counts[f] = floor_counts.get(f, 0) + 1
        floor_masses[f] = floor_masses.get(f, 0) + e.mass

    for f in sorted(floor_counts.keys()):
        summary_text += (
            f"  Floor {f}: {floor_counts[f]:,} elements, "
            f"{floor_masses[f]/1000:.1f}t\n"
        )

    if failed:
        summary_text += f"\nFailed elements:\n"
        for e in failed[:5]:
            summary_text += (
                f"  {e.element_type.value}: "
                f"{e.stress_notes}\n"
            )

    ax3.text(
        0.05, 0.95, summary_text,
        transform=ax3.transAxes,
        fontsize=9, fontfamily="monospace",
        verticalalignment="top",
    )

    fig.suptitle(
        "Building Element Analysis",
        fontsize=16, fontweight="bold",
    )
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path


def _element_to_mesh(element: Element) -> trimesh.Trimesh | None:
    """Convert a single Element to a trimesh box."""
    if element.length <= 0 or element.width <= 0 or element.height <= 0:
        return None

    # Create box at origin
    mesh = trimesh.creation.box(
        extents=[element.length, element.height, element.width],
    )

    # Translate to element position (Y is up)
    mesh.apply_translation([element.x, element.y, element.z])

    # Apply color from material
    color = _MAT_COLORS.get(
        element.material_name,
        [180, 180, 180, 255],
    )
    mesh.visual.face_colors = color

    return mesh


def _get_pie_color(material_name: str) -> str:
    """Get a hex color for the pie chart."""
    color_map = {
        "facing_brick": "#BE7850",
        "engineering_brick": "#6E3C37",
        "common_brick": "#AA6E4B",
        "mortar_lime": "#DCD7C8",
        "softwood_c24": "#C8AA78",
        "softwood_c16": "#D2B482",
        "roofing_slate": "#50555F",
        "lime_plaster": "#F0EBE1",
        "limestone": "#DCD2B9",
        "oak": "#A07848",
        "clay_roof_tile": "#AF5F3C",
        "cast_iron": "#55555A",
        "float_glass": "#B4D2F0",
        "wrought_iron": "#6E6964",
        "other": "#CCCCCC",
    }
    return color_map.get(material_name, "#AAAAAA")
