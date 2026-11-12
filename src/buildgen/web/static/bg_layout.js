// Stage 2 for template (BSP) types: port of buildgen/layout/engine.py (LayoutEngine). Rooms are boxes b =
// [minx, miny, maxx, maxy] in plan metres (y = 0 is the street front).
import { PyRandom } from './py_random.js';
import { boundaryDist, interpolate, pyInt, pyRound, roomRing, segLength, segSegDist } from './bg_util.js';
import { subdivideFloor, room } from './bg_subdivide.js';
import { placeFixturesInRoom } from './bg_fixtures.js';

export const opening = (type, position, width, height, sill = 0.0) => ({ type, position, width, height, sill_height: sill });
export const roomByName = (plan, name) => plan.rooms.find(r => r.name === name) || null;

export function layoutProgram(program) {
  const rng = new PyRandom(program.seed);
  const fb = [0, 0, program.footprint_width, program.footprint_depth];
  let stair = null;
  const stairRooms = program.floors.flatMap(f => f.rooms.filter(r => r.is_stairwell));
  if (stairRooms.length) {
    const sw = stairRooms[0], swW = 1.0, swD = Math.max(sw.min_area / swW, 2.5);
    let sx = (program.footprint_width - swW) / 2 + rng.uniform(-0.3, 0.3);
    let sy = program.footprint_depth * 0.35 + rng.uniform(-0.3, 0.3);
    sx = Math.max(0.3, Math.min(sx, program.footprint_width - swW - 0.3));
    sy = Math.max(0.3, Math.min(sy, program.footprint_depth - swD - 0.3));
    stair = [sx, sy, sx + swW, sy + swD];
  }
  return program.floors.map(fp => generateFloor(fp, fb, stair, program, rng));
}

function generateFloor(fp, fb, stair, program, rng) {
  const stairSpecs = fp.rooms.filter(r => r.is_stairwell), normal = fp.rooms.filter(r => !r.is_stairwell);
  const rooms = subdivideFloor(fb, normal, stair, rng);
  if (stair && stairSpecs.length) rooms.push(room(stairSpecs[0].name, stairSpecs[0].room_type, stair, fp.floor_index));
  const plan = { floor_index: fp.floor_index, rooms, footprint: fb };
  plan.walls = extractWalls(plan, program.wall_thickness);
  placeDoors(plan, fp);
  placeWindows(plan, fp);
  for (const r of plan.rooms) r.fixtures = placeFixturesInRoom(r.main || r.b, r.room_type, rng);
  return plan;
}

const close = (a, b, tol) => Math.abs(a[0] - b[0]) < tol && Math.abs(a[1] - b[1]) < tol;
const edgesMatch = (s1, e1, s2, e2, tol = 0.05) => (close(s1, s2, tol) && close(e1, e2, tol)) || (close(s1, e2, tol) && close(e1, s2, tol));

function extractWalls(plan, thickness) {
  const walls = [];
  for (const r of plan.rooms) {
    const c = roomRing(r);
    for (let i = 0; i < c.length - 1; i++) {
      const s = [pyRound(c[i][0], 4), pyRound(c[i][1], 4)], e = [pyRound(c[i + 1][0], 4), pyRound(c[i + 1][1], 4)];
      const ext = segLength(s, e) > 0.01 && boundaryDist(plan.footprint, s, e) < 0.01;
      if (walls.some(w => edgesMatch(w.start, w.end, s, e))) continue;
      walls.push({ start: s, end: e, wall_type: ext ? 'exterior' : 'interior', thickness });
    }
  }
  return walls;
}

function findSharedEdge(a, b, tol = 0.05) {
  const ca = roomRing(a), cb = roomRing(b);
  for (let i = 0; i < ca.length - 1; i++) for (let j = 0; j < cb.length - 1; j++)
    if (edgesMatch(ca[i], ca[i + 1], cb[j], cb[j + 1], tol)) return [ca[i], ca[i + 1]];
  for (let i = 0; i < ca.length - 1; i++) for (let j = 0; j < cb.length - 1; j++)
    if (segSegDist(ca[i], ca[i + 1], cb[j], cb[j + 1]) < tol) return [ca[i], ca[i + 1]];
  return null;
}

function placeDoors(plan, fp) {
  const placed = new Set();
  for (const adj of fp.adjacencies) {
    if (adj.adj_type === 'must_not') continue;
    const a = roomByName(plan, adj.room_a), b = roomByName(plan, adj.room_b);
    if (!a || !b) continue;
    const shared = findSharedEdge(a, b);
    if (!shared) continue;
    const key = [adj.room_a, adj.room_b].sort().join('|');
    if (placed.has(key)) continue;
    placed.add(key);
    a.openings.push(opening('door', [(shared[0][0] + shared[1][0]) / 2, (shared[0][1] + shared[1][1]) / 2], 0.9, 2.1));
  }
  if (plan.floor_index === 0) {
    const ent = roomByName(plan, 'entrance_hall');
    if (ent) {
      const fb = plan.footprint, eb = ent.b;
      const x = Math.max(eb[0] + 0.5, Math.min((fb[0] + fb[2]) / 2.0, eb[2] - 0.5));
      ent.openings.push(opening('front_door', [x, fb[1]], 1.1, 2.4));
    }
  }
}

function placeWindows(plan, fp) {
  for (const r of plan.rooms) {
    const spec = fp.rooms.find(s => s.name === r.name);
    if (spec && !spec.needs_window) continue;
    const c = roomRing(r);
    for (let i = 0; i < c.length - 1; i++) {
      const len = segLength(c[i], c[i + 1]);
      if (len < 1.0 || boundaryDist(plan.footprint, c[i], c[i + 1]) > 0.01) continue;
      const n = Math.max(1, pyInt(len / 2.0));
      for (let k = 0; k < n; k++) r.openings.push(opening('window', interpolate(c[i], c[i + 1], (k + 0.5) / n), 1.0, 1.4, 0.9));
    }
  }
}
