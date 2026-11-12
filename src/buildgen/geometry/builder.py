"""3D geometry builder — extrudes floor plans into 3D meshes."""

from __future__ import annotations

import numpy as np
import trimesh
from shapely.geometry import Polygon

from ..layout.models import FloorPlan, OpeningType, RoomPolygon, WallSegment, WallType
from ..style.models import StyleParams
from .models import Building3D
from .walls import build_wall_with_openings, opening_span
from .roofs import build_roof_mesh
from .stairs import build_stair_mesh


class GeometryBuilder:
    """Builds 3D geometry from floor plans and style parameters.

    Usage:
        builder = GeometryBuilder()
        building = builder.build(floor_plans, style)
    """

    def build(
        self,
        floor_plans: list[FloorPlan],
        style: StyleParams,
    ) -> Building3D:
        """Build complete 3D building from floor plans."""
        scene = trimesh.Scene()

        total_floor_area = 0.0

        for plan in floor_plans:
            floor_y = plan.floor_index * style.floor_height
            total_floor_area += plan.total_area

            # Floor slab — with stairwell openings cut out
            if plan.footprint:
                stairwell_rooms = [
                    r for r in plan.rooms if r.room_type == "stairwell"
                ]
                slab = self._build_slab_with_openings(
                    plan.footprint, floor_y, style.slab_thickness,
                    stairwell_rooms,
                )
                scene.add_geometry(
                    slab, node_name=f"floor_{plan.floor_index}_slab"
                )

            # Walls, with every door and window on this floor that lies on them left open
            openings = [o for room in plan.rooms for o in room.openings]
            for wi, wall in enumerate(plan.walls):
                spans = []
                for opening in openings:
                    span = opening_span(wall, opening, floor_y, style.floor_height)
                    if span is not None:
                        spans.append(span)
                wall_mesh = build_wall_with_openings(
                    wall, spans, floor_y, style.floor_height, style
                )
                if wall_mesh:
                    scene.add_geometry(
                        wall_mesh,
                        node_name=f"floor_{plan.floor_index}_wall_{wi}",
                    )

            # Stairs
            for room in plan.rooms:
                if room.room_type == "stairwell":
                    stair_mesh = build_stair_mesh(
                        room, floor_y, style.floor_height, style
                    )
                    if stair_mesh:
                        scene.add_geometry(
                            stair_mesh,
                            node_name=f"floor_{plan.floor_index}_stairs",
                        )

        # Ceiling / top slab
        if floor_plans:
            top_plan = floor_plans[-1]
            if top_plan.footprint:
                top_y = (top_plan.floor_index + 1) * style.floor_height
                ceiling = self._build_slab(
                    top_plan.footprint, top_y, style.slab_thickness
                )
                scene.add_geometry(ceiling, node_name="ceiling_slab")

            # Roof
            if top_plan.footprint:
                roof_y = (top_plan.floor_index + 1) * style.floor_height
                roof = build_roof_mesh(
                    top_plan.footprint, roof_y, style
                )
                if roof:
                    scene.add_geometry(roof, node_name="roof")

        fp_area = 0.0
        if floor_plans and floor_plans[0].footprint:
            fp_area = floor_plans[0].footprint.area

        return Building3D(
            mesh=scene,
            num_floors=len(floor_plans),
            footprint_area=fp_area,
            total_floor_area=total_floor_area,
        )

    def _build_slab_with_openings(
        self,
        footprint: Polygon,
        y: float,
        thickness: float,
        stairwell_rooms: list[RoomPolygon],
    ) -> trimesh.Trimesh:
        """Build a floor slab with holes cut for stairwells."""
        from shapely.geometry import box as shapely_box

        slab_poly = footprint
        # Cut out stairwell openings (stairs pass through the slab)
        for room in stairwell_rooms:
            b = room.bounds
            # Inset slightly so the stair opening isn't right at the edge
            margin = 0.05
            hole = shapely_box(
                b[0] + margin, b[1] + margin,
                b[2] - margin, b[3] - margin,
            )
            try:
                result = slab_poly.difference(hole)
                if not result.is_empty and result.area > 1.0:
                    slab_poly = result
            except Exception:
                pass

        return self._build_slab(slab_poly, y, thickness)

    def _build_slab(
        self, footprint: Polygon, y: float, thickness: float
    ) -> trimesh.Trimesh:
        """Build a floor slab from a polygon footprint.

        Handles simple polygons and polygons with holes (stairwell cutouts).
        Uses trimesh extrusion for robustness.
        """
        try:
            # Use trimesh's path extrusion for complex shapes
            from shapely.geometry import MultiPolygon

            # Handle MultiPolygon from boolean operations
            if isinstance(footprint, MultiPolygon):
                polys = list(footprint.geoms)
            else:
                polys = [footprint]

            meshes = []
            for poly in polys:
                # Convert shapely polygon to 2D path for extrusion
                coords_2d = np.array(poly.exterior.coords[:-1])
                # Swap y/z: shapely y -> trimesh z
                vertices_3d = np.column_stack([
                    coords_2d[:, 0],
                    np.full(len(coords_2d), 0),
                    coords_2d[:, 1],
                ])

                # Simple fan triangulation for exterior
                n = len(coords_2d)
                bottom_verts = [(c[0], y, c[1]) for c in coords_2d]
                top_verts = [(c[0], y + thickness, c[1]) for c in coords_2d]
                verts = bottom_verts + top_verts

                faces = []
                for i in range(1, n - 1):
                    faces.append([0, i, i + 1])
                    faces.append([n, n + i + 1, n + i])
                for i in range(n):
                    j = (i + 1) % n
                    faces.append([i, j, n + j])
                    faces.append([i, n + j, n + i])

                # Add hole side faces if polygon has interiors
                offset = 2 * n
                for interior in poly.interiors:
                    hole_coords = np.array(interior.coords[:-1])
                    nh = len(hole_coords)
                    hole_bottom = [(c[0], y, c[1]) for c in hole_coords]
                    hole_top = [(c[0], y + thickness, c[1]) for c in hole_coords]
                    verts.extend(hole_bottom)
                    verts.extend(hole_top)

                    # Side faces around the hole (inward-facing)
                    for i in range(nh):
                        j = (i + 1) % nh
                        vi0 = offset + i
                        vi1 = offset + j
                        vi2 = offset + nh + j
                        vi3 = offset + nh + i
                        faces.append([vi0, vi2, vi1])
                        faces.append([vi0, vi3, vi2])

                    offset += 2 * nh

                m = trimesh.Trimesh(
                    vertices=np.array(verts, dtype=np.float64),
                    faces=np.array(faces, dtype=np.int64),
                )
                m.fix_normals()
                m.visual.face_colors = [200, 200, 200, 255]
                meshes.append(m)

            if len(meshes) == 1:
                return meshes[0]
            return trimesh.util.concatenate(meshes)

        except Exception:
            # Fallback: simple rectangular slab from bounds
            b = footprint.bounds
            coords = [
                (b[0], b[1]), (b[2], b[1]),
                (b[2], b[3]), (b[0], b[3]),
            ]
            n = 4
            bottom = [(c[0], y, c[1]) for c in coords]
            top = [(c[0], y + thickness, c[1]) for c in coords]
            verts = bottom + top
            faces = [
                [0, 1, 2], [0, 2, 3],
                [4, 6, 5], [4, 7, 6],
                [0, 1, 5], [0, 5, 4],
                [1, 2, 6], [1, 6, 5],
                [2, 3, 7], [2, 7, 6],
                [3, 0, 4], [3, 4, 7],
            ]
            m = trimesh.Trimesh(
                vertices=np.array(verts, dtype=np.float64),
                faces=np.array(faces, dtype=np.int64),
            )
            m.fix_normals()
            m.visual.face_colors = [200, 200, 200, 255]
            return m
