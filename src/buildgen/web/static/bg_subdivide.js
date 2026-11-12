// Port of buildgen/layout/subdivide.py: the Georgian-style split of a footprint into a central hall column and
// left/right wings, rooms stacked front to back, small rooms carved from corners of the largest rooms.
import { rectArea, pySum } from './bg_util.js';

const FRONT = new Set(['entrance_hall', 'parlour', 'drawing_room', 'shop_floor']);
const REAR = new Set(['kitchen', 'scullery', 'pantry']);
const SMALL = new Set(['landing', 'wc', 'stairwell', 'dressing_room', 'pantry', 'storage']);
const CIRC = new Set(['entrance_hall', 'hallway', 'landing']);

export const room = (name, type, b, floor) => ({ name, room_type: type, b, floor, openings: [], fixtures: [] });

export function subdivideFloor(fb, rooms, stair, rng) {
  if (!rooms.length) return [];
  const [minx, miny, maxx, maxy] = fb, fw = maxx - minx, fd = maxy - miny;
  const circulation = rooms.filter(r => CIRC.has(r.room_type));
  const small = rooms.filter(r => SMALL.has(r.room_type) && !CIRC.has(r.room_type) && !r.is_stairwell);
  const front = rooms.filter(r => FRONT.has(r.room_type) && !CIRC.has(r.room_type));
  const rear = rooms.filter(r => REAR.has(r.room_type));
  const main = rooms.filter(r => !circulation.includes(r) && !small.includes(r) && !front.includes(r) && !rear.includes(r) && !r.is_stairwell);
  let result = [];

  const hallWidth = 1.2 + rng.uniform(-0.1, 0.1);
  let hx1, hx2;
  if (stair) {
    const cx = (stair[0] + stair[2]) / 2;
    hx1 = Math.min(cx - hallWidth / 2, stair[0]);
    hx2 = Math.max(cx + hallWidth / 2, stair[2]);
  } else {
    hx1 = minx + (fw - hallWidth) / 2;
    hx2 = hx1 + hallWidth;
  }
  const minWing = 2.5;
  hx1 = Math.max(minx + minWing, hx1);
  hx2 = Math.min(maxx - minWing, hx2);
  if (hx2 - hx1 < 1.0) { hx1 = minx + fw * 0.4; hx2 = hx1 + 1.2; }

  if (circulation.length) {
    const c = circulation[0];
    let depth;
    if (stair) {
      depth = Math.min(stair[3] + 0.5, maxy) - miny;
      const maxDepth = (hx2 - hx1) > 0 ? (c.max_area * 1.3) / (hx2 - hx1) : fd;
      depth = Math.max(2.0, Math.min(depth, maxDepth));
    } else {
      depth = Math.max(2.0, Math.min(fd * 0.4, c.max_area / (hx2 - hx1)));
    }
    result.push(room(c.name, c.room_type, [hx1, miny, hx2, miny + depth], c.floor));
    if (circulation.length > 1) small.push(...circulation.slice(1));
  }

  const leftW = hx1 - minx, rightW = maxx - hx2;
  const left = [], right = [];
  let la = 0, ra = 0;
  for (const r of [...front, ...main, ...rear]) {
    if (la <= ra) { left.push(r); la += r.target_area; } else { right.push(r); ra += r.target_area; }
  }
  if (left.length && leftW > 1.5) result.push(...subdivideColumn(minx, miny, hx1, maxy, left, rng));
  if (right.length && rightW > 1.5) result.push(...subdivideColumn(hx2, miny, maxx, maxy, right, rng));
  for (const s of small) result = carveSmallRoom(result, s, rng);
  return result;
}

function subdivideColumn(minx, miny, maxx, maxy, rooms, rng) {
  if (!rooms.length) return [];
  const colW = maxx - minx, colH = maxy - miny;
  if (rooms.length === 1) {
    const r = rooms[0];
    let h = colH, maxDepth = colW * 2.5;
    if (r.max_area > 0) maxDepth = Math.min(maxDepth, colW > 0 ? (r.max_area * 1.3) / colW : h);
    h = Math.max(2.0, Math.min(h, maxDepth));
    return [room(r.name, r.room_type, [minx, miny, maxx, miny + h], r.floor)];
  }
  const key = r => (FRONT.has(r.room_type) ? 0 : REAR.has(r.room_type) ? 2 : 1);
  const sorted = [...rooms].sort((a, b) => key(a) - key(b));
  let heights = sorted.map(r => {
    const target = colW > 0 ? r.target_area / colW : 3.0;
    const maxH = colW > 0 ? (r.max_area * 1.2) / colW : target * 1.5;
    const minH = colW > 0 ? Math.max(2.0, r.min_area / colW) : 2.0;
    return Math.max(minH, Math.min(target, maxH));
  });
  const total = pySum(heights);
  if (total > 0) { const scale = colH / total; heights = heights.map(h => h * scale); }
  for (let it = 0; it < 5; it++) {
    let surplus = 0.0;
    const growable = [];
    sorted.forEach((r, i) => {
      const h = heights[i], area = h * colW;
      let maxA = r.max_area * 1.3;
      if (SMALL.has(r.room_type)) maxA = r.max_area * 1.1;
      if (area > maxA && sorted.length > 1) { const ch = maxA / colW; surplus += h - ch; heights[i] = ch; }
      else growable.push(i);
    });
    if (surplus > 0.1 && growable.length) { const share = surplus / growable.length; for (const i of growable) heights[i] += share; }
    else break;
  }
  const out = [];
  let y = miny;
  sorted.forEach((r, i) => {
    let h = heights[i];
    if (i === sorted.length - 1) h = maxy - y;
    if (h < 0.5) return;
    h += rng.uniform(-0.15, 0.15);
    h = Math.max(1.5, h);
    if (y + h > maxy) h = maxy - y;
    out.push(room(r.name, r.room_type, [minx, y, maxx, y + h], r.floor));
    y += h;
  });
  return out;
}

// host.polygon.difference(small box): area and bounds of what is left (both are axis-aligned boxes).
function remainder(h, s) {
  const ox0 = Math.max(h[0], s[0]), oy0 = Math.max(h[1], s[1]), ox1 = Math.min(h[2], s[2]), oy1 = Math.min(h[3], s[3]);
  if (ox1 <= ox0 || oy1 <= oy0) return { area: rectArea(h), b: h };
  const area = rectArea(h) - (ox1 - ox0) * (oy1 - oy0);
  const fullX = ox0 <= h[0] && ox1 >= h[2], fullY = oy0 <= h[1] && oy1 >= h[3];
  if (fullX && fullY) return { area: 0, b: null };
  let b = h;
  if (fullX) b = oy0 <= h[1] ? [h[0], oy1, h[2], h[3]] : oy1 >= h[3] ? [h[0], h[1], h[2], oy0] : h;
  else if (fullY) b = ox0 <= h[0] ? [ox1, h[1], h[2], h[3]] : ox1 >= h[2] ? [h[0], h[1], ox0, h[3]] : h;
  return { area, b };
}

function carveSmallRoom(existing, spec, rng) {
  if (!existing.length) return existing;
  let cands = existing.filter(r => rectArea(r.b) > spec.target_area * 2);
  if (!cands.length) cands = existing.filter(r => rectArea(r.b) > spec.min_area * 1.5);
  if (!cands.length) return existing;
  let host = cands[0];
  for (const c of cands) if (rectArea(c.b) > rectArea(host.b)) host = c;
  const hb = host.b, hw = hb[2] - hb[0], hh = hb[3] - hb[1];
  const target = spec.target_area;
  let sw = Math.min(hw * 0.35, Math.max(1.0, Math.sqrt(target)));
  let sh = sw > 0 ? target / sw : 1.5;
  sh = Math.min(sh, hh * 0.45);
  sw = Math.max(0.8, sw);
  sh = Math.max(0.8, sh);
  const corner = rng.choice(['tr', 'tl', 'br', 'bl']);
  let sb;
  if (corner === 'tr') sb = [hb[2] - sw, hb[3] - sh, hb[2], hb[3]];
  else if (corner === 'tl') sb = [hb[0], hb[3] - sh, hb[0] + sw, hb[3]];
  else if (corner === 'br') sb = [hb[2] - sw, hb[1], hb[2], hb[1] + sh];
  else sb = [hb[0], hb[1], hb[0] + sw, hb[1] + sh];
  const rem = remainder(hb, sb);
  if (!rem.b || rem.area < spec.min_area) return existing;
  const out = existing.filter(r => r !== host);
  out.push(room(host.name, host.room_type, rem.b, host.floor));
  out.push(room(spec.name, spec.room_type, sb, spec.floor));
  return out;
}
