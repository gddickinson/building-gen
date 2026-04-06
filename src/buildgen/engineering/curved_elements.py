"""Curved architectural elements.

Creates 3D meshes for curved building features:
- Curved staircase (oval/circular)
- Apsidal wall ends (semicircular room terminations)
- Portico columns (cylindrical)
- Balcony railings (curved iron)
- Parapet walls
- String courses
- Rusticated quoins
"""

from __future__ import annotations

import math
import numpy as np
import trimesh

from .elements import Element, ElementType


def create_column(
    cx: float, cy_base: float, cz: float,
    diameter: float, height: float,
    color: list[int] | None = None,
    segments: int = 16,
) -> trimesh.Trimesh:
    """Create a cylindrical column."""
    if color is None:
        color = [220, 215, 200, 255]  # Stone

    cylinder = trimesh.creation.cylinder(
        radius=diameter / 2, height=height, sections=segments,
    )
    cylinder.apply_translation([cx, cy_base + height / 2, cz])
    cylinder.visual.face_colors = color
    return cylinder


def create_portico(
    cx: float, base_y: float, cz: float,
    width: float = 3.0,
    height: float = 4.0,
    depth: float = 1.5,
    num_columns: int = 2,
    column_diameter: float = 0.35,
    color: list[int] | None = None,
) -> list[trimesh.Trimesh]:
    """Create a portico with columns and entablature."""
    if color is None:
        color = [220, 215, 200, 255]

    meshes = []

    # Columns
    col_spacing = width / (num_columns + 1)
    for ci in range(num_columns):
        col_x = cx - width / 2 + (ci + 1) * col_spacing
        col = create_column(
            col_x, base_y, cz - depth / 2,
            column_diameter, height - 0.3,
            color,
        )
        meshes.append(col)

    # Entablature (beam across top of columns)
    entab = trimesh.creation.box(extents=[width + 0.2, 0.25, depth])
    entab.apply_translation([cx, base_y + height - 0.15, cz - depth / 2])
    entab.visual.face_colors = color
    meshes.append(entab)

    # Pediment (triangular)
    ped_h = width * 0.15
    verts = np.array([
        [cx - width / 2 - 0.1, base_y + height, cz - depth / 2],
        [cx + width / 2 + 0.1, base_y + height, cz - depth / 2],
        [cx, base_y + height + ped_h, cz - depth / 2],
        [cx - width / 2 - 0.1, base_y + height, cz - depth / 2 + 0.15],
        [cx + width / 2 + 0.1, base_y + height, cz - depth / 2 + 0.15],
        [cx, base_y + height + ped_h, cz - depth / 2 + 0.15],
    ], dtype=np.float64)
    faces = np.array([
        [0, 1, 2], [3, 5, 4],
        [0, 3, 4], [0, 4, 1],
        [1, 4, 5], [1, 5, 2],
        [0, 2, 5], [0, 5, 3],
    ], dtype=np.int64)
    ped = trimesh.Trimesh(vertices=verts, faces=faces)
    ped.fix_normals()
    ped.visual.face_colors = color
    meshes.append(ped)

    # Step/platform
    step = trimesh.creation.box(extents=[width + 0.4, 0.15, depth + 0.3])
    step.apply_translation([cx, base_y - 0.075, cz - depth / 2])
    step.visual.face_colors = color
    meshes.append(step)

    return meshes


def create_parapet(
    width: float, depth: float,
    base_y: float,
    parapet_height: float = 0.9,
    wall_thickness: float = 0.35,
    color: list[int] | None = None,
) -> list[trimesh.Trimesh]:
    """Create parapet walls around the roof perimeter."""
    if color is None:
        color = [190, 120, 80, 255]

    meshes = []

    # Four parapet walls (brick, matching exterior)
    for name, (x, z, lx, lz) in {
        "front": (width / 2, 0, width, wall_thickness),
        "rear": (width / 2, depth, width, wall_thickness),
        "left": (0, depth / 2, wall_thickness, depth),
        "right": (width, depth / 2, wall_thickness, depth),
    }.items():
        wall = trimesh.creation.box(extents=[lx, parapet_height, lz])
        wall.apply_translation([x, base_y + parapet_height / 2, z])
        wall.visual.face_colors = color
        meshes.append(wall)

    # Coping stone on top
    for name, (x, z, lx, lz) in {
        "front": (width / 2, 0, width + 0.1, wall_thickness + 0.1),
        "rear": (width / 2, depth, width + 0.1, wall_thickness + 0.1),
        "left": (0, depth / 2, wall_thickness + 0.1, depth + 0.1),
        "right": (width, depth / 2, wall_thickness + 0.1, depth + 0.1),
    }.items():
        coping = trimesh.creation.box(extents=[lx, 0.08, lz])
        coping.apply_translation([x, base_y + parapet_height + 0.04, z])
        coping.visual.face_colors = [210, 200, 180, 255]
        meshes.append(coping)

    return meshes


def create_balcony(
    cx: float, base_y: float, cz: float,
    width: float = 12.0,
    depth: float = 0.8,
    railing_height: float = 1.0,
    color: list[int] | None = None,
) -> list[trimesh.Trimesh]:
    """Create an iron balcony with railings."""
    if color is None:
        color = [40, 40, 45, 255]  # Dark iron

    meshes = []

    # Stone balcony slab
    slab = trimesh.creation.box(extents=[width, 0.1, depth])
    slab.apply_translation([cx, base_y, cz - depth / 2])
    slab.visual.face_colors = [210, 200, 180, 255]
    meshes.append(slab)

    # Iron railing - top rail
    rail = trimesh.creation.box(extents=[width, 0.04, 0.04])
    rail.apply_translation([cx, base_y + railing_height, cz - depth])
    rail.visual.face_colors = color
    meshes.append(rail)

    # Bottom rail
    bot_rail = trimesh.creation.box(extents=[width, 0.03, 0.03])
    bot_rail.apply_translation([cx, base_y + 0.1, cz - depth])
    bot_rail.visual.face_colors = color
    meshes.append(bot_rail)

    # Balusters
    num_balusters = int(width / 0.12)
    for bi in range(num_balusters):
        bx = cx - width / 2 + (bi + 0.5) * width / num_balusters
        bal = trimesh.creation.box(extents=[0.015, railing_height - 0.1, 0.015])
        bal.apply_translation([bx, base_y + railing_height / 2 + 0.05, cz - depth])
        bal.visual.face_colors = color
        meshes.append(bal)

    return meshes


def create_string_course(
    width: float, depth: float,
    y: float,
    projection: float = 0.05,
    height: float = 0.08,
    color: list[int] | None = None,
) -> list[trimesh.Trimesh]:
    """Create a horizontal string course/band around the building."""
    if color is None:
        color = [210, 200, 180, 255]

    meshes = []
    for x, z, lx, lz in [
        (width / 2, -projection, width + projection * 2, projection * 2),
        (width / 2, depth + projection, width + projection * 2, projection * 2),
        (-projection, depth / 2, projection * 2, depth + projection * 2),
        (width + projection, depth / 2, projection * 2, depth + projection * 2),
    ]:
        course = trimesh.creation.box(extents=[lx, height, lz])
        course.apply_translation([x, y, z])
        course.visual.face_colors = color
        meshes.append(course)

    return meshes


def create_curved_stair_mesh(
    cx: float, cy_base: float, cz: float,
    outer_radius: float = 2.5,
    inner_radius: float = 0.8,
    total_rise: float = 3.5,
    num_steps: int = 18,
    arc_degrees: float = 270,
    color: list[int] | None = None,
) -> list[trimesh.Trimesh]:
    """Create a curved/oval staircase as 3D mesh.

    Each step is a wedge-shaped segment of an annulus (ring).
    """
    if color is None:
        color = [200, 170, 120, 255]

    meshes = []
    arc_rad = math.radians(arc_degrees)
    angle_per_step = arc_rad / num_steps
    rise_per_step = total_rise / num_steps

    n_arc = 6  # Points per arc segment

    for step in range(num_steps):
        a_start = step * angle_per_step
        a_end = (step + 0.92) * angle_per_step
        step_y_top = cy_base + (step + 1) * rise_per_step
        step_y_bot = step_y_top - 0.04  # Tread thickness

        # Create wedge vertices
        verts = []
        # Bottom inner arc
        for k in range(n_arc + 1):
            t = k / n_arc
            a = a_start + t * (a_end - a_start)
            verts.append([cx + inner_radius * math.cos(a),
                         step_y_bot,
                         cz + inner_radius * math.sin(a)])
        # Bottom outer arc
        for k in range(n_arc + 1):
            t = k / n_arc
            a = a_start + t * (a_end - a_start)
            verts.append([cx + outer_radius * math.cos(a),
                         step_y_bot,
                         cz + outer_radius * math.sin(a)])
        # Top inner arc
        for k in range(n_arc + 1):
            t = k / n_arc
            a = a_start + t * (a_end - a_start)
            verts.append([cx + inner_radius * math.cos(a),
                         step_y_top,
                         cz + inner_radius * math.sin(a)])
        # Top outer arc
        for k in range(n_arc + 1):
            t = k / n_arc
            a = a_start + t * (a_end - a_start)
            verts.append([cx + outer_radius * math.cos(a),
                         step_y_top,
                         cz + outer_radius * math.sin(a)])

        n = n_arc + 1
        faces = []
        # Top face (between top inner and top outer)
        for k in range(n_arc):
            faces.append([2*n + k, 2*n + k+1, 3*n + k+1])
            faces.append([2*n + k, 3*n + k+1, 3*n + k])
        # Bottom face
        for k in range(n_arc):
            faces.append([k, n + k+1, k+1])
            faces.append([k, n + k, n + k+1])

        step_mesh = trimesh.Trimesh(
            vertices=np.array(verts, dtype=np.float64),
            faces=np.array(faces, dtype=np.int64),
        )
        step_mesh.fix_normals()
        step_mesh.visual.face_colors = color
        meshes.append(step_mesh)

    # Central newel (column)
    newel = create_column(cx, cy_base, cz, inner_radius * 0.5, total_rise,
                          [160, 120, 75, 255])
    meshes.append(newel)

    return meshes
