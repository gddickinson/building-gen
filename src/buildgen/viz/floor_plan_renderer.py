"""2D floor plan rendering with architectural drawing conventions.

Draws proper wall thicknesses, door swings, window marks in walls,
stair arrows, fixture symbols, and dimension annotations.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Arc, FancyArrowPatch
import numpy as np

from ..layout.models import FloorPlan, Opening, OpeningType, WallType
from ..layout.fixtures import Fixture, FixtureType
from .fixture_renderer import draw_room_fixtures, FIXTURE_SYMBOLS


# Room type fill colors (light architectural tints)
_ROOM_COLORS: dict[str, str] = {
    "entrance_hall": "#F5EDE0",
    "hallway": "#F5EDE0",
    "landing": "#F5EDE0",
    "parlour": "#E8F0E0",
    "drawing_room": "#E8F0E0",
    "dining_room": "#DEEAF0",
    "kitchen": "#F0E4DA",
    "scullery": "#EDE8E0",
    "pantry": "#EDE8E0",
    "wc": "#E0E0EE",
    "bathroom": "#DAF0F0",
    "bedroom": "#EDE0F0",
    "master_bedroom": "#E0D8EE",
    "dressing_room": "#EDE0E8",
    "nursery": "#F5EDE0",
    "servants_quarters": "#E8E8E0",
    "study": "#DEE8DE",
    "library": "#D8E0D8",
    "storage": "#E8E8E8",
    "stairwell": "#FFF8E0",
    "generic": "#F0F0F0",
}


def render_floor_plan(
    plan: FloorPlan,
    output_path: str | Path | None = None,
    ax: plt.Axes | None = None,
    title: str | None = None,
    show_fixtures: bool = True,
    show_dimensions: bool = True,
) -> plt.Figure | None:
    """Render a floor plan using architectural drawing conventions."""
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(1, 1, figsize=(10, 12))
    else:
        fig = ax.figure

    # 1. Draw room fills
    for room in plan.rooms:
        color = _ROOM_COLORS.get(room.room_type, "#F0F0F0")
        coords = list(room.polygon.exterior.coords)
        poly_patch = patches.Polygon(
            coords, closed=True,
            facecolor=color, edgecolor="none",
            alpha=0.9,
        )
        ax.add_patch(poly_patch)

    # 2. Draw walls with proper thickness
    _draw_walls(ax, plan)

    # 3. Draw openings (doors with swings, windows with marks)
    for room in plan.rooms:
        for opening in room.openings:
            _draw_opening(ax, opening, plan)

    # 4. Draw stair indicators
    for room in plan.rooms:
        if room.room_type == "stairwell":
            _draw_stairs(ax, room)

    # 5. Draw fixtures
    if show_fixtures:
        for room in plan.rooms:
            _draw_room_fixtures(ax, room)

    # 6. Room labels
    for room in plan.rooms:
        cx, cy = room.centroid
        label = room.name.replace("_", " ").title()
        area_str = f"{room.area:.1f}m\u00b2"
        ax.text(
            cx, cy, f"{label}\n{area_str}",
            ha="center", va="center",
            fontsize=6.5, fontweight="bold",
            color="#444444", style="italic",
        )

    # 7. Dimensions
    if show_dimensions and plan.footprint:
        _draw_dimensions(ax, plan)

    # Formatting
    if plan.footprint:
        b = plan.footprint.bounds
        margin = 1.5
        ax.set_xlim(b[0] - margin, b[2] + margin)
        ax.set_ylim(b[1] - margin, b[3] + margin)

    ax.set_aspect("equal")
    ax.grid(True, alpha=0.1, linestyle=":")

    if title is None:
        title = f"Floor {plan.floor_index}"
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("metres", fontsize=9)
    ax.set_ylabel("metres", fontsize=9)
    ax.tick_params(labelsize=7)

    if standalone and output_path:
        fig.tight_layout()
        fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
        plt.close(fig)
        return None

    return fig


def _draw_walls(ax: plt.Axes, plan: FloorPlan) -> None:
    """Draw walls with proper thickness — thick for exterior, thin for interior."""
    for wall in plan.walls:
        sx, sy = wall.start
        ex, ey = wall.end

        dx = ex - sx
        dy = ey - sy
        length = math.hypot(dx, dy)
        if length < 0.01:
            continue

        # Wall thickness in drawing
        if wall.wall_type == WallType.EXTERIOR:
            t = 0.15  # Draw exterior walls thick
            color = "#1a1a1a"
            fill_color = "#2a2a2a"
        else:
            t = 0.06  # Interior walls thinner
            color = "#444444"
            fill_color = "#555555"

        # Normal perpendicular to wall
        nx = -dy / length * t
        ny = dx / length * t

        # Wall rectangle
        corners = [
            (sx + nx, sy + ny),
            (sx - nx, sy - ny),
            (ex - nx, ey - ny),
            (ex + nx, ey + ny),
        ]
        wall_patch = patches.Polygon(
            corners, closed=True,
            facecolor=fill_color, edgecolor=color,
            linewidth=0.5, zorder=3,
        )
        ax.add_patch(wall_patch)


def _draw_opening(
    ax: plt.Axes, opening: Opening, plan: FloorPlan
) -> None:
    """Draw door with swing arc or window with parallel lines."""
    ox, oy = opening.position

    if opening.opening_type in (OpeningType.DOOR, OpeningType.FRONT_DOOR):
        _draw_door_swing(ax, opening)
    elif opening.opening_type == OpeningType.WINDOW:
        _draw_window_mark(ax, opening, plan)


def _draw_door_swing(ax: plt.Axes, opening: Opening) -> None:
    """Draw a door with a 90-degree swing arc (architectural convention)."""
    ox, oy = opening.position
    w = opening.width
    is_front = opening.opening_type == OpeningType.FRONT_DOOR

    # Clear the wall where the door is
    clear = patches.Circle(
        (ox, oy), w * 0.15,
        facecolor="white", edgecolor="none", zorder=4,
    )
    ax.add_patch(clear)

    # Door leaf (line)
    color = "#8B4513" if is_front else "#666666"
    lw = 2.0 if is_front else 1.2

    # Draw the door leaf as a line from hinge to edge
    ax.plot(
        [ox - w / 2, ox + w / 2],
        [oy, oy],
        color=color, linewidth=lw, zorder=5,
        solid_capstyle="round",
    )

    # Draw the swing arc
    arc = Arc(
        (ox - w / 2, oy), w, w,
        angle=0, theta1=0, theta2=90,
        color=color, linewidth=0.8,
        linestyle="--", zorder=5,
    )
    ax.add_patch(arc)

    if is_front:
        ax.annotate(
            "ENTRY", (ox, oy),
            fontsize=5, ha="center", va="top",
            color="#8B4513", fontweight="bold",
            xytext=(0, -10), textcoords="offset points",
            zorder=6,
        )


def _draw_window_mark(
    ax: plt.Axes, opening: Opening, plan: FloorPlan
) -> None:
    """Draw window as a gap in the wall with parallel lines (architectural convention)."""
    ox, oy = opening.position
    w = opening.width / 2

    # Determine wall orientation by checking which footprint edge we're near
    if plan.footprint:
        b = plan.footprint.bounds
        # Distance to each edge
        dist_bottom = abs(oy - b[1])
        dist_top = abs(oy - b[3])
        dist_left = abs(ox - b[0])
        dist_right = abs(ox - b[2])
        min_dist = min(dist_bottom, dist_top, dist_left, dist_right)

        if min_dist == dist_bottom or min_dist == dist_top:
            # Horizontal wall — window runs left-right
            # Three parallel lines (architectural window symbol)
            for offset in [-0.06, 0, 0.06]:
                ax.plot(
                    [ox - w, ox + w],
                    [oy + offset, oy + offset],
                    color="#4472C4", linewidth=1.2, zorder=5,
                )
            # Glass fill
            rect = patches.Rectangle(
                (ox - w, oy - 0.06), w * 2, 0.12,
                facecolor="#C5D9F0", edgecolor="none",
                alpha=0.5, zorder=4,
            )
            ax.add_patch(rect)
        else:
            # Vertical wall — window runs up-down
            for offset in [-0.06, 0, 0.06]:
                ax.plot(
                    [ox + offset, ox + offset],
                    [oy - w, oy + w],
                    color="#4472C4", linewidth=1.2, zorder=5,
                )
            rect = patches.Rectangle(
                (ox - 0.06, oy - w), 0.12, w * 2,
                facecolor="#C5D9F0", edgecolor="none",
                alpha=0.5, zorder=4,
            )
            ax.add_patch(rect)


def _draw_stairs(ax: plt.Axes, room) -> None:
    """Draw stair indication with parallel treads and an arrow."""
    b = room.bounds
    minx, miny, maxx, maxy = b
    sw = maxx - minx
    sh = maxy - miny
    margin = 0.15

    # Draw tread lines
    if sh >= sw:
        # Stairs run vertically
        num_treads = max(3, int(sh / 0.28))
        step = (sh - 2 * margin) / num_treads
        for i in range(num_treads + 1):
            y = miny + margin + i * step
            ax.plot(
                [minx + margin, maxx - margin],
                [y, y],
                color="#888888", linewidth=0.6, zorder=3,
            )
        # Arrow indicating "up"
        ax.annotate(
            "", xy=(minx + sw / 2, maxy - margin * 2),
            xytext=(minx + sw / 2, miny + sh * 0.4),
            arrowprops=dict(
                arrowstyle="->", color="#333333",
                lw=1.5,
            ),
            zorder=4,
        )
        ax.text(
            minx + sw / 2, miny + sh * 0.35,
            "UP", ha="center", va="center",
            fontsize=7, fontweight="bold", color="#333333",
            zorder=4,
        )
    else:
        # Stairs run horizontally
        num_treads = max(3, int(sw / 0.28))
        step = (sw - 2 * margin) / num_treads
        for i in range(num_treads + 1):
            x = minx + margin + i * step
            ax.plot(
                [x, x],
                [miny + margin, maxy - margin],
                color="#888888", linewidth=0.6, zorder=3,
            )
        ax.annotate(
            "", xy=(maxx - margin * 2, miny + sh / 2),
            xytext=(minx + sw * 0.4, miny + sh / 2),
            arrowprops=dict(
                arrowstyle="->", color="#333333", lw=1.5,
            ),
            zorder=4,
        )
        ax.text(
            minx + sw * 0.35, miny + sh / 2,
            "UP", ha="center", va="center",
            fontsize=7, fontweight="bold", color="#333333",
            zorder=4,
        )


def _draw_room_fixtures(ax: plt.Axes, room) -> None:
    """Draw fixture symbols inside a room. Delegates to fixture_renderer."""
    draw_room_fixtures(ax, room)


def _draw_dimensions(ax: plt.Axes, plan: FloorPlan) -> None:
    """Draw overall dimension lines outside the building."""
    if not plan.footprint:
        return

    b = plan.footprint.bounds
    minx, miny, maxx, maxy = b
    offset = 0.8

    # Bottom dimension (width)
    y_dim = miny - offset
    ax.annotate(
        "", xy=(maxx, y_dim), xytext=(minx, y_dim),
        arrowprops=dict(arrowstyle="<->", color="#666", lw=0.8),
    )
    ax.text(
        (minx + maxx) / 2, y_dim - 0.15,
        f"{maxx - minx:.1f}m",
        ha="center", va="top", fontsize=7, color="#666",
    )

    # Left dimension (depth)
    x_dim = minx - offset
    ax.annotate(
        "", xy=(x_dim, maxy), xytext=(x_dim, miny),
        arrowprops=dict(arrowstyle="<->", color="#666", lw=0.8),
    )
    ax.text(
        x_dim - 0.15, (miny + maxy) / 2,
        f"{maxy - miny:.1f}m",
        ha="right", va="center", fontsize=7, color="#666",
        rotation=90,
    )


def render_all_floors(
    plans: list[FloorPlan],
    output_path: str | Path,
    building_title: str = "Building Floor Plans",
) -> None:
    """Render all floor plans side by side to a single PNG."""
    n = len(plans)
    fig, axes = plt.subplots(1, n, figsize=(8 * n, 10))

    if n == 1:
        axes = [axes]

    for plan, ax in zip(plans, axes):
        render_floor_plan(
            plan, ax=ax,
            title=f"Floor {plan.floor_index}",
        )

    fig.suptitle(building_title, fontsize=18, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
