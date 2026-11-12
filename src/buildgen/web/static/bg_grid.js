// Stage 2 for reference (grid) types: port of buildgen/layout/grid_layout.py (generate_from_grid). Each room takes
// a cell (or part of one, or a span of cells) of a rows x columns grid scaled to a varied footprint.
import { PyRandom } from './py_random.js';
import { boxRing, boundaryDist, bufferedOverlapArea, interpolate, pyInt, pyRound, pySum, segLength, segSegDist } from './bg_util.js';
import { room } from './bg_subdivide.js';
import { opening, roomByName } from './bg_layout.js';
import { placeFixturesInRoom } from './bg_fixtures.js';

const g = (o, k, d) => (o && o[k] !== undefined && o[k] !== null ? o[k] : d);
const NO_WINDOW = new Set(['stairwell', 'landing', 'storage', 'pantry', 'wc', 'dressing_room', 'hallway']);
const edgeKey = (s, e) => { const [a, b] = (s[0] < e[0] || (s[0] === e[0] && s[1] <= e[1])) ? [s, e] : [e, s]; return `${a[0]},${a[1]}|${b[0]},${b[1]}`; };

export function generateFromGrid(tmpl, seed = 0) {
  const rng = new PyRandom(seed);
  const fp = g(tmpl, 'footprint', {});
  const width = g(fp, 'width', 8.5) + rng.uniform(-g(fp, 'width_var', 0.8), g(fp, 'width_var', 0.8));
  const depth = g(fp, 'depth', 11.0) + rng.uniform(-g(fp, 'depth_var', 1.0), g(fp, 'depth_var', 1.0));
  const wallT = g(fp, 'wall_thickness', 0.35);
  const grid = g(tmpl, 'grid', {});
  const colWidths = g(grid, 'col_widths', [0.42, 0.16, 0.42]);
  const totalCw = pySum(colWidths);
  const cols = [];
  let x = 0.0;
  for (const cw of colWidths) {
    const w = width * (cw / totalCw), jitter = rng.uniform(-0.1, 0.1);
    cols.push([x, x + w + jitter]);
    x += w + jitter;
  }
  if (cols.length) cols[cols.length - 1] = [cols[cols.length - 1][0], width];

  const plans = [];
  for (const fd of g(grid, 'floors', [])) {
    const idx = fd.index, fracs = g(fd, 'rows', [0.5, 0.5]), totalRf = pySum(fracs);
    const rows = [];
    let y = 0.0;
    for (const rf of fracs) {
      const h = depth * (rf / totalRf), jitter = rng.uniform(-0.15, 0.15);
      rows.push([y, y + h + jitter]);
      y += h + jitter;
    }
    if (rows.length) rows[rows.length - 1] = [rows[rows.length - 1][0], depth];
    const rooms = [], fb = [0, 0, width, depth];
    for (const rd of g(fd, 'rooms', [])) {
      if (g(rd, 'optional', false) && rng.random() > g(rd, 'probability', 0.5)) continue;
      const col = g(rd, 'col', 0), row = g(rd, 'row', 0);
      if (col >= cols.length || row >= rows.length) continue;
      let [x1, x2] = cols[col], [y1, y2] = rows[row];
      if (x2 <= x1 || y2 <= y1) continue;
      const half = g(rd, 'half', null), frac = g(rd, 'fraction', 0.5);
      if (half === 'top') y1 = y2 - (y2 - y1) * frac;
      else if (half === 'bottom') y2 = y1 + (y2 - y1) * frac;
      else if (half === 'left') x2 = x1 + (x2 - x1) * frac;
      else if (half === 'right') x1 = x2 - (x2 - x1) * frac;
      const cs = g(rd, 'col_span', 1), rs = g(rd, 'row_span', 1);
      if (cs > 1 && col + cs - 1 < cols.length) x2 = cols[col + cs - 1][1];
      if (rs > 1 && row + rs - 1 < rows.length) y2 = rows[row + rs - 1][1];
      rooms.push(room(rd.name, g(rd, 'type', 'generic'), [x1, y1, x2, y2], idx));
    }
    const plan = { floor_index: idx, rooms, footprint: fb };
    plan.walls = extractWalls(plan, wallT);
    placeDoors(plan);
    placeWindows(plan);
    for (const r of plan.rooms) r.fixtures = placeFixturesInRoom(r.b, r.room_type, rng);
    plans.push(plan);
  }
  return { plans, width, depth };
}

function extractWalls(plan, thickness) {
  const walls = [], ext = new Set(), seen = new Set();
  const fc = boxRing(plan.footprint);
  for (let i = 0; i < fc.length - 1; i++) {
    const s = [pyRound(fc[i][0], 2), pyRound(fc[i][1], 2)], e = [pyRound(fc[i + 1][0], 2), pyRound(fc[i + 1][1], 2)];
    if (segLength(s, e) < 0.01) continue;
    walls.push({ start: s, end: e, wall_type: 'exterior', thickness });
    ext.add(edgeKey(s, e));
  }
  for (const r of plan.rooms) {
    const c = boxRing(r.b);
    for (let i = 0; i < c.length - 1; i++) {
      const s = [pyRound(c[i][0], 2), pyRound(c[i][1], 2)], e = [pyRound(c[i + 1][0], 2), pyRound(c[i + 1][1], 2)];
      if (segLength(s, e) < 0.01) continue;
      const key = edgeKey(s, e);
      if (ext.has(key) || seen.has(key)) continue;
      seen.add(key);
      const mid = [(s[0] + e[0]) / 2, (s[1] + e[1]) / 2];
      const onB = boundaryDist(plan.footprint, s) < 0.1 && boundaryDist(plan.footprint, e) < 0.1 && boundaryDist(plan.footprint, mid) < 0.1;
      if (!onB) walls.push({ start: s, end: e, wall_type: 'interior', thickness: thickness * 0.4 });
    }
  }
  return walls;
}

function sharedEdge(a, b) {
  const ca = boxRing(a.b), cb = boxRing(b.b);
  for (let i = 0; i < ca.length - 1; i++) {
    if (segLength(ca[i], ca[i + 1]) < 0.1) continue;
    for (let j = 0; j < cb.length - 1; j++) {
      if (segLength(cb[j], cb[j + 1]) < 0.1) continue;
      if (segSegDist(ca[i], ca[i + 1], cb[j], cb[j + 1]) < 0.05
        && bufferedOverlapArea(ca[i], ca[i + 1], cb[j], cb[j + 1], 0.02) > 0.01) return [ca[i], ca[i + 1]];
    }
  }
  return null;
}

function placeDoors(plan) {
  const placed = new Set(), R = plan.rooms;
  for (let i = 0; i < R.length; i++) for (let j = i + 1; j < R.length; j++) {
    const a = R[i], b = R[j];
    if (a.room_type === 'stairwell' || b.room_type === 'stairwell') continue;
    const sh = sharedEdge(a, b);
    if (!sh) continue;
    const key = [a.name, b.name].sort().join('|');
    if (placed.has(key)) continue;
    placed.add(key);
    a.openings.push(opening('door', [(sh[0][0] + sh[1][0]) / 2, (sh[0][1] + sh[1][1]) / 2], 0.9, 2.1));
  }
  if (plan.floor_index !== 0) return;
  const fb = plan.footprint;
  let ent = null;
  for (const n of ['entrance_hall', 'hallway', 'entrance_passage', 'hall', 'foyer', 'entrance']) { ent = roomByName(plan, n); if (ent) break; }
  if (ent) ent.openings.push(opening('front_door', [(ent.b[0] + ent.b[2]) / 2, fb[1]], 1.1, 2.4));
  for (const n of ['kitchen', 'scullery', 'back_room', 'morning_room']) {
    const rear = roomByName(plan, n);
    if (rear) { rear.openings.push(opening('front_door', [(rear.b[0] + rear.b[2]) / 2, fb[3]], 0.9, 2.1)); break; }
  }
}

function placeWindows(plan) {
  const fb = plan.footprint;
  const onBoundary = (a, b) => [a, b, [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]].every(p => boundaryDist(fb, p) < 0.01);
  for (const r of plan.rooms) {
    if (NO_WINDOW.has(r.room_type)) continue;
    const c = boxRing(r.b);
    for (let i = 0; i < c.length - 1; i++) {
      const len = segLength(c[i], c[i + 1]);
      if (len < 1.0 || !onBoundary(c[i], c[i + 1])) continue;
      const n = Math.max(1, pyInt(len / 2.0));
      for (let k = 0; k < n; k++) r.openings.push(opening('window', interpolate(c[i], c[i + 1], (k + 0.5) / n), 1.0, 1.4, 0.9));
    }
  }
}
