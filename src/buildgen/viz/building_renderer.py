"""3D building rendering and screenshot generation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from ..geometry.models import Building3D
from ..layout.models import FloorPlan


def screenshot_3d(
    building: Building3D,
    output_path: str | Path,
    resolution: tuple[int, int] = (1200, 900),
    angles: list[str] | None = None,
) -> list[Path]:
    """Render 3D building to PNG screenshots from multiple angles.

    Args:
        building: Building3D to render
        output_path: base path (e.g., "output/house") — angle suffix added
        angles: list of view angles ("front", "side", "top", "perspective")

    Returns:
        list of saved file paths
    """
    if angles is None:
        angles = ["perspective", "front", "side", "top"]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []
    scene = building.mesh

    for angle_name in angles:
        camera_transform = _get_camera_transform(scene, angle_name)

        try:
            # Use trimesh's offscreen rendering
            png_data = scene.save_image(
                resolution=resolution,
                visible=False,
            )

            if png_data:
                file_path = output_path.parent / (
                    f"{output_path.stem}_{angle_name}.png"
                )
                with open(file_path, "wb") as f:
                    f.write(png_data)
                saved_paths.append(file_path)

        except Exception as e:
            print(f"  Warning: 3D render '{angle_name}' failed: {e}")

    return saved_paths


def render_building_sheet(
    building: Building3D,
    floor_plans: list[FloorPlan],
    output_path: str | Path,
    building_title: str = "Building",
) -> Path:
    """Render a complete building overview sheet with plans and 3D views.

    Creates a composite image with floor plans on the left
    and building info on the right.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from .floor_plan_renderer import render_floor_plan

    n_floors = len(floor_plans)
    n_cols = n_floors + 1  # floors + info panel

    fig, axes = plt.subplots(
        1, n_cols,
        figsize=(6 * n_cols, 8),
        gridspec_kw={"width_ratios": [1] * n_floors + [0.8]},
    )

    if n_cols == 1:
        axes = [axes]

    # Render floor plans
    for i, plan in enumerate(floor_plans):
        render_floor_plan(
            plan, ax=axes[i],
            title=f"Floor {plan.floor_index}",
        )

    # Info panel
    info_ax = axes[-1]
    info_ax.axis("off")
    info_text = (
        f"{building_title}\n"
        f"{'=' * 30}\n\n"
        f"Floors: {building.num_floors}\n"
        f"Footprint: {building.footprint_area:.1f} m\u00b2\n"
        f"Total floor area: {building.total_floor_area:.1f} m\u00b2\n"
        f"Style: {building.style}\n"
        f"Seed: {building.seed}\n\n"
        f"Rooms per floor:\n"
    )
    for plan in floor_plans:
        info_text += f"\n  Floor {plan.floor_index}:\n"
        for room in sorted(plan.rooms, key=lambda r: r.name):
            info_text += f"    {room.name}: {room.area:.1f}m\u00b2\n"

    # Add structural data if available
    try:
        from ..engineering import design_structure, calculate_loads
        fp_w = floor_plans[0].footprint.bounds[2] if floor_plans else 8.0
        fp_d = floor_plans[0].footprint.bounds[3] if floor_plans else 10.0
        struct = design_structure(fp_w, fp_d, building.num_floors)
        loads = calculate_loads(struct)

        info_text += f"\n--- Structure ---\n"
        info_text += f"Material: {struct.wall_material}\n"
        info_text += f"Ext wall: {struct.walls[0].thickness*1000:.0f}mm\n"
        info_text += f"LB walls: {len(struct.load_bearing_walls)}\n"
        info_text += f"Joist span: {struct.floors[0].max_span:.1f}m\n"
        info_text += f"Joist depth: {struct.floors[0].depth*1000:.0f}mm\n"
        info_text += f"Foundation: {struct.foundation_type}\n"
        info_text += f"Found width: {loads.required_foundation_width:.2f}m\n"
        info_text += f"Load/m: {loads.foundation_load_per_m:.0f}kN/m\n"
        info_text += f"Roof thrust: {loads.roof_thrust:.1f}kN/m\n"
    except Exception:
        pass

    info_ax.text(
        0.05, 0.95, info_text,
        transform=info_ax.transAxes,
        fontsize=8, fontfamily="monospace",
        verticalalignment="top",
    )

    fig.suptitle(building_title, fontsize=16, fontweight="bold")
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path


def _get_camera_transform(
    scene: trimesh.Scene, angle: str
) -> np.ndarray:
    """Get camera transform matrix for a named viewing angle."""
    bounds = scene.bounds
    center = (bounds[0] + bounds[1]) / 2.0
    size = np.linalg.norm(bounds[1] - bounds[0])
    dist = size * 2.0

    # The street front faces +z (plan y runs to -z, see geometry/builder.py)
    if angle == "front":
        eye = center + np.array([0, size * 0.3, dist])
    elif angle == "side":
        eye = center + np.array([dist, size * 0.3, 0])
    elif angle == "top":
        eye = center + np.array([0, dist, 0.01])
    else:  # perspective
        eye = center + np.array([dist * 0.7, size * 0.6, dist * 0.7])

    return _look_at(eye, center)


def _look_at(
    eye: np.ndarray, target: np.ndarray, up: np.ndarray | None = None
) -> np.ndarray:
    """Create a look-at camera transform matrix."""
    if up is None:
        up = np.array([0, 1, 0], dtype=np.float64)

    forward = target - eye
    forward = forward / np.linalg.norm(forward)

    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)

    true_up = np.cross(right, forward)

    transform = np.eye(4)
    transform[:3, 0] = right
    transform[:3, 1] = true_up
    transform[:3, 2] = -forward
    transform[:3, 3] = eye

    return transform
