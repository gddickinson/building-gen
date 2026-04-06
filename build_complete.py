"""Build a complete Georgian townhouse with every system.

Generates all elements and exports:
- Grouped glTF for interactive viewer
- Diagnostic views (elevations, sections, cutaways, systems)
- Element analysis summary
"""

from buildgen.engineering.design import design_structure
from buildgen.engineering.elements import ElementCollection
from buildgen.engineering.wall_builder import build_solid_brick_wall
from buildgen.engineering.floor_builder import build_detailed_floor
from buildgen.engineering.roof_builder import build_detailed_roof
from buildgen.engineering.stair_builder import build_detailed_staircase
from buildgen.engineering.window_builder import build_sash_window, build_panel_door
from buildgen.engineering.chimney_builder import build_chimney_stack
from buildgen.engineering.plumbing_builder import build_plumbing_system
from buildgen.engineering.basement_builder import build_basement
from buildgen.engineering.guttering_builder import build_guttering
from buildgen.engineering.partition_builder import build_partition_wall
from buildgen.engineering.granular_builder import _generate_foundation
from buildgen.engineering.loads import calculate_loads
from buildgen.viz.detailed_viewer import render_full_diagnostic
from buildgen.viz.element_renderer import render_element_summary
from buildgen.viz.export_grouped import export_grouped_glb

# ── Design the structure ──
W, D = 8.5, 10.5
FLOORS = 3
FH = 3.2

model = design_structure(W, D, FLOORS, FH, "brick", "hip", 35.0)
loads = calculate_loads(model)
coll = ElementCollection()

print("Building Georgian Townhouse (complete)...")

# ── BASEMENT ──
print("  Basement...")
coll.elements.extend(build_basement(W, D))

# ── FOUNDATION ──
print("  Foundation...")
_generate_foundation(coll, model, loads)

# ── EXTERIOR WALLS (every brick, all floors) ──
print("  Exterior walls...")
for floor in range(FLOORS):
    fy = floor * FH
    load = loads.foundation_load_per_m / FLOORS
    for name, x1, z1, x2, z2 in [
        ("south", 0, 0, W, 0), ("east", W, 0, W, D),
        ("north", W, D, 0, D), ("west", 0, D, 0, 0),
    ]:
        coll.elements.extend(build_solid_brick_wall(
            x1, z1, x2, z2, fy, FH, bond="flemish", thickness_bricks=2,
            brick_material="facing_brick", load_per_m=load,
            floor_idx=floor, parent=name,
        ))

# ── INTERIOR LOAD-BEARING WALL ──
# Structural centre wall divides the building into two equal bays
# for joist support. It has doorway gaps for room access.
# The front door is off-centre (at x=W/2) so it doesn't clash.
print("  Load-bearing wall...")
LB_WALL_X = W / 2  # Structural centre for equal joist spans

from buildgen.engineering.elements import Element, ElementType as ET2

for floor in range(FLOORS):
    fy = floor * FH

    # The wall has 3 sections with 2 doorway gaps:
    # Section 1: z=1.2 to z=D*0.38 (skip first 1.2m for front door clearance)
    coll.elements.extend(build_solid_brick_wall(
        LB_WALL_X, 1.2, LB_WALL_X, D * 0.38, fy, FH,
        bond="stretcher", thickness_bricks=1,
        brick_material="common_brick",
        load_per_m=loads.foundation_load_per_m / 6,
        floor_idx=floor, parent="wall_centre",
    ))
    # Lintel over front doorway gap (z=0 to z=1.2)
    coll.elements.append(Element(
        element_type=ET2.LINTEL, material_name="oak",
        x=LB_WALL_X, y=fy + 2.15, z=0.6,
        length=0.12, width=1.4, height=0.15,
        parent="wall_centre_lintel", floor_index=floor,
    ))

    # Gap at z=D*0.38 to z=D*0.58 for stair/landing circulation

    # Section 2: z=D*0.58 to z=D-1.2 (skip last 1.2m for rear door clearance)
    coll.elements.extend(build_solid_brick_wall(
        LB_WALL_X, D * 0.58, LB_WALL_X, D - 1.2, fy, FH,
        bond="stretcher", thickness_bricks=1,
        brick_material="common_brick",
        load_per_m=loads.foundation_load_per_m / 6,
        floor_idx=floor, parent="wall_centre",
    ))
    # Lintel over rear doorway gap
    coll.elements.append(Element(
        element_type=ET2.LINTEL, material_name="oak",
        x=LB_WALL_X, y=fy + 2.15, z=D - 0.6,
        length=0.12, width=1.4, height=0.15,
        parent="wall_centre_lintel", floor_index=floor,
    ))
    # Lintel over central stair gap
    coll.elements.append(Element(
        element_type=ET2.LINTEL, material_name="oak",
        x=LB_WALL_X, y=fy + FH - 0.2, z=D * 0.48,
        length=0.12, width=D * 0.22, height=0.15,
        parent="wall_centre_lintel", floor_index=floor,
    ))

# ── INTERIOR PARTITION WALLS (non-load-bearing) ──
print("  Partition walls...")
# Partitions divide the front from back rooms on each floor.
# They run across the building width at about 45% of the depth.
for floor in range(FLOORS):
    fy = floor * FH
    # Front-to-back divider on left wing
    coll.elements.extend(build_partition_wall(
        0, D * 0.45, LB_WALL_X, D * 0.45,
        fy, FH - 0.25,
        has_door=True, door_position=0.5,
        floor_idx=floor, parent=f"part_fb_left_{floor}",
    ))
    # Front-to-back divider on right wing
    coll.elements.extend(build_partition_wall(
        LB_WALL_X, D * 0.45, W, D * 0.45,
        fy, FH - 0.25,
        has_door=True, door_position=0.4,
        floor_idx=floor, parent=f"part_fb_right_{floor}",
    ))

# ── FLOORS (joists, boards, laths, plaster, skirting) ──
print("  Floors...")
for floor in range(FLOORS):
    coll.elements.extend(build_detailed_floor(
        W, D, floor * FH, model.floors[0].max_span, floor,
        is_ground_floor=(floor == 0), parent=f"floor_{floor}",
    ))

# ── ROOF (rafters, battens, slates, ridge, purlins, ties) ──
print("  Roof...")
import math
ROOF_PITCH_DEG = 35.0
ridge_h = (W / 2) * math.tan(math.radians(ROOF_PITCH_DEG))  # Correct: half_span * tan(pitch)
coll.elements.extend(build_detailed_roof(
    W, D, FLOORS * FH, pitch_deg=ROOF_PITCH_DEG, roof_type="hip",
    covering="slate", parent="roof",
))

# ── STAIRS ──
print("  Stairs...")
# Stairs beside the central wall, behind the entrance hall
STAIR_X = LB_WALL_X - 1.2  # Just to the left of the centre wall
STAIR_Z = D * 0.38  # At the circulation gap
for floor in range(FLOORS):
    coll.elements.extend(build_detailed_staircase(
        x=STAIR_X, z=STAIR_Z, base_y=floor * FH,
        total_rise=FH, stair_width=0.86, stair_depth=2.5,
        direction="z", stair_type="straight",
        parent=f"stairs_f{floor}", floor_idx=floor,
    ))

# ── WINDOWS (sash, every component) ──
print("  Windows...")
for floor in range(FLOORS):
    fy = floor * FH
    # Front and back: 3 windows each (skip where doors are on ground floor)
    for wz, wn in [(0, "south"), (D, "north")]:
        for wi in range(3):
            wx = (wi + 0.5) * W / 3

            # Skip the centre window on ground floor front/back (door there)
            if floor == 0 and wi == 1:
                continue

            coll.elements.extend(build_sash_window(
                wx, fy + 0.85 + 0.825, wz,
                parent=f"win_{wn}_{floor}_{wi}", floor_idx=floor,
            ))
    # Sides: 2 windows each
    for wx, wn in [(0, "west"), (W, "east")]:
        for wi in range(2):
            wz = (wi + 0.5) * D / 2
            coll.elements.extend(build_sash_window(
                wx, fy + 0.85 + 0.825, wz, rotation=90,
                panes_wide=2, panes_high_per_sash=3,
                parent=f"win_{wn}_{floor}_{wi}", floor_idx=floor,
            ))

# ── DOORS ──
print("  Doors...")
coll.elements.extend(build_panel_door(W / 2, 1.05, 0, has_fanlight=True, parent="front_door"))
coll.elements.extend(build_panel_door(W / 2, 1.05, D, has_fanlight=False, parent="rear_door"))

# ── DOOR STEPS (stone steps at front and rear) ──
print("  Door steps...")
from buildgen.engineering.elements import Element, ElementType
step_w = 1.400   # Width of steps (wider than door)
step_d = 0.300   # Depth of each step
step_h = 0.150   # Height of each step
num_steps = 3    # 3 steps up to door threshold

# Front steps
for si in range(num_steps):
    # Each step is wider at the bottom (splayed)
    sw = step_w + si * 0.050  # Slightly wider at bottom
    coll.elements.append(Element(
        element_type=ElementType.STONE_BLOCK,
        material_name="limestone",
        x=W / 2,
        y=si * step_h + step_h / 2,
        z=-step_d * (num_steps - si) + step_d / 2,
        length=sw, width=step_d, height=step_h,
        parent="front_steps",
    ))

# Rear steps (simpler, 2 steps)
for si in range(2):
    coll.elements.append(Element(
        element_type=ElementType.STONE_BLOCK,
        material_name="limestone",
        x=W / 2,
        y=si * step_h + step_h / 2,
        z=D + step_d * (2 - si) - step_d / 2,
        length=1.100, width=step_d, height=step_h,
        parent="rear_steps",
    ))

# ── CHIMNEYS (2 stacks, 3 flues each) ──
print("  Chimneys...")
# ridge_h is height of ridge ABOVE eaves (not absolute from ground)
for cx, cz, name in [(1.0, D / 2, "chimney_west"), (W - 1.0, D / 2, "chimney_east")]:
    coll.elements.extend(build_chimney_stack(
        cx, cz, base_y=0, num_floors=FLOORS, floor_height=FH,
        roof_ridge_height=ridge_h, fuel_type="coal",
        num_flues=3, parent=name,
    ))

# ── PLUMBING ──
print("  Plumbing...")
fixtures = [
    [{"type": "sink", "x": 6.5, "z": 8.0}],
    [],
    [
        {"type": "toilet", "x": 6.5, "z": 8.5},
        {"type": "bath", "x": 7.0, "z": 7.5},
        {"type": "basin", "x": 6.0, "z": 8.5},
    ],
]
coll.elements.extend(build_plumbing_system(
    soil_stack_x=7.0, soil_stack_z=8.5,
    base_y=0, num_floors=FLOORS, floor_height=FH,
    roof_height=ridge_h, fixtures_per_floor=fixtures,
    parent="plumbing",
))

# ── GUTTERING ──
print("  Guttering...")
coll.elements.extend(build_guttering(
    W, D, eaves_y=FLOORS * FH,
    roof_overhang=0.300, material="cast_iron",
    parent="guttering",
))

# ── HEATING SYSTEM (boiler, cylinder, radiators, pipes) ──
print("  Heating system...")
from buildgen.engineering.heating_builder import build_heating_system

rooms_for_heating = [
    # Ground floor: hall (left), parlour (right-front), kitchen (right-rear)
    [
        {"name": "hall", "type": "entrance_hall", "x": 0.9, "z": 2.0, "width": 1.5, "depth": 4.0},
        {"name": "parlour", "type": "parlour", "x": 5.0, "z": 2.5, "width": 5.0, "depth": 4.5},
        {"name": "kitchen", "type": "kitchen", "x": 5.0, "z": 7.5, "width": 5.0, "depth": 4.0},
    ],
    # First floor: landing (left), drawing room (right-front), bedroom (right-rear)
    [
        {"name": "drawing", "type": "drawing_room", "x": 5.0, "z": 3.0, "width": 5.0, "depth": 5.0},
        {"name": "master_bed", "type": "master_bedroom", "x": 5.0, "z": 8.0, "width": 5.0, "depth": 4.0},
        {"name": "landing", "type": "landing", "x": 0.9, "z": 5.0, "width": 1.5, "depth": 3.0},
    ],
    # Second floor
    [
        {"name": "bed2", "type": "bedroom", "x": 5.0, "z": 3.0, "width": 5.0, "depth": 5.0},
        {"name": "bed3", "type": "bedroom", "x": 5.0, "z": 8.0, "width": 5.0, "depth": 4.0},
        {"name": "bathroom", "type": "bathroom", "x": 0.9, "z": 8.0, "width": 1.5, "depth": 3.0},
    ],
]

coll.elements.extend(build_heating_system(
    boiler_x=6.5, boiler_z=8.5,
    cylinder_x=7.0, cylinder_z=5.0,
    base_y=0, num_floors=FLOORS, floor_height=FH,
    rooms_per_floor=rooms_for_heating,
    building_width=W, building_depth=D,
    period="georgian", parent="heating",
))

# ── SUMMARY ──
print()
print(f"{'=' * 50}")
print(f"COMPLETE BUILDING: {coll.total_count:,} elements")
print(f"Total mass: {coll.total_mass / 1000:.1f} tonnes ({coll.total_weight:,.0f} kN)")
print()

counts = coll.count_by_type()
for t, c in sorted(counts.items(), key=lambda x: -x[1])[:25]:
    print(f"  {t:20s}: {c:>7,}")

print()
failed = coll.check_all_stresses()
print(f"Structural checks: {len(failed)} failures / {coll.total_count:,} elements")
if failed:
    for e in failed[:5]:
        print(f"  FAIL: {e.element_type.value} — {e.stress_notes}")

# ── EXPORT ──
print()
print("Exporting...")

# Grouped GLB for interactive viewer
print("  Grouped GLB...")
group_counts = export_grouped_glb(
    coll, "output/building_grouped.glb", skip_mortar=True,
    building_width=W, building_depth=D,
    eaves_height=FLOORS * FH, ridge_height_above_eaves=ridge_h,
)
for g, c in sorted(group_counts.items(), key=lambda x: -x[1]):
    print(f"    {g:20s}: {c:,}")

# Diagnostic views
print("  Diagnostic views...")
render_full_diagnostic(
    coll, "output/diagnostic",
    building_width=W, building_depth=D,
    num_floors=FLOORS, floor_height=FH,
    title="Georgian Townhouse (Complete)",
)

# Element analysis
print("  Element analysis...")
render_element_summary(coll, "output/element_analysis.png")

print()
print("Done! Open viewer.html in a browser to view the 3D model.")
print("  (or open output/building_grouped.glb in Blender)")
