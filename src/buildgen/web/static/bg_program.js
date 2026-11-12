// Stage 1 and the style library: port of buildgen/program/generator.py (ProgramGenerator.generate) and the built-in
// styles of buildgen/style/library.py + StyleParams defaults (style/models.py). Templates are the YAML files as
// JSON (served by the API as /templates).
import { PyRandom } from './py_random.js';

const g = (o, k, d) => (o && o[k] !== undefined && o[k] !== null ? o[k] : d);

// StyleParams defaults overridden by the built-in "georgian" style (the only style buildgen has).
export const STYLES = {
  georgian: {
    name: 'georgian', floor_height: 3.2, slab_thickness: 0.25, wall_thickness: 0.35, window_width: 1.05,
    window_height: 1.6, window_sill_height: 0.85, door_width: 0.9, door_height: 2.1, front_door_width: 1.2,
    front_door_height: 2.5, roof_type: 'hip', roof_pitch: 0.4, roof_overhang: 0.25, stair_riser: 0.19, stair_tread: 0.28,
    exterior_wall_color: [190, 130, 85, 255], interior_wall_color: [240, 235, 225, 255], roof_color: [70, 65, 60, 255],
    floor_color: [200, 200, 200, 255], stair_color: [150, 110, 70, 255], window_color: [150, 180, 220, 200],
    door_color: [100, 70, 50, 255],
  },
};

export const isGridTemplate = t => g(t, 'layout_type', null) === 'grid';

export function makeRoomSpec(o) {
  const r = { min_aspect: 0.4, max_aspect: 1.0, needs_exterior_wall: true, needs_window: true, is_stairwell: false, floor: 0, ...o };
  r.target_area = (r.min_area + r.max_area) / 2;
  return r;
}

export function generateProgram(tmpl, buildingType, style = 'georgian', seed = 0) {
  const rng = new PyRandom(seed);
  const fp = g(tmpl, 'footprint', {});
  const program = { building_type: buildingType, style, seed, floors: [] };
  program.footprint_width = g(fp, 'width', 8.0) + rng.uniform(-g(fp, 'width_var', 1.0), g(fp, 'width_var', 1.0));
  program.footprint_depth = g(fp, 'depth', 12.0) + rng.uniform(-g(fp, 'depth_var', 1.5), g(fp, 'depth_var', 1.5));
  program.wall_thickness = g(fp, 'wall_thickness', 0.3);
  const floorDefs = g(tmpl, 'floors', []);

  for (const fd of floorDefs) {
    const idx = fd.index;
    const floor = { floor_index: idx, rooms: [], adjacencies: [] };
    for (const rd of g(fd, 'rooms', [])) {
      if (g(rd, 'optional', false) && rng.random() > g(rd, 'probability', 0.5)) continue;
      let minA = g(rd, 'min_area', 8.0), maxA = g(rd, 'max_area', 16.0);
      const v = g(rd, 'area_var', 1.0);
      minA = Math.max(4.0, minA + rng.uniform(-v, v));
      maxA = Math.max(minA + 1.0, maxA + rng.uniform(-v, v));
      floor.rooms.push(makeRoomSpec({
        name: rd.name, room_type: g(rd, 'type', 'generic'), min_area: minA, max_area: maxA,
        min_aspect: g(rd, 'min_aspect', 0.4), max_aspect: g(rd, 'max_aspect', 1.0),
        needs_exterior_wall: g(rd, 'needs_exterior_wall', true), needs_window: g(rd, 'needs_window', true),
        is_stairwell: g(rd, 'is_stairwell', false), floor: idx,
      }));
    }
    const names = new Set(floor.rooms.map(r => r.name));
    for (const ad of g(fd, 'adjacencies', [])) {
      if (names.has(ad.a) && names.has(ad.b)) floor.adjacencies.push({ room_a: ad.a, room_b: ad.b, adj_type: g(ad, 'type', 'should') });
    }
    if (floorDefs.length > 1 && !floor.rooms.some(r => r.is_stairwell)) {
      floor.rooms.push(makeRoomSpec({
        name: `stairs_${idx}`, room_type: 'stairwell', min_area: 4.0, max_area: 5.0, // ROOM_CONSTRAINTS stairwell min_area
        needs_exterior_wall: false, needs_window: false, is_stairwell: true, floor: idx,
      }));
    }
    program.floors.push(floor);
  }
  return program;
}
