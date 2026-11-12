# INTERFACE.md: navigation map

## Python package `src/buildgen/`
| Path | Contents |
|---|---|
| `pipeline.py` | `Pipeline.generate(type, style, seed)` -> `PipelineResult` (program, floor_plans, building, style); `generate_and_save` writes plans/sheet PNGs and the .glb |
| `cli.py`, `__main__.py` | `buildgen` command: `--type --style --seed --count --output --list-types --list-styles` |
| `program/generator.py` | `ProgramGenerator` (template YAML -> `BuildingProgram`), `is_building_template` |
| `program/models.py`, `constraints.py` | `RoomSpec`, `FloorProgram`, `BuildingProgram`, `RoomType`; `ROOM_CONSTRAINTS` etc. |
| `program/templates/*.yaml` | 6 building templates (5 grid, `townhouse` BSP) + `building_type_rules.yaml` (design-rules reference, not a template) |
| `layout/engine.py`, `subdivide.py` | BSP layout for template types: hall column + wings, walls, doors, windows |
| `layout/grid_layout.py` | `generate_from_grid` for reference (grid) templates |
| `layout/fixtures.py`, `models.py`, `validator.py` | fixtures placed in rooms; `FloorPlan`, `RoomPolygon`, `WallSegment`, `Opening` |
| `geometry/builder.py` | `GeometryBuilder.build(floor_plans, style)` -> `Building3D` (trimesh Scene: slabs, walls, stairs, ceiling, roof) |
| `geometry/walls.py` | `build_wall_mesh`, `opening_span`, `build_wall_with_openings` (no boolean engine needed) |
| `geometry/slabs.py` | `solid_rects`, `stairwell_holes`, `build_slab_with_holes` |
| `geometry/roofs.py`, `stairs.py` | hip / gable / flat roofs; straight, L, U and spiral stairs |
| `style/library.py`, `models.py` | `StyleLibrary` (built-in `georgian`), `StyleParams` |
| `engineering/` | detailed element-by-element builder (bricks, rafters, systems, loads); driven by `build_complete.py` |
| `viz/` | matplotlib plans/sheets/diagnostics, grouped glTF export for `viewer.html` |
| `web/` | web interface (below) |

## Web interface `src/buildgen/web/`
| Path | Contents |
|---|---|
| `app.py` | FastAPI: `/api/info, /types, /templates, /styles, /verify` (exported to the static site via `STATIC_ENDPOINTS`), `/api/building`, `/api/glb` (local only) |
| `service.py` | `generate(type, seed, overrides)`, `describe`, `glb_bytes`, `templates`, `reference_cases`, `STYLE_CONTROLS` |
| `static/index.html, main.js, core.js, style.css, style_app.css, static_api.js` | shell, router (kit), theme, static-site API answers |
| `static/py_random.js` | bit-exact Python `random.Random` (MT19937) |
| `static/bg_util.js` | Python `round`/`sum`, shapely box rings, GEOS distances, interpolate |
| `static/bg_program.js` | `generateProgram`, `STYLES` (port of program/generator.py + style library) |
| `static/bg_subdivide.js`, `bg_layout.js`, `bg_grid.js`, `bg_fixtures.js` | ports of layout/subdivide.py, engine.py, grid_layout.py, fixtures.py |
| `static/bg_mesh.js`, `bg_geometry.js`, `bg_stairs.js` | trimesh-like meshes + `fixNormals`; walls/slabs/roofs/`buildGeometry`; stairs |
| `static/bg_pipeline.js` | `generateBuilding(templates, type, seed, overrides)` |
| `static/bg_glb.js` | `exportGlb(nodes)`: trimesh-identical .glb bytes |
| `static/gl_math.js`, `gl_view.js`, `plan_view.js`, `snapshots.js` | raw WebGL viewer + orbit camera, 2D plan canvas, off-screen renders |
| `static/building_data.js` | data loading, stats, SHA-256, node classification |
| `static/home.js, generate.js, gallery.js, types.js, detail.js, verify.js, about.js` | pages |
| `static/bg_engine.test.mjs` | node test: JS vs `tests/fixtures/building_fixture.json` (plans, meshes, .glb SHA-256) |

## Scripts and tests
| Path | Contents |
|---|---|
| `run_web.py` | starts the app on 127.0.0.1:8228 |
| `scripts/build_static.py`, `screenshots.py` | static site export (+ detail images from `docs/images`); Playwright smoke test / README shots |
| `scripts/make_building_fixture.py` | writes `tests/fixtures/building_fixture.json` from the Python generator |
| `tests/test_pipeline.py` | original pipeline tests |
| `tests/test_fixes.py` | regression tests for the bugs fixed on 2026-11-11 |
| `tests/test_web.py` | API, static build, fixture currency, node tests |
| `build_complete.py`, `viewer.html`, `view.sh` | detailed townhouse build and its standalone viewer |
