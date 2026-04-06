"""Export granular element model as grouped glTF for interactive viewing.

Instead of 72,000+ individual meshes (too slow), elements are grouped
by type into merged meshes. Each group is a named node in the glTF
scene, allowing the viewer to toggle visibility per element type.

Groups: bricks, mortar, timber_structure, roof_covering, glass,
        windows_doors, stairs, chimneys, plumbing, foundation, finishes
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from ..engineering.elements import ElementType, ElementCollection


# Map element types to viewer groups
_TYPE_GROUPS: dict[ElementType, str] = {
    ElementType.BRICK: "bricks",
    ElementType.STONE_BLOCK: "bricks",
    ElementType.MORTAR_JOINT: "mortar",
    ElementType.JOIST: "timber_structure",
    ElementType.BEAM: "timber_structure",
    ElementType.WALL_PLATE: "timber_structure",
    ElementType.TIE_BEAM: "timber_structure",
    ElementType.PURLIN: "timber_structure",
    ElementType.RAFTER: "roof_structure",
    ElementType.RIDGE_BOARD: "roof_structure",
    ElementType.SLATE: "roof_covering",
    ElementType.TILE: "roof_covering",
    ElementType.STUD: "battens_strutting",
    ElementType.FLOORBOARD: "floors",
    ElementType.CEILING_LATH: "ceilings",
    ElementType.PLASTER: "finishes",
    ElementType.WINDOW_FRAME: "windows",
    ElementType.WINDOW_SASH: "windows",
    ElementType.GLAZING_BAR: "windows",
    ElementType.GLASS_PANE: "glass",
    ElementType.DOOR_FRAME: "doors",
    ElementType.DOOR_LEAF: "doors",
    ElementType.LINTEL: "lintels",
    ElementType.COLUMN: "columns_pipes",
    ElementType.FOUNDATION: "foundation",
    ElementType.HINGE: "hardware",
    ElementType.NAIL: "hardware",
    ElementType.SOLE_PLATE: "timber_structure",
    ElementType.HEAD_PLATE: "timber_structure",
}

# Colors per group (RGBA 0-255)
_GROUP_COLORS: dict[str, list[int]] = {
    # Brick sub-groups
    "ext_walls": [190, 120, 80, 255],
    "int_walls": [210, 180, 150, 255],
    "ext_basement": [120, 80, 60, 255],
    "chimneys": [140, 90, 70, 255],
    # Original groups
    "bricks": [190, 120, 80, 255],
    "mortar": [220, 215, 200, 255],
    "timber_structure": [200, 170, 120, 255],
    "roof_structure": [180, 150, 100, 255],
    "roof_covering": [80, 85, 95, 255],
    "battens_strutting": [210, 180, 130, 255],
    "floors": [220, 195, 150, 255],
    "floor_0": [220, 195, 150, 255],
    "floor_1": [215, 190, 145, 255],
    "floor_2": [210, 185, 140, 255],
    "ceilings": [235, 230, 220, 255],
    "finishes": [240, 235, 225, 255],
    "windows": [160, 130, 90, 255],
    "glass": [180, 210, 240, 100],
    "doors": [140, 100, 65, 255],
    "lintels": [150, 115, 75, 255],
    "stairs": [185, 155, 110, 255],
    "services": [70, 90, 120, 255],
    "columns_pipes": [100, 100, 110, 255],
    "foundation": [100, 80, 65, 255],
    "hardware": [120, 120, 130, 255],
}


def export_grouped_glb(
    collection: ElementCollection,
    output_path: str | Path,
    skip_mortar: bool = True,
    building_width: float = 8.5,
    building_depth: float = 10.5,
    eaves_height: float = 9.6,
    ridge_height_above_eaves: float = 1.7,
) -> dict[str, int]:
    """Export elements as grouped glTF binary.

    Returns dict of group_name -> element_count.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    scene = trimesh.Scene()
    group_counts: dict[str, int] = {}

    # Collect meshes per group
    group_meshes: dict[str, list[trimesh.Trimesh]] = {}

    # Create proper angled rafter meshes instead of axis-aligned boxes
    from ..engineering.rafter_mesh import create_all_roof_meshes
    rafter_meshes = create_all_roof_meshes(
        building_width, building_depth,
        eaves_height, ridge_height_above_eaves,
        pitch_deg=35.0,
        roof_type="hip",
    )
    if rafter_meshes:
        color = [180, 150, 100, 255]
        for rm in rafter_meshes:
            rm.visual.face_colors = color
        group_meshes["roof_structure"] = rafter_meshes
        group_counts["roof_structure"] = len(rafter_meshes)

    for element in collection.elements:
        base_group = _TYPE_GROUPS.get(element.element_type, "other")

        if skip_mortar and base_group == "mortar":
            continue

        # Skip old axis-aligned rafter elements — replaced by angled meshes above
        if base_group == "roof_structure":
            continue

        # Skip old stepped rafter segments that ended up as STUD/battens
        # These are above the eaves height and create the dual-roof artifact
        if (element.element_type == ElementType.STUD
                and element.y > eaves_height - 0.5
                and "batten" in element.parent):
            continue

        if element.length <= 0 or element.width <= 0 or element.height <= 0:
            continue

        # Split bricks into exterior/interior/chimney/basement sub-groups
        # based on the element's parent name, for toggling visibility
        if base_group == "bricks":
            parent = element.parent.lower()
            if "basement" in parent or element.floor_index < 0:
                group = "ext_basement"
            elif "chimney" in parent or "flue" in parent or "pot" in parent:
                group = "chimneys"
            elif parent.startswith("wall_centre") or "part_" in parent:
                group = "int_walls"
            elif parent.startswith(("south", "north", "east", "west")):
                group = "ext_walls"
            else:
                group = "ext_walls"
        elif base_group in ("roof_structure", "roof_covering"):
            group = base_group  # Keep separate
        elif base_group == "floors":
            # Exclude guttering fascia/soffit boards from floor groups
            if "guttering" in element.parent or "fascia" in element.parent or "soffit" in element.parent:
                group = "finishes"
            elif element.floor_index >= 0:
                group = f"floor_{element.floor_index}"
            else:
                group = "ext_basement"
        elif base_group == "windows":
            group = "windows"
        elif base_group == "glass":
            group = "glass"
        elif base_group == "doors":
            group = "doors"
        elif base_group in ("timber_structure", "battens_strutting"):
            if "stair" in element.parent.lower():
                group = "stairs"
            else:
                group = base_group
        elif base_group == "columns_pipes":
            parent = element.parent.lower()
            if "plumbing" in parent or "heating" in parent:
                group = "services"
            else:
                group = base_group
        else:
            group = base_group

        mesh = trimesh.creation.box(
            extents=[element.length, element.height, element.width],
        )
        mesh.apply_translation([element.x, element.y, element.z])

        color = _GROUP_COLORS.get(group, _GROUP_COLORS.get(base_group, [180, 180, 180, 255]))
        mesh.visual.face_colors = color

        if group not in group_meshes:
            group_meshes[group] = []
        group_meshes[group].append(mesh)
        group_counts[group] = group_counts.get(group, 0) + 1

    # Merge each group into a single mesh and add to scene
    for group_name, meshes in group_meshes.items():
        if not meshes:
            continue

        try:
            if len(meshes) > 1:
                merged = trimesh.util.concatenate(meshes)
            else:
                merged = meshes[0]

            color = _GROUP_COLORS.get(group_name, [180, 180, 180, 255])
            merged.visual.face_colors = color

            # Set mesh name explicitly so it survives GLB export
            merged.metadata['name'] = group_name

            scene.add_geometry(merged, node_name=group_name, geom_name=group_name)
        except Exception as e:
            print(f"Warning: failed to merge group '{group_name}': {e}")

    scene.export(str(output_path))

    return group_counts
