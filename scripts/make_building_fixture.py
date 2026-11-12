"""Write tests/fixtures/building_fixture.json: what the Python generator produces for a set of cases, for the
JS port's node tests (src/buildgen/web/static/*.test.mjs) and the "fixture is current" check in tests/test_web.py.

Run: python scripts/make_building_fixture.py
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from buildgen.web import service  # noqa: E402

OUT = ROOT / "tests" / "fixtures" / "building_fixture.json"


def build() -> dict:
    out = {"templates": service.templates(), "cases": [], "random": []}
    for t, s, ov in service.reference_cases():
        r = service.generate(t, s, ov)
        d = service.describe(r)
        d["overrides"] = ov
        d["glb_sha256"] = service.glb_sha256(r)
        d["glb_length"] = len(service.glb_bytes(r))
        out["cases"].append(d)
    for seed in (0, 1, 42, 123456789, 2**40 + 7):
        rng = random.Random(seed)
        out["random"].append({"seed": seed, "random": [rng.random() for _ in range(5)],
                              "uniform": [rng.uniform(-0.3, 0.3) for _ in range(5)],
                              "choice": [rng.choice(["tr", "tl", "br", "bl"]) for _ in range(20)]})
    return out


if __name__ == "__main__":
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    print(f"{len(data['cases'])} cases -> {OUT} ({OUT.stat().st_size / 1e3:.0f} kB)")
