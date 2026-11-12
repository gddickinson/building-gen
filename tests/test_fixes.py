"""Regression tests for bugs fixed while adding the web interface (2026-11-11).

Each test failed before its fix; see SESSION_LOG.md for what changed.
"""
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
