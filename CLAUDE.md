# building-gen

Procedural 3D building generator (Python package `buildgen` in `src/`) with a web interface and a JS port of the
generator in `src/buildgen/web/static/`. Navigation map: @INTERFACE.md. Progress log: SESSION_LOG.md.

- Tests: `PYTHONPATH=src python -m pytest -q` (all pass). Web: `python -m pytest -q tests/test_web.py`.
- Any change to generation code (program/, layout/, geometry/, style/) must be mirrored in the JS port (`bg_*.js`);
  then rerun `python scripts/make_building_fixture.py` and `node src/buildgen/web/static/bg_engine.test.mjs`.
