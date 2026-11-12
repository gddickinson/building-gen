# SESSION_LOG

## 2026-11-11: web interface, static site, bug fixes (branch `web-interface`)
- Read George's review of building-gen (UK_buildings/docs/building_gen_review.md) first; its observations of solid walls,
  roofs and missing windows led to the fixes below.
- Bug fixes, each its own commit with a regression test in `tests/test_fixes.py`:
  1. `--list-types` offered `building_type_rules` (a rules reference) as a building type; generating it built an empty box.
  2. Door/window openings were cut with trimesh booleans, which need manifold3d or a Blender install: without one every
     wall was solid; with Blender a townhouse took 112 s. Walls are now built from solid pieces around openings.
  3. Slabs with stairwell holes were fan-triangulated over the outer ring, covering the holes; now built from boxes.
  4. Roofs: ridge always ran front to back (pyramid hip / wrong gable on the wide cottage), and all roof faces pointed down.
  5. Grid layouts gave windows only to room edges spanning a whole footprint side (cottage: no ground-floor windows).
- Second round (George: "fix any other problems you come across"):
  6. Rooms overlapped: carved closets inside their host (host now L-shaped, `RoomPolygon.main_bounds` for fittings),
     hall/landing over the stairwell (now stop at its foot), grid cells shared by two rooms (larger room trimmed).
     Fixed `test_room_aspect_ratios`.
  7. Automatic stairwells used 3.0 m² min area vs 4.0 in ROOM_CONSTRAINTS. Fixed `test_rooms_not_too_small`.
  8. 3D model was a mirror image of the plans: plan y now maps to -z (GeometryBuilder._add), screenshot cameras at +z.
  Regenerated output/*_s42 (.glb, plans, sheets, 3d_views) and docs/images copies. Full pytest now 0 failures.
- Not changed: engineering outputs.
- Third round: `screenshot_3d` used trimesh/pyglet off-screen rendering (pyglet missing -> warning only, camera never
  applied) and `generate_and_save` swallowed errors, so the `*_3d_perspective.png` files were blank. Replaced with a numpy
  z-buffer software renderer (`render_scene_png`) that uses the camera; errors now propagate. Regenerated the 5 PNGs.
- Web: FastAPI app + static site; full JS port of the generator, byte-identical .glb on the 22 reference cases and on a
  360-case stress run (all types, seeds 100-159). Port 8228.
- Mac mini not used.
