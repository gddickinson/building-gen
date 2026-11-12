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
- Pre-existing failures (before any change): `TestRoomSizes::test_rooms_not_too_small` (stairwell 3.0 m² < 3.2) and
  `test_room_aspect_ratios` (seed 2 entrance hall 1.1 × 7.9 m) on the BSP townhouse. Not changed.
- Needs George's decision (not changed): BSP `_carve_small_room` keeps the host room at its full bounding box, so it
  overlaps the carved room; the 3D model is mirrored relative to the plans (plan y -> +z with y up).
- Web: FastAPI app + static site; full JS port of the generator, byte-identical .glb on the 22 reference cases and on a
  360-case stress run (all types, seeds 100-159). Port 8228.
- Mac mini not used.
