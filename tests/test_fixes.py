"""Regression tests for bugs fixed while adding the web interface (2026-11-11).

Each test failed before its fix; see SESSION_LOG.md for what changed.
"""
import numpy as np
import pytest

from buildgen.pipeline import Pipeline
from buildgen.program import ProgramGenerator


def test_rules_file_is_not_listed_as_a_building_type():
    # building_type_rules.yaml is a design-rules reference, not a template: --list-types offered it and
    # generating it built an empty default box.
    types = ProgramGenerator().available_types()
    assert "building_type_rules" not in types
    assert {"townhouse", "cottage", "tavern", "victorian_terrace",
            "townhouse_reference", "grosvenor_townhouse"} <= set(types)


def test_generating_a_non_template_raises():
    with pytest.raises(ValueError):
        Pipeline().generate("building_type_rules", "georgian", 1)


def _node_meshes(result, prefix=""):
    """{node name: mesh} for the scene nodes whose name starts with prefix."""
    scene = result.building.mesh
    out = {}
    for node in scene.graph.nodes_geometry:
        if node.startswith(prefix):
            out[node] = scene.geometry[scene.graph[node][1]]
    return out


def _wall_volume(result):
    return sum(g.volume for name, g in _node_meshes(result).items() if "_wall_" in name)


def test_openings_cut_without_a_boolean_engine(monkeypatch):
    # Door and window openings were cut with trimesh boolean difference, which needs manifold3d or Blender;
    # without one the exception was swallowed and every wall came out solid (and with Blender each cut took ~1 s).
    import trimesh

    def no_engine(*a, **k):
        raise ImportError("no boolean engine")
    monkeypatch.setattr(trimesh.Trimesh, "difference", no_engine)
    r = Pipeline().generate("cottage", "georgian", 42)
    # Uncut volume: every wall as a full box.
    full = 0.0
    for plan in r.floor_plans:
        for w in plan.walls:
            full += w.length * w.thickness * r.style.floor_height
    assert _wall_volume(r) < full - 1.0  # at least ~1 m^3 of doors and windows removed


def _segment_hits(mesh, a, b):
    """True if the segment a->b crosses any triangle of mesh (Moller-Trumbore, no rtree needed)."""
    import numpy as np
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    tri = mesh.triangles
    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    p = np.cross(d, e2)
    det = (e1 * p).sum(1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1), 0)
    s = a - tri[:, 0]
    u = (s * p).sum(1) * inv
    q = np.cross(s, e1)
    v = (d * q).sum(1) * inv
    t = (e2 * q).sum(1) * inv
    return bool(np.any(ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t >= 0) & (t <= 1)))


def test_front_door_is_open():
    r = Pipeline().generate("cottage", "georgian", 42)
    ground = r.floor_plans[0]
    door = [o for room in ground.rooms for o in room.openings if o.opening_type.value == "front_door"][0]
    x, z = door.position
    walls = list(_node_meshes(r, "floor_0_wall_").values())
    assert walls
    hit = [_segment_hits(g, (x, 1.0, z - 1.0), (x, 1.0, z + 0.3)) for g in walls]
    assert not any(hit), "a wall blocks the front door"


@pytest.mark.parametrize("btype", ["cottage", "tavern", "townhouse"])
def test_stairwell_hole_is_open_in_floor_slab(btype):
    # The slab with stairwell holes was triangulated as a fan over its outer ring, so its top and bottom
    # faces covered the holes: only the hole's side walls existed.
    r = Pipeline().generate(btype, "georgian", 42)
    checked = 0
    for plan in r.floor_plans:
        y = plan.floor_index * r.style.floor_height
        slab = _node_meshes(r, f"floor_{plan.floor_index}_slab")[f"floor_{plan.floor_index}_slab"]
        for room in plan.rooms:
            if room.room_type != "stairwell":
                continue
            cx, cz = room.centroid
            assert not _segment_hits(slab, (cx, y - 1, cz), (cx, y + 1, cz)), f"slab covers {room.name}"
            checked += 1
    assert checked


@pytest.mark.parametrize("roof_type", ["hip", "gable"])
def test_roof_ridge_runs_along_the_longer_side(roof_type):
    # The ridge always ran front to back: on a building wider than deep (the cottage) the hip roof
    # collapsed to a pyramid and the gable spanned the long way, against the docstrings.
    from dataclasses import replace

    from buildgen.geometry.roofs import build_roof_mesh
    from buildgen.style import StyleLibrary
    from shapely.geometry import box

    style = replace(StyleLibrary().get("georgian"), roof_type=roof_type)
    for w, d in [(9.0, 5.0), (5.0, 9.0)]:
        roof = build_roof_mesh(box(0, 0, w, d), 6.0, style)
        v = roof.vertices
        ridge = v[v[:, 1] > v[:, 1].min() + 1e-6]
        span_x = ridge[:, 0].max() - ridge[:, 0].min()
        span_z = ridge[:, 2].max() - ridge[:, 2].min()
        if w > d:
            assert span_x > 1.0 and span_z < 1e-9
        else:
            assert span_z > 1.0 and span_x < 1e-9
        assert (roof.face_normals[:, 1] > -1e-9).all()  # slopes face up, gable ends are vertical


def test_flat_roof_faces_up():
    from dataclasses import replace

    from buildgen.geometry.roofs import build_roof_mesh
    from buildgen.style import StyleLibrary
    from shapely.geometry import box

    roof = build_roof_mesh(box(0, 0, 6, 9), 6.0, replace(StyleLibrary().get("georgian"), roof_type="flat"))
    top = roof.face_normals[np.abs(roof.face_normals[:, 1]) > 0.5]
    assert len(top) and (top[:, 1] > 0).all()


@pytest.mark.parametrize("btype", ["cottage", "tavern", "victorian_terrace", "townhouse_reference", "grosvenor_townhouse"])
def test_grid_rooms_on_the_outside_get_windows(btype):
    # Reference (grid) layouts only gave windows to room edges that matched a whole side of the footprint,
    # so rooms sharing a facade with a neighbour had none (the cottage had no ground-floor windows).
    no_window = {"stairwell", "landing", "storage", "pantry", "wc", "dressing_room", "hallway"}
    for seed in (1, 42):
        r = Pipeline().generate(btype, "georgian", seed)
        for plan in r.floor_plans:
            w, d = plan.footprint.bounds[2], plan.footprint.bounds[3]
            for room in plan.rooms:
                if room.room_type in no_window:
                    continue
                b = room.bounds
                outside = [(b[2] - b[0]) >= 1 and (abs(b[1]) < 0.01 or abs(b[3] - d) < 0.01),
                           (b[3] - b[1]) >= 1 and (abs(b[0]) < 0.01 or abs(b[2] - w) < 0.01)]
                if any(outside):
                    wins = [o for o in room.openings if o.opening_type.value == "window"]
                    assert wins, f"{btype} seed {seed} floor {plan.floor_index}: {room.name} has no window"


@pytest.mark.parametrize("btype", ["townhouse", "townhouse_reference", "grosvenor_townhouse", "victorian_terrace", "cottage", "tavern"])
def test_no_two_rooms_on_a_floor_overlap(btype):
    # In the template townhouse a small room carved from a corner of a larger one left the larger room at its
    # full size, and the entrance hall / landing ran over the stairwell.
    for seed in range(10):
        r = Pipeline().generate(btype, "georgian", seed)
        for plan in r.floor_plans:
            rooms = plan.rooms
            for i, a in enumerate(rooms):
                for b in rooms[i + 1:]:
                    ov = a.polygon.intersection(b.polygon).area
                    assert ov < 1e-6, f"{btype} seed {seed} floor {plan.floor_index}: {a.name} overlaps {b.name} by {ov:.2f} m2"
