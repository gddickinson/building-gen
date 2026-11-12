// Port of buildgen/geometry/stairs.py: straight, L-shaped, U-shaped (dog-leg) and spiral stairs inside a
// stairwell box b = [minx, minz, maxx, maxz] (plan y becomes 3D z; y is up).
import { pyRoundInt } from './bg_util.js';
import { concat, darken, fixNormals, makeBox, mesh } from './bg_mesh.js';

export function buildStairMesh(b, floorY, floorHeight, style, type = 'auto') {
  const sw = b[2] - b[0], sd = b[3] - b[1];
  if (sw < 0.5 || sd < 0.5) return null;
  if (type === 'auto') {
    const aspect = Math.min(sw, sd) > 0 ? Math.max(sw, sd) / Math.min(sw, sd) : 1, area = sw * sd;
    if (Math.min(sw, sd) < 1.2) type = aspect < 1.3 ? 'spiral' : 'straight';
    else if (aspect > 2.0) type = 'straight';
    else if (area > 5.0) type = 'u_shape';
    else type = 'l_shape';
  }
  let rise = floorHeight - style.slab_thickness;
  if (rise <= 0) rise = floorHeight;
  const y0 = floorY + style.slab_thickness;
  const f = { spiral: spiral, u_shape: uStair, l_shape: lStair }[type] || straight;
  return f(b, y0, rise, style);
}

function straight(b, startY, rise, style) {
  const sw = b[2] - b[0], sd = b[3] - b[1];
  const n = Math.max(3, pyRoundInt(rise / style.stair_riser)), rh = rise / n;
  const alongZ = sd >= sw;
  const width = alongZ ? Math.min(sw * 0.85, sw - 0.1) : Math.min(sd * 0.85, sd - 0.1);
  const run = alongZ ? sd - 0.2 : sw - 0.2;
  const td = run / n, cx = (b[0] + b[2]) / 2, cz = (b[1] + b[3]) / 2;
  const c = style.stair_color, dark = darken(c, 25);
  const out = [];
  for (let i = 0; i < n; i++) {
    const base = startY + i * rh, top = startY + (i + 1) * rh;
    let x0, x1, z0, z1;
    if (alongZ) { z0 = b[1] + 0.1 + i * td; z1 = z0 + td; x0 = cx - width / 2; x1 = cx + width / 2; }
    else { x0 = b[0] + 0.1 + i * td; x1 = x0 + td; z0 = cz - width / 2; z1 = cz + width / 2; }
    out.push(makeBox(x0, top - 0.04, z0, x1, top, z1, c));
    out.push(alongZ ? makeBox(x0, base, z0, x1, top - 0.04, z0 + 0.02, dark) : makeBox(x0, base, z0, x0 + 0.02, top - 0.04, z1, dark));
  }
  // stringer segments
  const sc = darken(c, 30), segs = Math.max(2, Math.floor(n / 4));
  for (let s = 0; s < segs; s++) {
    const t0 = s / segs, t1 = (s + 1) / segs, ya = startY + rise * t0 - 0.06, yb = startY + rise * t0;
    if (alongZ) out.push(makeBox(cx - width / 2, ya, b[1] + 0.1 + (b[3] - b[1] - 0.2) * t0, cx + width / 2, yb, b[1] + 0.1 + (b[3] - b[1] - 0.2) * t1, sc));
    else out.push(makeBox(b[0] + 0.1 + (b[2] - b[0] - 0.2) * t0, ya, cz - width / 2, b[0] + 0.1 + (b[2] - b[0] - 0.2) * t1, yb, cz + width / 2, sc));
  }
  return concat(out);
}

function lStair(b, startY, rise, style) {
  const sw = b[2] - b[0], sd = b[3] - b[1], c = style.stair_color;
  const n = Math.max(6, pyRoundInt(rise / style.stair_riser)), rh = rise / n;
  const s1 = Math.floor(n * 3 / 5), s2 = n - s1;
  const w = Math.min(sw, sd) * 0.4, land = w;
  const out = [];
  for (let i = 0; i < s1; i++) {
    const top = startY + (i + 1) * rh, td = (sd - land) / s1;
    const x0 = b[0] + 0.05, z0 = b[1] + 0.05 + i * td;
    out.push(makeBox(x0, top - 0.04, z0, x0 + w, top, z0 + td, c));
  }
  const ly = startY + s1 * rh, lx0 = b[0] + 0.05, lx1 = lx0 + land, lz0 = b[3] - land - 0.05, lz1 = b[3] - 0.05;
  out.push(makeBox(lx0, ly - 0.06, lz0, lx1, ly, lz1, c));
  for (let i = 0; i < s2; i++) {
    const top = ly + (i + 1) * rh, td = (sw - land - 0.1) / s2, x0 = lx1 + i * td;
    out.push(makeBox(x0, top - 0.04, lz0, x0 + td, top, lz1, c));
  }
  return concat(out);
}

function uStair(b, startY, rise, style) {
  const sw = b[2] - b[0], sd = b[3] - b[1], c = style.stair_color;
  const n = Math.max(6, pyRoundInt(rise / style.stair_riser)), rh = rise / n;
  const s1 = Math.floor(n / 2), s2 = n - s1;
  const fw = (sw - 0.15) / 2, landD = 1.0, run = sd - landD - 0.1, td = run / s1;
  const out = [];
  for (let i = 0; i < s1; i++) {
    const top = startY + (i + 1) * rh, x0 = b[0] + 0.05, z0 = b[1] + 0.05 + i * td;
    out.push(makeBox(x0, top - 0.04, z0, x0 + fw, top, z0 + td, c));
  }
  const ly = startY + s1 * rh;
  out.push(makeBox(b[0] + 0.05, ly - 0.06, b[3] - landD - 0.05, b[2] - 0.05, ly, b[3] - 0.05, c));
  const td2 = run / s2;
  for (let i = 0; i < s2; i++) {
    const top = ly + (i + 1) * rh, z1 = b[3] - landD - 0.05 - i * td2;
    out.push(makeBox(b[2] - 0.05 - fw, top - 0.04, z1 - td2, b[2] - 0.05, top, z1, c));
  }
  return concat(out);
}

function spiral(b, startY, rise, style) {
  const sw = b[2] - b[0], sd = b[3] - b[1], cx = (b[0] + b[2]) / 2, cz = (b[1] + b[3]) / 2;
  const radius = Math.min(sw, sd) / 2 - 0.05, inner = 0.12;
  if (radius < 0.3) return null;
  const n = Math.max(8, pyRoundInt(rise / style.stair_riser)), rh = rise / n;
  const per = (2 * Math.PI * 1.1) / n;
  const pv = [], pf = [];
  for (let i = 0; i < 8; i++) {
    const a = 2 * Math.PI * i / 8, px = cx + inner * Math.cos(a), pz = cz + inner * Math.sin(a);
    pv.push([px, startY, pz], [px, startY + rise, pz]);
  }
  for (let i = 0; i < 8; i++) { const j = (i + 1) % 8; pf.push([i * 2, j * 2, j * 2 + 1], [i * 2, j * 2 + 1, i * 2 + 1]); }
  const out = [mesh(pv, pf, darken(style.stair_color, 40))];
  for (let i = 0; i < n; i++) {
    const a0 = i * per, a1 = (i + 0.9) * per, top = startY + (i + 1) * rh;
    const pts = [];
    for (let k = 0; k <= 4; k++) { const a = a0 + (k / 4) * (a1 - a0); pts.push([cx + inner * Math.cos(a), cz + inner * Math.sin(a)]); }
    for (let k = 4; k >= 0; k--) { const a = a0 + (k / 4) * (a1 - a0); pts.push([cx + radius * Math.cos(a), cz + radius * Math.sin(a)]); }
    const np = pts.length, v = [...pts.map(p => [p[0], top - 0.04, p[1]]), ...pts.map(p => [p[0], top, p[1]])], f = [];
    for (let j = 1; j < np - 1; j++) f.push([0, j, j + 1], [np, np + j + 1, np + j]);
    for (let j = 0; j < np; j++) { const k = (j + 1) % np; f.push([j, k, np + k], [j, np + k, np + j]); }
    out.push(fixNormals(mesh(v, f, style.stair_color)));
  }
  return concat(out);
}
