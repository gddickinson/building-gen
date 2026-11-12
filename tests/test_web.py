"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from buildgen.web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific -------------------------------------------------------------------------------------------
FIXTURE = ROOT / "tests" / "fixtures" / "building_fixture.json"


def _close(a, b, rtol=1e-9):
    return abs(a - b) <= rtol * max(1.0, abs(a), abs(b))


def test_fixture_is_current():
    """tests/fixtures/building_fixture.json matches the Python generator (rerun scripts/make_building_fixture.py)."""
    import json
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_building_fixture
    want = json.loads(FIXTURE.read_text())
    got = json.loads(json.dumps(make_building_fixture.build()))
    assert got["templates"] == want["templates"] and got["random"] == want["random"]
    assert len(got["cases"]) == len(want["cases"])
    for g, w in zip(got["cases"], want["cases"]):
        assert (g["type"], g["seed"], g["overrides"]) == (w["type"], w["seed"], w["overrides"])
        assert (g["vertices"], g["faces"], len(g["nodes"])) == (w["vertices"], w["faces"], len(w["nodes"]))
        for gn, wn in zip(g["nodes"], w["nodes"]):
            assert gn["name"] == wn["name"] and all(_close(a, b) for a, b in zip(gn["sum"], wn["sum"]))
        for gp, wp in zip(g["plans"], w["plans"]):
            assert [r["name"] for r in gp["rooms"]] == [r["name"] for r in wp["rooms"]]
            for gr, wr in zip(gp["rooms"], wp["rooms"]):
                assert all(_close(a, b) for a, b in zip(gr["bounds"], wr["bounds"]))


def test_building_endpoint_and_glb():
    r = client.get("/api/building?type=cottage&seed=42&roof_type=gable")
    assert r.status_code == 200
    d = r.json()
    assert d["num_floors"] == 2 and d["overrides"] == {"roof_type": "gable"}
    g = client.get("/api/glb?type=cottage&seed=42&roof_type=gable")
    assert g.status_code == 200 and g.content[:4] == b"glTF" and len(g.content) == d["glb_length"]


@pytest.mark.parametrize("q", ["type=nope", "seed=x", "roof_type=dome", "roof_pitch=9", "colour=red"])
def test_bad_parameters_rejected(q):
    assert client.get("/api/building?" + q).status_code == 400


def test_types_exclude_rules_file():
    names = [t["name"] for t in client.get("/api/types").json()]
    assert "building_type_rules" not in names and len(names) == 6
