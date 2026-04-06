"""Granular building element generator.

Generates every individual brick, joist, rafter, slate, window pane,
door panel, nail, and hinge in a building. Each element has exact
position, dimensions, material, and structural loads.

A typical Georgian townhouse contains approximately:
    - 40,000-60,000 bricks
    - 100-200 floor joists
    - 40-60 roof rafters
    - 800-1200 roof slates
    - 20-30 windows with ~600 glass panes
    - 15-20 doors
    - 2,000+ floorboards
    - 50,000+ mortar joints
"""

from __future__ import annotations

import math

from .elements import Element, ElementType, ElementCollection
from .model import StructuralModel
from .loads import calculate_loads
from .wall_builder import build_solid_brick_wall, build_cavity_wall, build_stone_wall
from .window_builder import build_sash_window, build_panel_door


# ── Standard dimensions (metres) ──────────────────────────────────

# UK standard brick: 215 x 102.5 x 65 mm
BRICK_L = 0.215
BRICK_W = 0.1025
BRICK_H = 0.065
MORTAR_T = 0.010   # 10mm mortar joint

# Brick + mortar = one course height
COURSE_H = BRICK_H + MORTAR_T  # 75mm

# Floor joist standard sizes
JOIST_WIDTH = 0.047   # 47mm
JOIST_SPACING = 0.400  # 400mm centres

# Rafter standard
RAFTER_WIDTH = 0.047
RAFTER_DEPTH = 0.150  # Depends on span
RAFTER_SPACING = 0.400

# Floorboard
BOARD_WIDTH = 0.150    # 150mm tongue-and-groove
BOARD_THICKNESS = 0.022  # 22mm

# Slate
SLATE_W = 0.300
SLATE_H = 0.600
SLATE_T = 0.005

# Window components
SASH_FRAME_W = 0.070   # Frame section width
GLAZING_BAR_W = 0.020  # Glazing bar width
GLASS_T = 0.003        # 3mm float glass


def generate_all_elements(
    model: StructuralModel,
    floor_height: float = 3.0,
    num_floors: int = 2,
) -> ElementCollection:
    """Generate every individual element in a building.

    Args:
        model: The structural model (footprint, walls, etc.)
        floor_height: Height of each floor in metres
        num_floors: Number of floors

    Returns:
        ElementCollection with every brick, joist, etc.
    """
    collection = ElementCollection()
    loads = calculate_loads(model)

    w = model.footprint_width
    d = model.footprint_depth

    # ── FOUNDATION ──
    _generate_foundation(collection, model, loads)

    # ── WALLS (every brick and mortar joint) ──
    # Use appropriate wall construction for the material
    wall_data = [
        ("wall_south", 0, 0, w, 0),
        ("wall_east", w, 0, w, d),
        ("wall_north", w, d, 0, d),
        ("wall_west", 0, d, 0, 0),
    ]

    for floor in range(num_floors):
        floor_y = floor * floor_height
        load = loads.foundation_load_per_m / num_floors

        for name, x1, z1, x2, z2 in wall_data:
            if model.wall_material in ("brick", "stucco_over_brick"):
                # Georgian: solid Flemish bond, 1.5 brick thick
                elems = build_solid_brick_wall(
                    x1, z1, x2, z2, floor_y, floor_height,
                    bond="flemish", thickness_bricks=2,
                    brick_material="facing_brick",
                    load_per_m=load,
                    floor_idx=floor, parent=name,
                )
            elif model.wall_material in ("stone",):
                elems = build_stone_wall(
                    x1, z1, x2, z2, floor_y, floor_height,
                    stone_type="ashlar", stone_material="limestone",
                    wall_thickness=0.600,
                    load_per_m=load,
                    floor_idx=floor, parent=name,
                )
            elif model.wall_material in ("timber_frame",):
                # Timber frame — use stretcher bond for infill panels
                elems = build_solid_brick_wall(
                    x1, z1, x2, z2, floor_y, floor_height,
                    bond="stretcher", thickness_bricks=1,
                    brick_material="common_brick",
                    load_per_m=load,
                    floor_idx=floor, parent=name,
                )
            else:
                elems = build_solid_brick_wall(
                    x1, z1, x2, z2, floor_y, floor_height,
                    bond="stretcher", thickness_bricks=1,
                    brick_material="common_brick",
                    load_per_m=load,
                    floor_idx=floor, parent=name,
                )
            collection.elements.extend(elems)

    # ── FLOORS (joists + floorboards) ──
    for floor in range(num_floors):
        floor_y = floor * floor_height
        _generate_floor_structure(
            collection, w, d, floor_y, model.floors[0].max_span,
            floor, loads.floor_total_loads[0],
        )

    # ── ROOF (rafters + slates) ──
    roof_y = num_floors * floor_height
    _generate_roof_structure(
        collection, w, d, roof_y, model.roof.pitch_degrees,
        model.roof.roof_type,
    )

    # ── WINDOWS (detailed sash construction) ──
    bay_spacing = 2.4
    sill_height = 0.85
    win_h = 1.65
    for floor in range(num_floors):
        floor_y = floor * floor_height
        # Windows on front and back walls
        for wall_z, wall_name in [(0, "south"), (d, "north")]:
            num_win = max(1, int(w / bay_spacing))
            for wi in range(num_win):
                wx = (wi + 0.5) * w / num_win
                wy = floor_y + sill_height + win_h / 2
                elems = build_sash_window(
                    wx, wy, wall_z,
                    panes_wide=3, panes_high_per_sash=3,
                    parent=f"win_{wall_name}_{floor}_{wi}",
                    floor_idx=floor, period="georgian",
                )
                collection.elements.extend(elems)

        # Windows on side walls (fewer)
        for wall_x, wall_name in [(0, "west"), (w, "east")]:
            num_win = max(1, int(d / (bay_spacing * 1.5)))
            for wi in range(num_win):
                wz = (wi + 0.5) * d / num_win
                wy = floor_y + sill_height + win_h / 2
                elems = build_sash_window(
                    wall_x, wy, wz,
                    panes_wide=2, panes_high_per_sash=3,
                    rotation=90,
                    parent=f"win_{wall_name}_{floor}_{wi}",
                    floor_idx=floor, period="georgian",
                )
                collection.elements.extend(elems)

    # ── DOORS (detailed panel construction) ──
    # Front door with fanlight
    door_elems = build_panel_door(
        w / 2, 1.05, 0,
        door_width=1.05, door_height=2.1,
        num_panels=6, has_fanlight=True,
        parent="front_door",
    )
    collection.elements.extend(door_elems)

    # Rear door (simpler, no fanlight)
    rear_door = build_panel_door(
        w / 2, 1.05, d,
        door_width=0.9, door_height=2.1,
        num_panels=4, has_fanlight=False,
        parent="rear_door",
    )
    collection.elements.extend(rear_door)

    return collection


def _generate_foundation(
    coll: ElementCollection,
    model: StructuralModel,
    loads,
) -> None:
    """Generate strip foundation elements."""
    w = model.footprint_width
    d = model.footprint_depth
    found_w = max(0.45, loads.required_foundation_width)
    found_d = model.foundation_depth

    # Foundation as concrete strips under each wall
    # For walls along X: length=X, width=Z
    # For walls along Z: length=found_w (narrow), width=wall_length (long)
    for wall_name, (x1, z1, x2, z2) in [
        ("found_south", (0, 0, w, 0)),
        ("found_east", (w, 0, w, d)),
        ("found_north", (0, d, w, d)),
        ("found_west", (0, 0, 0, d)),
    ]:
        wall_length = ((x2 - x1) ** 2 + (z2 - z1) ** 2) ** 0.5
        cx = (x1 + x2) / 2
        cz = (z1 + z2) / 2
        runs_along_z = abs(z2 - z1) > abs(x2 - x1)

        if runs_along_z:
            el_length = found_w       # Narrow in X
            el_width = wall_length    # Long in Z
        else:
            el_length = wall_length   # Long in X
            el_width = found_w        # Narrow in Z

        coll.elements.append(Element(
            element_type=ElementType.FOUNDATION,
            material_name="engineering_brick",
            x=cx, y=-found_d / 2, z=cz,
            length=el_length, width=el_width, height=found_d,
            parent=wall_name,
            compression=loads.foundation_load_per_m * wall_length,
        ))


def _generate_wall_bricks(
    coll: ElementCollection,
    x1: float, z1: float, x2: float, z2: float,
    floor_y: float, wall_height: float,
    material: str, floor_idx: int, parent: str,
    load_per_m: float,
) -> None:
    """Lay individual bricks in a wall with mortar joints.

    Uses Flemish bond: alternating headers and stretchers per course,
    offset by half a brick each course.
    """
    wall_dx = x2 - x1
    wall_dz = z2 - z1
    wall_length = (wall_dx ** 2 + wall_dz ** 2) ** 0.5

    if wall_length < 0.1:
        return

    # Direction vectors
    dir_x = wall_dx / wall_length
    dir_z = wall_dz / wall_length

    # Rotation angle for brick orientation
    rotation = math.degrees(math.atan2(dir_z, dir_x))

    # Number of courses in wall height
    num_courses = int(wall_height / COURSE_H)

    # Wall thickness — for exterior, 1.5 bricks (stretcher + header)
    # Simplified: we model as single-skin stretcher bond
    wall_thickness = BRICK_W

    # Brick material based on wall material
    if material in ("brick", "stucco_over_brick"):
        brick_mat = "facing_brick"
    else:
        brick_mat = "common_brick"

    # Load diminishes from bottom to top
    bricks_in_wall = 0

    for course in range(num_courses):
        y = floor_y + course * COURSE_H + BRICK_H / 2

        # Offset alternating courses by half a brick (Flemish bond)
        offset = (BRICK_L / 2) if course % 2 == 1 else 0

        # Number of bricks along the wall
        num_bricks = int((wall_length - offset) / (BRICK_L + MORTAR_T))

        # Load on this course (kN per brick)
        # Courses above carry progressively less load
        courses_above = num_courses - course - 1
        load_factor = courses_above / num_courses if num_courses > 0 else 0
        load_on_brick = load_per_m * (BRICK_L + MORTAR_T) * load_factor

        for b in range(num_bricks):
            # Position along wall
            t = (offset + b * (BRICK_L + MORTAR_T) + BRICK_L / 2) / wall_length
            if t > 1.0:
                break

            bx = x1 + t * wall_dx
            bz = z1 + t * wall_dz

            coll.elements.append(Element(
                element_type=ElementType.BRICK,
                material_name=brick_mat,
                x=bx, y=y, z=bz,
                length=BRICK_L, width=BRICK_W, height=BRICK_H,
                rotation=rotation,
                parent=parent,
                floor_index=floor_idx,
                compression=load_on_brick,
            ))

            # Mortar joint (bed joint — horizontal)
            if course > 0:
                coll.elements.append(Element(
                    element_type=ElementType.MORTAR_JOINT,
                    material_name="mortar_lime",
                    x=bx, y=y - BRICK_H / 2 - MORTAR_T / 2, z=bz,
                    length=BRICK_L, width=BRICK_W, height=MORTAR_T,
                    rotation=rotation,
                    parent=parent,
                    floor_index=floor_idx,
                ))

            bricks_in_wall += 1


def _generate_floor_structure(
    coll: ElementCollection,
    width: float, depth: float,
    floor_y: float, max_span: float,
    floor_idx: int, floor_load: float,
) -> None:
    """Generate individual floor joists and floorboards."""
    # Joists span the shorter dimension (width)
    joist_span = min(width, max_span)
    joist_depth = _size_joist_depth(joist_span)

    num_joists = int(depth / JOIST_SPACING)
    load_per_joist = floor_load * JOIST_SPACING * joist_span  # kN total

    # UDL bending moment: M = wL²/8
    w_udl = floor_load * JOIST_SPACING  # kN/m
    max_moment = w_udl * joist_span ** 2 / 8  # kN·m
    max_shear = w_udl * joist_span / 2  # kN

    for j in range(num_joists):
        z = j * JOIST_SPACING + JOIST_SPACING / 2
        if z > depth:
            break

        coll.elements.append(Element(
            element_type=ElementType.JOIST,
            material_name="softwood_c24",
            x=width / 2, y=floor_y + joist_depth / 2, z=z,
            length=joist_span, width=JOIST_WIDTH, height=joist_depth,
            rotation=0,
            parent=f"floor_{floor_idx}",
            floor_index=floor_idx,
            compression=0,
            bending_moment=max_moment,
            shear=max_shear,
        ))

    # Floorboards on top of joists
    num_boards = int(width / BOARD_WIDTH)
    for b in range(num_boards):
        bx = b * BOARD_WIDTH + BOARD_WIDTH / 2
        coll.elements.append(Element(
            element_type=ElementType.FLOORBOARD,
            material_name="softwood_c16",
            x=bx, y=floor_y + joist_depth + BOARD_THICKNESS / 2, z=depth / 2,
            length=depth, width=BOARD_WIDTH, height=BOARD_THICKNESS,
            rotation=90,
            parent=f"floor_{floor_idx}",
            floor_index=floor_idx,
        ))

    # Wall plate (timber beam on top of wall, joists sit on this)
    for name, (px, pz, rot) in [
        ("plate_south", (width / 2, 0, 0)),
        ("plate_north", (width / 2, depth, 0)),
    ]:
        coll.elements.append(Element(
            element_type=ElementType.WALL_PLATE,
            material_name="softwood_c24",
            x=px, y=floor_y, z=pz,
            length=width, width=0.100, height=0.075,
            rotation=rot,
            parent=f"floor_{floor_idx}",
            floor_index=floor_idx,
        ))


def _generate_roof_structure(
    coll: ElementCollection,
    width: float, depth: float,
    roof_y: float, pitch_deg: float,
    roof_type: str,
) -> None:
    """Generate individual rafters, purlins, ridge board, and slates."""
    pitch_rad = math.radians(pitch_deg)
    half_span = width / 2
    rafter_length = half_span / math.cos(pitch_rad) if math.cos(pitch_rad) > 0.1 else half_span
    ridge_height = half_span * math.tan(pitch_rad)

    rafter_depth = max(0.100, rafter_length / 30 + 0.05)
    num_rafters = int(depth / RAFTER_SPACING) * 2  # Both sides

    # Ridge board
    coll.elements.append(Element(
        element_type=ElementType.RIDGE_BOARD,
        material_name="softwood_c24",
        x=width / 2, y=roof_y + ridge_height, z=depth / 2,
        length=depth, width=0.038, height=0.200,
        parent="roof",
    ))

    # Rafters — left and right slopes
    for i in range(int(depth / RAFTER_SPACING)):
        z = i * RAFTER_SPACING + RAFTER_SPACING / 2
        if z > depth:
            break

        for side, x_start, angle_sign in [("left", 0, 1), ("right", width, -1)]:
            cx = x_start + angle_sign * half_span / 2
            cy = roof_y + ridge_height / 2

            coll.elements.append(Element(
                element_type=ElementType.RAFTER,
                material_name="softwood_c24",
                x=cx, y=cy, z=z,
                length=rafter_length, width=RAFTER_WIDTH, height=rafter_depth,
                rotation=angle_sign * pitch_deg,
                parent=f"roof_{side}",
            ))

    # Tie beams (prevent roof spreading)
    for i in range(int(depth / (RAFTER_SPACING * 3))):
        z = i * RAFTER_SPACING * 3 + RAFTER_SPACING
        coll.elements.append(Element(
            element_type=ElementType.TIE_BEAM,
            material_name="softwood_c24",
            x=width / 2, y=roof_y, z=z,
            length=width, width=0.100, height=0.200,
            parent="roof",
            tension=0.5,  # Tie resists roof thrust
        ))

    # Roof slates/tiles
    slope_length = rafter_length
    num_slate_rows = int(slope_length / (SLATE_H * 0.5))  # Double lap
    num_slates_per_row = int(depth / SLATE_W)

    for side in ["left", "right"]:
        for row in range(num_slate_rows):
            for col in range(num_slates_per_row):
                # Position on slope
                t_up = row / num_slate_rows
                z = col * SLATE_W + SLATE_W / 2

                if side == "left":
                    sx = t_up * half_span
                else:
                    sx = width - t_up * half_span

                sy = roof_y + t_up * ridge_height

                coll.elements.append(Element(
                    element_type=ElementType.SLATE,
                    material_name="roofing_slate",
                    x=sx, y=sy, z=z,
                    length=SLATE_W, width=SLATE_H, height=SLATE_T,
                    parent=f"roof_{side}",
                ))


def _generate_windows(
    coll: ElementCollection,
    width: float, depth: float,
    floor_y: float, floor_height: float,
    floor_idx: int,
) -> None:
    """Generate window components: frame, sashes, glazing bars, glass.

    Georgian sash window: 6-over-6 (12 panes total).
    """
    window_w = 1.05   # Window opening width
    window_h = 1.65   # Window opening height
    sill_h = 0.85     # Sill height above floor
    bay_spacing = 2.4  # Distance between window centres

    # Windows on front (z=0) and back (z=depth) walls
    for wall_z, wall_name in [(0, "south"), (depth, "north")]:
        num_windows = max(1, int(width / bay_spacing))
        for wi in range(num_windows):
            wx = (wi + 0.5) * width / num_windows
            wy = floor_y + sill_h + window_h / 2
            parent = f"window_{wall_name}_{floor_idx}_{wi}"

            # Lintel over the window (load-bearing beam)
            lintel_depth = 0.150
            lintel_w = window_w + 0.200  # Bearing 100mm each side
            coll.elements.append(Element(
                element_type=ElementType.LINTEL,
                material_name="oak",
                x=wx, y=floor_y + sill_h + window_h + lintel_depth / 2, z=wall_z,
                length=lintel_w, width=BRICK_W, height=lintel_depth,
                parent=parent, floor_index=floor_idx,
            ))

            # Window frame (4 pieces: head, sill, 2 jambs)
            # Head
            coll.elements.append(Element(
                element_type=ElementType.WINDOW_FRAME,
                material_name="softwood_c16",
                x=wx, y=wy + window_h / 2 - SASH_FRAME_W / 2, z=wall_z,
                length=window_w, width=0.050, height=SASH_FRAME_W,
                parent=parent, floor_index=floor_idx,
            ))
            # Sill
            coll.elements.append(Element(
                element_type=ElementType.WINDOW_FRAME,
                material_name="softwood_c16",
                x=wx, y=wy - window_h / 2 + SASH_FRAME_W / 2, z=wall_z,
                length=window_w + 0.050, width=0.070, height=SASH_FRAME_W,
                parent=parent, floor_index=floor_idx,
            ))

            # Sashes (upper and lower, each with glazing bars and glass)
            sash_h = (window_h - SASH_FRAME_W * 2) / 2
            for sash_name, sash_y_off in [("upper", sash_h / 2), ("lower", -sash_h / 2)]:
                sash_cy = wy + sash_y_off

                # Sash frame
                coll.elements.append(Element(
                    element_type=ElementType.WINDOW_SASH,
                    material_name="softwood_c16",
                    x=wx, y=sash_cy, z=wall_z,
                    length=window_w - SASH_FRAME_W * 2,
                    width=0.035, height=sash_h,
                    parent=parent, floor_index=floor_idx,
                ))

                # 6 panes per sash (3 wide x 2 tall) = 6-over-6
                pane_w = (window_w - SASH_FRAME_W * 2 - GLAZING_BAR_W * 2) / 3
                pane_h = (sash_h - GLAZING_BAR_W) / 2

                for px in range(3):
                    for py in range(2):
                        pane_cx = wx - window_w / 2 + SASH_FRAME_W + pane_w * (px + 0.5) + GLAZING_BAR_W * px
                        pane_cy = sash_cy - sash_h / 2 + pane_h * (py + 0.5) + GLAZING_BAR_W * py

                        # Glass pane
                        coll.elements.append(Element(
                            element_type=ElementType.GLASS_PANE,
                            material_name="float_glass",
                            x=pane_cx, y=pane_cy, z=wall_z,
                            length=pane_w, width=GLASS_T, height=pane_h,
                            parent=parent, floor_index=floor_idx,
                        ))

                # Glazing bars (2 vertical + 1 horizontal per sash)
                for gb in range(2):
                    gb_x = wx - window_w / 2 + SASH_FRAME_W + pane_w * (gb + 1) + GLAZING_BAR_W * gb
                    coll.elements.append(Element(
                        element_type=ElementType.GLAZING_BAR,
                        material_name="softwood_c16",
                        x=gb_x, y=sash_cy, z=wall_z,
                        length=GLAZING_BAR_W, width=0.015, height=sash_h,
                        parent=parent, floor_index=floor_idx,
                    ))


def _generate_doors(
    coll: ElementCollection,
    width: float, depth: float,
    floor_y: float, floor_height: float,
) -> None:
    """Generate door components: frame, leaf, hinges."""
    door_w = 1.1
    door_h = 2.4
    frame_w = 0.100

    # Front door at centre of south wall
    dx = width / 2
    dy = floor_y + door_h / 2
    parent = "front_door"

    # Lintel
    coll.elements.append(Element(
        element_type=ElementType.LINTEL,
        material_name="oak",
        x=dx, y=floor_y + door_h + 0.075, z=0,
        length=door_w + 0.200, width=BRICK_W, height=0.150,
        parent=parent,
    ))

    # Door frame (head + 2 jambs)
    coll.elements.append(Element(
        element_type=ElementType.DOOR_FRAME,
        material_name="oak",
        x=dx, y=floor_y + door_h - frame_w / 2, z=0,
        length=door_w + frame_w * 2, width=0.070, height=frame_w,
        parent=parent,
    ))
    for side_x in [dx - door_w / 2 - frame_w / 2, dx + door_w / 2 + frame_w / 2]:
        coll.elements.append(Element(
            element_type=ElementType.DOOR_FRAME,
            material_name="oak",
            x=side_x, y=dy, z=0,
            length=frame_w, width=0.070, height=door_h,
            parent=parent,
        ))

    # Door leaf (6-panel Georgian door)
    coll.elements.append(Element(
        element_type=ElementType.DOOR_LEAF,
        material_name="oak",
        x=dx, y=dy, z=0,
        length=door_w, width=0.044, height=door_h,
        parent=parent,
    ))

    # Hinges (3 per door)
    for hy in [floor_y + 0.200, floor_y + door_h / 2, floor_y + door_h - 0.200]:
        coll.elements.append(Element(
            element_type=ElementType.HINGE,
            material_name="wrought_iron",
            x=dx - door_w / 2, y=hy, z=0,
            length=0.100, width=0.003, height=0.075,
            parent=parent,
        ))


def _size_joist_depth(span: float) -> float:
    """Size floor joist depth for a given span."""
    depth_mm = span * 1000 / 24 + 50
    standard = [0.150, 0.175, 0.200, 0.225, 0.250, 0.300]
    for s in standard:
        if s >= depth_mm / 1000:
            return s
    return 0.300
