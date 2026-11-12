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
        # Software render with matplotlib: the trimesh/pyglet off-screen
        # renderer needed pyglet (not installed by default) and an OpenGL
        # context, failed silently and never used camera_transform.
        png_data = render_scene_png(scene, camera_transform, resolution)
        file_path = output_path.parent / f"{output_path.stem}_{angle_name}.png"
        with open(file_path, "wb") as f:
            f.write(png_data)
        saved_paths.append(file_path)

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


def render_scene_png(
    scene: trimesh.Scene,
    camera_transform: np.ndarray,
    resolution: tuple[int, int] = (1200, 900),
    fov_deg: float = 30.0,
) -> bytes:
    """Render the scene's triangles to PNG bytes from a camera (camera-to-world matrix looking down -z).

    A small software rasteriser (numpy z-buffer, flat-shaded face colours on white), so it needs no
    OpenGL or pyglet. Raises ValueError if no triangle is in front of the camera.
    """
    import io

    from PIL import Image

    tris, cols = [], []
    for node in scene.graph.nodes_geometry:
        transform, name = scene.graph[node]
        mesh = scene.geometry[name]
        if len(mesh.faces) == 0:
            continue
        tris.append(trimesh.transform_points(mesh.vertices, transform)[mesh.faces])
        cols.append(np.asarray(mesh.visual.face_colors, dtype=np.float64)[:, :3])
    if not tris:
        raise ValueError("scene has no triangles to render")
    tris = np.concatenate(tris)
    cols = np.concatenate(cols)

    world_to_cam = np.linalg.inv(camera_transform)
    cam = tris @ world_to_cam[:3, :3].T + world_to_cam[:3, 3]
    depth = -cam[:, :, 2]
    keep = (depth > 1e-3).all(axis=1)
    if not keep.any():
        raise ValueError("no geometry in front of the camera")
    tris, cols, cam, depth = tris[keep], cols[keep], cam[keep], depth[keep]

    # Flat shading: key light plus ambient, two-sided
    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    normals = normals / np.where(lengths > 0, lengths, 1.0)[:, None]
    light = np.array([0.45, 0.8, 0.35]) / np.linalg.norm([0.45, 0.8, 0.35])
    colours = np.clip(cols * (0.45 + 0.55 * np.abs(normals @ light))[:, None], 0, 255)

    w, h = resolution
    f = (h / 2.0) / np.tan(np.radians(fov_deg) / 2.0)
    px = w / 2.0 + cam[:, :, 0] / depth * f
    py = h / 2.0 - cam[:, :, 1] / depth * f

    image = np.full((h, w, 3), 255.0)
    zbuf = np.full((h, w), np.inf)
    for t in range(len(tris)):
        x, y, z = px[t], py[t], depth[t]
        x0, x1 = max(int(np.floor(x.min())), 0), min(int(np.ceil(x.max())), w - 1)
        y0, y1 = max(int(np.floor(y.min())), 0), min(int(np.ceil(y.max())), h - 1)
        if x0 > x1 or y0 > y1:
            continue
        area = (x[1] - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (y[1] - y[0])
        if abs(area) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        w0 = ((x[1] - gx) * (y[2] - gy) - (x[2] - gx) * (y[1] - gy)) / area
        w1 = ((x[2] - gx) * (y[0] - gy) - (x[0] - gx) * (y[2] - gy)) / area
        w2 = 1.0 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not inside.any():
            continue
        # perspective-correct depth
        zz = 1.0 / (w0 / z[0] + w1 / z[1] + w2 / z[2])
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        win = inside & (zz < sub)
        sub[win] = zz[win]
        image[y0:y1 + 1, x0:x1 + 1][win] = colours[t]

    buf = io.BytesIO()
    Image.fromarray(image.astype(np.uint8)).save(buf, format="PNG")
    return buf.getvalue()
