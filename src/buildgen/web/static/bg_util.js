// Numeric and 2D helpers that reproduce what buildgen's Python gets from round(), shapely and GEOS, so the JS
// port takes the same branches: Python round() (half-even, exact decimal), shapely.box ring order, GEOS ring area,
// point/segment distances and LineString.interpolate.

// Python round(x, d) for d >= 1: correctly rounded to d decimals, exact ties go to the even digit.
export function pyRound(x, d) {
  if (!Number.isFinite(x)) return x;
  const exact = Math.abs(x).toFixed(100); // exact decimal expansion of the double (enough digits for our range)
  const dot = exact.indexOf('.');
  const tail = exact.slice(dot + 1 + d);
  if (tail[0] === '5' && /^50*$/.test(tail)) { // exact tie
    const kept = exact.slice(0, dot + 1 + d);
    const last = +kept[kept.length - 1];
    const down = Number(kept);
    const v = last % 2 === 0 ? down : Number((down + Math.pow(10, -d)).toFixed(d));
    return x < 0 ? -v : v;
  }
  return Number(x.toFixed(d));
}

// Python round(x) to an integer (half to even).
export function pyRoundInt(x) {
  const f = Math.floor(x), diff = x - f;
  if (diff < 0.5) return f;
  if (diff > 0.5) return f + 1;
  return f % 2 === 0 ? f : f + 1;
}

export const pyInt = x => Math.trunc(x);

// shapely.geometry.box(minx, miny, maxx, maxy) exterior ring (ccw, closed).
export const boxRing = b => [[b[2], b[1]], [b[2], b[3]], [b[0], b[3]], [b[0], b[1]], [b[2], b[1]]];
export const rectArea = b => (b[2] - b[0]) * (b[3] - b[1]); // GEOS ring area of a box, bit for bit

export const segLength = (a, b) => { const dx = b[0] - a[0], dy = b[1] - a[1]; return Math.sqrt(dx * dx + dy * dy); };

// GEOS Distance::pointToSegment
export function pointSegDist(p, a, b) {
  if (a[0] === b[0] && a[1] === b[1]) return segLength(p, a);
  const len2 = (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]);
  const r = ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / len2;
  if (r <= 0) return segLength(p, a);
  if (r >= 1) return segLength(p, b);
  const s = ((a[1] - p[1]) * (b[0] - a[0]) - (a[0] - p[0]) * (b[1] - a[1])) / len2;
  return Math.abs(s) * Math.sqrt(len2);
}

const orient = (a, b, c) => Math.sign((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]));
const onSeg = (a, b, p) => Math.min(a[0], b[0]) <= p[0] && p[0] <= Math.max(a[0], b[0])
  && Math.min(a[1], b[1]) <= p[1] && p[1] <= Math.max(a[1], b[1]);
function segsIntersect(a, b, c, d) {
  const o1 = orient(a, b, c), o2 = orient(a, b, d), o3 = orient(c, d, a), o4 = orient(c, d, b);
  if (o1 !== o2 && o3 !== o4) return true;
  return (o1 === 0 && onSeg(a, b, c)) || (o2 === 0 && onSeg(a, b, d)) || (o3 === 0 && onSeg(c, d, a)) || (o4 === 0 && onSeg(c, d, b));
}

// GEOS Distance::segmentToSegment
export function segSegDist(a, b, c, d) {
  if (segsIntersect(a, b, c, d)) return 0;
  return Math.min(pointSegDist(a, c, d), pointSegDist(b, c, d), pointSegDist(c, a, b), pointSegDist(d, a, b));
}

// Distance from a segment (or a point when b is omitted) to the boundary of the box bounds fb.
export function boundaryDist(fb, a, b = null) {
  const r = boxRing(fb);
  let m = Infinity;
  for (let i = 0; i < 4; i++) m = Math.min(m, b ? segSegDist(a, b, r[i], r[i + 1]) : pointSegDist(a, r[i], r[i + 1]));
  return m;
}

// LineString([a, b]).interpolate(t, normalized=True) as GEOS computes it.
export function interpolate(a, b, t) {
  const len = segLength(a, b);
  const frac = len > 0 ? (t * len) / len : 0;
  return [a[0] + frac * (b[0] - a[0]), a[1] + frac * (b[1] - a[1])];
}

// Area of buffer(r) of segment a intersected with buffer(r) of segment b, for axis-aligned parallel segments
// (all buildgen rooms are boxes). Two half-disc caps plus the overlapping strip; other cases are tiny.
export function bufferedOverlapArea(a0, a1, b0, b1, r) {
  const horiz = a0[1] === a1[1] && b0[1] === b1[1], vert = a0[0] === a1[0] && b0[0] === b1[0];
  if (!horiz && !vert) return 0;
  const k = horiz ? 0 : 1, o = 1 - k;
  const off = Math.abs(a0[o] - b0[o]);
  if (off >= 2 * r) return 0;
  const lo = Math.max(Math.min(a0[k], a1[k]), Math.min(b0[k], b1[k]));
  const hi = Math.min(Math.max(a0[k], a1[k]), Math.max(b0[k], b1[k]));
  if (hi <= lo) return 0;
  return (2 * r - off) * (hi - lo) + (off === 0 ? Math.PI * r * r : 0);
}

// Python 3.12+ sum() of floats: Neumaier compensated summation (CPython bltinmodule.c), not a plain loop.
export function pySum(xs) {
  let s = 0.0, c = 0.0;
  for (const x of xs) {
    const t = s + x;
    if (Math.abs(s) >= Math.abs(x)) c += (s - t) + x; else c += (x - t) + s;
    s = t;
  }
  return c !== 0 && Number.isFinite(c) ? s + c : s;
}
