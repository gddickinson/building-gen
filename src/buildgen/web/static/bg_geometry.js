// Stage 3: port of buildgen/geometry (walls.py, slabs.py, roofs.py and GeometryBuilder.build in builder.py).
// Output is a list of scene nodes {name, mesh} in the order trimesh's Scene receives them, plus the stats Building3D has.
import { boxRing, pySum, rectArea, roomArea } from './bg_util.js';
import { concat, fixNormals, makeBox, mesh } from './bg_mesh.js';
import { buildStairMesh } from './bg_stairs.js';

const WALL_FACES = [[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 4, 7], [0, 7, 3], [1, 6, 5], [1, 2, 6], [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6]];
const SLAB_COLOR = [200, 200, 200, 255];

export function buildWallMesh(wall, floorY, height, style) {
  const [sx, sy] = wall.start, [ex, ey] = wall.end, dx = ex - sx, dy = ey - sy;
  const length = Math.sqrt(dx * dx + dy * dy);
  if (length < 0.01) return null;
  const t = wall.thickness / 2.0, nx = -dy / length * t, ny = dx / length * t;
  const corners = [[sx + nx, sy + ny], [sx - nx, sy - ny], [ex - nx, ey - ny], [ex + nx, ey + ny]];
  const v = [...corners.map(([x, z]) => [x, floorY, z]), ...corners.map(([x, z]) => [x, floorY + height, z])];
  const color = wall.wall_type === 'exterior' ? style.exterior_wall_color : style.interior_wall_color;
  return fixNormals(mesh(v, WALL_FACES.map(f => f.slice()), color));
}

// walls.opening_span: [along_start, along_end, y_bottom, y_top] where the opening cuts this wall, or null.
export function openingSpan(wall, o, floorY, height) {
  const [ox, oy] = o.position, [sx, sy] = wall.start, [ex, ey] = wall.end, dx = ex - sx, dy = ey - sy;
  const length = Math.sqrt(dx * dx + dy * dy);
  if (length < 0.01) return null;
  const t = ((ox - sx) * dx + (oy - sy) * dy) / (length * length);
  const px = sx + t * dx, py = sy + t * dy;
  const dist = Math.sqrt((ox - px) ** 2 + (oy - py) ** 2);
  if (dist > wall.thickness * 2 || t < -0.1 || t > 1.1) return null;
  let yb, yt;
  if (o.type === 'window') { yb = floorY + o.sill_height; yt = floorY + o.sill_height + o.height; }
  else { yb = floorY; yt = floorY + o.height; }
  const c = t * length, a = Math.max(0.0, c - o.width / 2.0), b = Math.min(length, c + o.width / 2.0);
  yb = Math.max(floorY, yb); yt = Math.min(floorY + height, yt);
  if (b - a < 1e-6 || yt - yb < 1e-6) return null;
  return [a, b, yb, yt];
}

function subtractRanges(solid, cut) {
  const out = [];
  for (const [lo, hi] of solid) {
    if (cut[1] <= lo || cut[0] >= hi) { out.push([lo, hi]); continue; }
    if (cut[0] > lo) out.push([lo, cut[0]]);
    if (cut[1] < hi) out.push([cut[1], hi]);
  }
  return out.filter(r => r[1] - r[0] > 1e-6);
}
const sameRanges = (a, b) => a.length === b.length && a.every((r, i) => r[0] === b[i][0] && r[1] === b[i][1]);

export function buildWallWithOpenings(wall, spans, floorY, height, style) {
  if (!spans.length) return buildWallMesh(wall, floorY, height, style);
  const [sx, sy] = wall.start, [ex, ey] = wall.end, dx = ex - sx, dy = ey - sy;
  const length = Math.sqrt(dx * dx + dy * dy), y0 = floorY, y1 = floorY + height;
  const cuts = [...new Set([0.0, length, ...spans.map(s => s[0]), ...spans.map(s => s[1])])].sort((a, b) => a - b);
  const pieces = [];
  for (let i = 0; i < cuts.length - 1; i++) {
    const u = cuts[i], v = cuts[i + 1];
    if (v - u < 1e-6) continue;
    const mid = (u + v) / 2.0;
    let solid = [[y0, y1]];
    for (const [a, b, yb, yt] of spans) if (a < mid && mid < b) solid = subtractRanges(solid, [yb, yt]);
    if (pieces.length && sameRanges(pieces[pieces.length - 1][2], solid)) pieces[pieces.length - 1][1] = v;
    else pieces.push([u, v, solid]);
  }
  const meshes = [];
  let volume = 0.0;
  for (const [u, v, solid] of pieces) {
    const part = { start: [sx + dx / length * u, sy + dy / length * u], end: [sx + dx / length * v, sy + dy / length * v], wall_type: wall.wall_type, thickness: wall.thickness };
    for (const [lo, hi] of solid) {
      const m = buildWallMesh(part, lo, hi - lo, style);
      if (m) { meshes.push(m); volume += (v - u) * wall.thickness * (hi - lo); }
    }
  }
  if (!meshes.length || volume <= 0.01) return buildWallMesh(wall, floorY, height, style);
  return concat(meshes);
}

// GeometryBuilder._build_slab for a box footprint: fan triangulation of the ring, then trimesh fix_normals.
export function buildSlab(fb, y, th) {
  const c = boxRing(fb).slice(0, -1), n = c.length;
  const v = [...c.map(p => [p[0], y, p[1]]), ...c.map(p => [p[0], y + th, p[1]])], f = [];
  for (let i = 1; i < n - 1; i++) f.push([0, i, i + 1], [n, n + i + 1, n + i]);
  for (let i = 0; i < n; i++) { const j = (i + 1) % n; f.push([i, j, n + j], [i, n + j, n + i]); }
  return fixNormals(mesh(v, f, SLAB_COLOR));
}

// slabs.solid_rects / stairwell_holes / build_slab_with_holes
export function solidRects(b, holes) {
  const clampX = v => Math.min(Math.max(v, b[0]), b[2]), clampY = v => Math.min(Math.max(v, b[1]), b[3]);
  const xs = [...new Set([b[0], b[2], ...holes.flatMap(h => [clampX(h[0]), clampX(h[2])])])].sort((p, q) => p - q);
  const ys = [...new Set([b[1], b[3], ...holes.flatMap(h => [clampY(h[1]), clampY(h[3])])])].sort((p, q) => p - q);
  const rects = [];
  for (let j = 0; j < ys.length - 1; j++) {
    const y0 = ys[j], y1 = ys[j + 1];
    if (y1 - y0 <= 1e-9) continue;
    const cy = (y0 + y1) / 2;
    let run = null;
    for (let i = 0; i < xs.length - 1; i++) {
      const x0 = xs[i], x1 = xs[i + 1];
      if (x1 - x0 <= 1e-9) continue;
      const cx = (x0 + x1) / 2;
      const solid = !holes.some(h => h[0] < cx && cx < h[2] && h[1] < cy && cy < h[3]);
      if (solid) run = run ? [run[0], x1] : [x0, x1];
      else if (run) { rects.push([run[0], y0, run[1], y1]); run = null; }
    }
    if (run) rects.push([run[0], y0, run[1], y1]);
  }
  return rects;
}

export function stairwellHoles(b, stairs, margin = 0.05) {
  const holes = [];
  for (const s of stairs) {
    const h = [s[0] + margin, s[1] + margin, s[2] - margin, s[3] - margin];
    if (h[2] <= h[0] || h[3] <= h[1]) continue;
    if (pySum(solidRects(b, [...holes, h]).map(rectArea)) > 1.0) holes.push(h);
  }
  return holes;
}

function slabWithOpenings(fb, y, th, stairRooms) {
  const holes = stairwellHoles(fb, stairRooms.map(r => r.b));
  if (!holes.length) return buildSlab(fb, y, th);
  return concat(solidRects(fb, holes).map(r => makeBox(r[0], y, r[1], r[2], y + th, r[3], SLAB_COLOR)));
}

// roofs.py (after the ridge/normal fixes): face lists as in Python, reversed to face outward, then fix_normals.
export function buildRoofMesh(fb, baseY, style) {
  const [minx, miny, maxx, maxy] = fb, w = maxx - minx, d = maxy - miny, o = style.roof_overhang;
  const rh = style.roof_pitch * Math.min(w, d) / 2.0, ry = baseY + rh;
  const eaves = [[minx - o, baseY, miny - o], [maxx + o, baseY, miny - o], [maxx + o, baseY, maxy + o], [minx - o, baseY, maxy + o]];
  let v, f;
  if (style.roof_type === 'gable') {
    if (d >= w) { const mx = (minx + maxx) / 2.0; v = [...eaves, [mx, ry, miny - o], [mx, ry, maxy + o]]; f = [[0, 4, 5], [0, 5, 3], [1, 2, 5], [1, 5, 4], [0, 1, 4], [2, 3, 5]]; }
    else { const mz = (miny + maxy) / 2.0; v = [...eaves, [minx - o, ry, mz], [maxx + o, ry, mz]]; f = [[0, 5, 4], [0, 1, 5], [3, 5, 2], [3, 4, 5], [0, 4, 3], [1, 2, 5]]; }
  } else if (style.roof_type === 'hip') {
    const inset = Math.min(w, d) / 2.0;
    if (d >= w) { const mx = (minx + maxx) / 2.0; v = [...eaves, [mx, ry, miny + inset], [mx, ry, maxy - inset]]; f = [[0, 1, 4], [1, 2, 5], [1, 5, 4], [2, 3, 5], [3, 0, 4], [3, 4, 5]]; }
    else { const mz = (miny + maxy) / 2.0; v = [...eaves, [minx + inset, ry, mz], [maxx - inset, ry, mz]]; f = [[3, 0, 4], [0, 1, 5], [0, 5, 4], [1, 2, 5], [2, 3, 4], [2, 4, 5]]; }
  } else {
    const c = boxRing(fb).slice(0, -1), n = c.length, ph = 0.3;
    v = [...c.map(p => [p[0], baseY, p[1]]), ...c.map(p => [p[0], baseY + ph, p[1]])];
    f = [];
    for (let i = 1; i < n - 1; i++) f.push([n, n + i, n + i + 1]);
    for (let i = 0; i < n; i++) { const j = (i + 1) % n; f.push([i, j, n + j], [i, n + j, n + i]); }
  }
  return fixNormals(mesh(v, f.map(x => x.slice().reverse()), style.roof_color));
}

export function buildGeometry(plans, style) {
  const nodes = [];
  let total = 0.0;
  for (const plan of plans) {
    const fy = plan.floor_index * style.floor_height;
    total += pySum(plan.rooms.map(roomArea));
    nodes.push({ name: `floor_${plan.floor_index}_slab`, mesh: slabWithOpenings(plan.footprint, fy, style.slab_thickness, plan.rooms.filter(r => r.room_type === 'stairwell')) });
    const openings = plan.rooms.flatMap(r => r.openings);
    plan.walls.forEach((w, wi) => {
      const spans = openings.map(o => openingSpan(w, o, fy, style.floor_height)).filter(Boolean);
      const m = buildWallWithOpenings(w, spans, fy, style.floor_height, style);
      if (m) nodes.push({ name: `floor_${plan.floor_index}_wall_${wi}`, mesh: m });
    });
    for (const r of plan.rooms) {
      if (r.room_type !== 'stairwell') continue;
      const m = buildStairMesh(r.b, fy, style.floor_height, style);
      if (m) nodes.push({ name: `floor_${plan.floor_index}_stairs`, mesh: m });
    }
  }
  if (plans.length) {
    const top = plans[plans.length - 1], ty = (top.floor_index + 1) * style.floor_height;
    nodes.push({ name: 'ceiling_slab', mesh: buildSlab(top.footprint, ty, style.slab_thickness) });
    nodes.push({ name: 'roof', mesh: buildRoofMesh(top.footprint, ty, style) });
  }
  return { nodes, num_floors: plans.length, footprint_area: plans.length ? rectArea(plans[0].footprint) : 0.0, total_floor_area: total };
}
