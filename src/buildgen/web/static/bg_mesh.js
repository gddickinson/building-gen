// Triangle meshes as trimesh holds them: vertices [[x, y, z]], faces [[a, b, c]], one RGBA colour per face.
// fixNormals reproduces trimesh's fix_normals (consistent winding by flipping faces, then invert a closed mesh with
// negative volume); for the closed meshes buildgen builds the result is unique, so it matches trimesh exactly.
export const mesh = (vertices, faces, color) => ({ vertices, faces, colors: faces.map(() => color.slice()) });

const ekey = (a, b) => a + ',' + b;

function edgeMap(faces) {
  const m = new Map();
  faces.forEach((f, fi) => { for (let k = 0; k < 3; k++) { const a = f[k], b = f[(k + 1) % 3]; const key = a < b ? ekey(a, b) : ekey(b, a); (m.get(key) || m.set(key, []).get(key)).push([fi, a, b]); } });
  return m;
}

export function isWatertight(faces) {
  for (const v of edgeMap(faces).values()) if (v.length !== 2) return false;
  return true;
}

function windingConsistent(faces) {
  for (const v of edgeMap(faces).values()) if (v.length === 2 && v[0][1] === v[1][1]) return false;
  return true;
}

export function signedVolume(m) {
  let s = 0;
  for (const [a, b, c] of m.faces) {
    const p = m.vertices[a], q = m.vertices[b], r = m.vertices[c];
    s += p[0] * (q[1] * r[2] - q[2] * r[1]) - p[1] * (q[0] * r[2] - q[2] * r[0]) + p[2] * (q[0] * r[1] - q[1] * r[0]);
  }
  return s / 6;
}

export function fixNormals(m) {
  if (!windingConsistent(m.faces)) {
    const faces = m.faces.map(f => f.slice());
    const adj = faces.map(() => []);
    for (const v of edgeMap(faces).values()) if (v.length === 2) { adj[v[0][0]].push(v[1][0]); adj[v[1][0]].push(v[0][0]); }
    const seen = new Uint8Array(faces.length);
    for (let s = 0; s < faces.length; s++) {
      if (seen[s]) continue;
      seen[s] = 1;
      const queue = [s];
      while (queue.length) {
        const f = queue.shift();
        for (const n of adj[f]) {
          if (seen[n]) continue;
          seen[n] = 1;
          // shared edge must run in opposite directions in the two faces
          const fa = faces[f], fb = faces[n];
          let same = false;
          for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++)
            if (fa[i] === fb[j] && fa[(i + 1) % 3] === fb[(j + 1) % 3]) same = true;
          if (same) faces[n] = fb.slice().reverse();
          queue.push(n);
        }
      }
    }
    m.faces = faces;
  }
  if (isWatertight(m.faces) && signedVolume(m) < 0) m.faces = m.faces.map(f => f.slice().reverse());
  return m;
}

export function concat(meshes) {
  const out = { vertices: [], faces: [], colors: [] };
  for (const m of meshes) {
    const off = out.vertices.length;
    out.vertices.push(...m.vertices);
    for (const f of m.faces) out.faces.push([f[0] + off, f[1] + off, f[2] + off]);
    out.colors.push(...m.colors);
  }
  return out;
}

// buildgen/geometry/stairs.py _make_box: axis-aligned box, no normal fixing.
const BOX_FACES = [[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6], [0, 4, 7], [0, 7, 3], [1, 2, 6], [1, 6, 5]];
export function makeBox(x0, y0, z0, x1, y1, z1, color) {
  if (x1 <= x0 || y1 <= y0 || z1 <= z0) { x1 = Math.max(x1, x0 + 0.01); y1 = Math.max(y1, y0 + 0.01); z1 = Math.max(z1, z0 + 0.01); }
  const v = [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]];
  return mesh(v, BOX_FACES.map(f => f.slice()), color);
}

export const darken = (c, amount = 20) => [...c.slice(0, 3).map(x => Math.max(0, x - amount)), c.length > 3 ? c[3] : 255];
