"""3D building visualization using matplotlib.

Renders 3D views of buildings without requiring GPU/OpenGL.
Uses matplotlib's mplot3d projection to draw building elements
as colored 3D boxes from multiple viewpoints.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

from ..layout.models import FloorPlan, WallType
from ..style.models import StyleParams


def render_3d_views(
    floor_plans: list[FloorPlan],
    style: StyleParams,
    output_path: str | Path,
    title: str = "Building",
) -> Path:
    """Render 3D building views from multiple angles.

    Creates a 2x2 grid: perspective, front elevation, side elevation, top.
    """
    fig = plt.figure(figsize=(16, 14))

    views = [
        ("Perspective", 25, -55),
        ("Front Elevation", 5, -90),
        ("Side Elevation", 5, 0),
        ("Aerial View", 75, -60),
    ]

    for idx, (view_name, elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 2, idx + 1, projection="3d")
        _draw_building_3d(ax, floor_plans, style)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(view_name, fontsize=11, fontweight="bold")
        ax.set_xlabel("X (m)", fontsize=7)
        ax.set_ylabel("Z (m)", fontsize=7)
        ax.set_zlabel("Y (m)", fontsize=7)
        ax.tick_params(labelsize=6)

    fig.suptitle(title, fontsize=16, fontweight="bold")
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def _draw_building_3d(
    ax: Axes3D,
    floor_plans: list[FloorPlan],
    style: StyleParams,
) -> None:
    """Draw the full building in 3D."""

    for plan in floor_plans:
        floor_y = plan.floor_index * style.floor_height

        # Draw floor slab
        if plan.footprint:
            b = plan.footprint.bounds
            _draw_box(
                ax, b[0], floor_y, b[1],
                b[2], floor_y + style.slab_thickness, b[3],
                color=(0.8, 0.8, 0.8, 0.3), edge_color=(0.5, 0.5, 0.5, 0.5),
            )

        # Draw walls
        for wall in plan.walls:
            sx, sy = wall.start
            ex, ey = wall.end

            dx = ex - sx
            dy = ey - sy
            length = (dx**2 + dy**2) ** 0.5
            if length < 0.01:
                continue

            nx = -dy / length
            ny = dx / length

            is_ext = wall.wall_type == WallType.EXTERIOR
            t = 0.15 if is_ext else 0.06

            if is_ext:
                color = (0.75, 0.50, 0.33, 0.85)  # Brick
                edge_c = (0.4, 0.25, 0.15, 0.6)
            else:
                color = (0.9, 0.88, 0.85, 0.5)  # Plaster
                edge_c = (0.6, 0.6, 0.6, 0.4)

            # Wall as 4 corner points extruded vertically
            corners_base = [
                (sx + nx * t, sy + ny * t),
                (sx - nx * t, sy - ny * t),
                (ex - nx * t, ey - ny * t),
                (ex + nx * t, ey + ny * t),
            ]

            y_bot = floor_y
            y_top = floor_y + style.floor_height

            verts = []
            for cx, cz in corners_base:
                verts.append([cx, y_bot, cz])
            for cx, cz in corners_base:
                verts.append([cx, y_top, cz])

            # 6 faces of the wall box
            faces = [
                [verts[0], verts[1], verts[2], verts[3]],  # bottom
                [verts[4], verts[5], verts[6], verts[7]],  # top
                [verts[0], verts[1], verts[5], verts[4]],  # front
                [verts[2], verts[3], verts[7], verts[6]],  # back
                [verts[0], verts[3], verts[7], verts[4]],  # left
                [verts[1], verts[2], verts[6], verts[5]],  # right
            ]

            poly = Poly3DCollection(faces, alpha=color[3])
            poly.set_facecolor(color[:3])
            poly.set_edgecolor(edge_c[:3])
            poly.set_linewidth(0.3)
            ax.add_collection3d(poly)

        # Draw room labels at floor level
        for room in plan.rooms:
            if room.room_type == "stairwell":
                continue
            cx, cz = room.centroid
            ax.text(
                cx, floor_y + 0.5, cz,
                room.name.replace("_", "\n"),
                fontsize=3.5, ha="center", va="bottom",
                color=(0.3, 0.3, 0.3),
            )

    # Draw roof
    if floor_plans and floor_plans[-1].footprint:
        _draw_roof(ax, floor_plans[-1], style)

    # Set equal aspect
    if floor_plans and floor_plans[0].footprint:
        b = floor_plans[0].footprint.bounds
        max_dim = max(b[2] - b[0], b[3] - b[1],
                      len(floor_plans) * style.floor_height)
        ax.set_xlim(b[0] - 1, b[0] + max_dim + 1)
        ax.set_ylim(-0.5, max_dim + 1)
        ax.set_zlim(b[1] - 1, b[1] + max_dim + 1)


def _draw_roof(ax: Axes3D, top_plan: FloorPlan, style: StyleParams) -> None:
    """Draw the roof as a 3D shape."""
    if not top_plan.footprint:
        return

    b = top_plan.footprint.bounds
    roof_y = (top_plan.floor_index + 1) * style.floor_height
    w = b[2] - b[0]
    d = b[3] - b[1]

    ridge_h = style.roof_pitch * min(w, d) / 2
    mid_x = (b[0] + b[2]) / 2
    ovh = style.roof_overhang

    if style.roof_type == "hip":
        inset = min(w, d) / 2
        ridge_z1 = b[1] + inset
        ridge_z2 = b[3] - inset

        # 4 hip faces
        faces = [
            # Front hip
            [[b[0] - ovh, roof_y, b[1] - ovh],
             [b[2] + ovh, roof_y, b[1] - ovh],
             [mid_x, roof_y + ridge_h, ridge_z1]],
            # Back hip
            [[b[2] + ovh, roof_y, b[3] + ovh],
             [b[0] - ovh, roof_y, b[3] + ovh],
             [mid_x, roof_y + ridge_h, ridge_z2]],
            # Left slope
            [[b[0] - ovh, roof_y, b[1] - ovh],
             [mid_x, roof_y + ridge_h, ridge_z1],
             [mid_x, roof_y + ridge_h, ridge_z2],
             [b[0] - ovh, roof_y, b[3] + ovh]],
            # Right slope
            [[b[2] + ovh, roof_y, b[1] - ovh],
             [b[2] + ovh, roof_y, b[3] + ovh],
             [mid_x, roof_y + ridge_h, ridge_z2],
             [mid_x, roof_y + ridge_h, ridge_z1]],
        ]
    else:
        # Gable roof
        faces = [
            # Left slope
            [[b[0] - ovh, roof_y, b[1] - ovh],
             [mid_x, roof_y + ridge_h, b[1] - ovh],
             [mid_x, roof_y + ridge_h, b[3] + ovh],
             [b[0] - ovh, roof_y, b[3] + ovh]],
            # Right slope
            [[b[2] + ovh, roof_y, b[1] - ovh],
             [b[2] + ovh, roof_y, b[3] + ovh],
             [mid_x, roof_y + ridge_h, b[3] + ovh],
             [mid_x, roof_y + ridge_h, b[1] - ovh]],
            # Front gable
            [[b[0] - ovh, roof_y, b[1] - ovh],
             [b[2] + ovh, roof_y, b[1] - ovh],
             [mid_x, roof_y + ridge_h, b[1] - ovh]],
            # Back gable
            [[b[0] - ovh, roof_y, b[3] + ovh],
             [mid_x, roof_y + ridge_h, b[3] + ovh],
             [b[2] + ovh, roof_y, b[3] + ovh]],
        ]

    roof_color = (0.32, 0.28, 0.25, 0.85)  # Dark slate
    poly = Poly3DCollection(faces, alpha=0.85)
    poly.set_facecolor(roof_color[:3])
    poly.set_edgecolor((0.2, 0.18, 0.15))
    poly.set_linewidth(0.5)
    ax.add_collection3d(poly)


def _draw_box(
    ax: Axes3D,
    x0: float, y0: float, z0: float,
    x1: float, y1: float, z1: float,
    color: tuple = (0.8, 0.8, 0.8, 0.5),
    edge_color: tuple = (0.5, 0.5, 0.5, 0.5),
) -> None:
    """Draw an axis-aligned box in 3D."""
    verts = [
        [x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1],
        [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1],
    ]
    faces = [
        [verts[0], verts[1], verts[2], verts[3]],
        [verts[4], verts[5], verts[6], verts[7]],
        [verts[0], verts[1], verts[5], verts[4]],
        [verts[2], verts[3], verts[7], verts[6]],
        [verts[0], verts[3], verts[7], verts[4]],
        [verts[1], verts[2], verts[6], verts[5]],
    ]
    poly = Poly3DCollection(faces, alpha=color[3])
    poly.set_facecolor(color[:3])
    poly.set_edgecolor(edge_color[:3])
    poly.set_linewidth(0.3)
    ax.add_collection3d(poly)
