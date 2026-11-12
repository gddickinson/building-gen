// GLB export written the way trimesh exports a Scene (trimesh/exchange/gltf export_glb): same JSON layout and key
// order, accessors and buffer views shared between identical arrays, vertex colours averaged from face colours,
// Python float formatting. The same building gives the same .glb bytes as `buildgen` (checked by the node tests).

// Python repr() of a float (shortest round-trip digits, Python's switch to exponent form).
export function pyFloat(x) {
  if (Object.is(x, -0)) return '-0.0';
  if (x === 0) return '0.0';
  const [mant, expS] = Math.abs(x).toExponential().split('e');
  const e = +expS, digits = mant.replace('.', ''), sign = x < 0 ? '-' : '';
  if (e >= -4 && e < 16) {
    let s;
    if (e >= 0) {
      const ip = digits.slice(0, e + 1).padEnd(e + 1, '0'), fp = digits.slice(e + 1);
      s = ip + '.' + (fp || '0');
    } else s = '0.' + '0'.repeat(-e - 1) + digits;
    return sign + s;
  }
  return sign + mant + 'e' + (e < 0 ? '-' : '+') + String(Math.abs(e)).padStart(2, '0');
}

function toJson(v) {
  if (v && v.__float !== undefined) return pyFloat(v.__float);
  if (Array.isArray(v)) return '[' + v.map(toJson).join(',') + ']';
  if (v && typeof v === 'object') return '{' + Object.entries(v).map(([k, x]) => JSON.stringify(k) + ':' + toJson(x)).join(',') + '}';
  return JSON.stringify(v);
}
const F = x => ({ __float: x });

const bytesOf = ta => new Uint8Array(ta.buffer, ta.byteOffset, ta.byteLength);
const keyOf = u8 => { let s = ''; for (let i = 0; i < u8.length; i += 4096) s += String.fromCharCode.apply(null, u8.subarray(i, i + 4096)); return s; };
const pad4 = u8 => { if (u8.length % 4 === 0) return u8; const o = new Uint8Array(u8.length + 4 - (u8.length % 4)); o.set(u8); return o; };

function vertexColors(m) {
  const n = m.vertices.length, sum = new Float64Array(n * 4), deg = new Float64Array(n);
  m.faces.forEach((f, fi) => { for (const v of f) { deg[v]++; for (let k = 0; k < 4; k++) sum[v * 4 + k] += m.colors[fi][k]; } });
  const out = new Uint8Array(n * 4);
  for (let v = 0; v < n; v++) for (let k = 0; k < 4; k++) out[v * 4 + k] = deg[v] > 0 ? Math.trunc(sum[v * 4 + k] / deg[v]) : sum[v * 4 + k];
  return out;
}

export function exportGlb(nodes) {
  const buffers = new Map(), bufList = [], accessors = new Map(), accList = [];
  function append(blob, ta, comps, isFloat) {
    const raw = bytesOf(ta), key = keyOf(raw);
    if (!buffers.has(key)) { buffers.set(key, bufList.length); bufList.push(pad4(raw)); }
    blob.bufferView = buffers.get(key);
    const akey = JSON.stringify(blob) + '|' + key;
    if (accessors.has(akey)) return accessors.get(akey);
    const count = ta.length / comps, mx = [], mn = [];
    for (let c = 0; c < comps; c++) {
      let hi = -Infinity, lo = Infinity;
      for (let i = c; i < ta.length; i += comps) { if (ta[i] > hi) hi = ta[i]; if (ta[i] < lo) lo = ta[i]; }
      mx.push(isFloat ? F(hi) : hi); mn.push(isFloat ? F(lo) : lo);
    }
    blob.count = comps === 1 ? ta.length : count;
    blob.max = mx; blob.min = mn;
    accessors.set(akey, accList.length); accList.push(blob);
    return accList.length - 1;
  }
  const meshes = [];
  nodes.forEach((node, i) => {
    const m = node.mesh;
    const idx = append({ componentType: 5125, type: 'SCALAR' }, Uint32Array.from(m.faces.flat()), 1, false);
    const pos = append({ componentType: 5126, type: 'VEC3', byteOffset: 0 }, Float32Array.from(m.vertices.flat()), 3, true);
    const col = append({ componentType: 5121, normalized: true, type: 'VEC4', byteOffset: 0 }, vertexColors(m), 4, false);
    meshes.push({ name: `geometry_${i}`, extras: { processed: true }, primitives: [{ attributes: { POSITION: pos, COLOR_0: col }, indices: idx, mode: 4 }] });
  });
  let off = 0;
  const views = bufList.map(b => { const v = { buffer: 0, byteOffset: off, byteLength: b.length }; off += b.length; return v; });
  const tree = {
    scene: 0, scenes: [{ nodes: nodes.map((_, i) => i) }],
    asset: { version: '2.0', generator: 'https://github.com/mikedh/trimesh' },
    accessors: accList, meshes, nodes: nodes.map((n, i) => ({ name: n.name, mesh: i })),
    buffers: [{ byteLength: off }], bufferViews: views,
  };
  let json = toJson(tree);
  json += ' '.repeat(4 - ((json.length + 20) % 4));
  const content = new TextEncoder().encode(json);
  const out = new Uint8Array(20 + content.length + 8 + off);
  const dv = new DataView(out.buffer);
  dv.setUint32(0, 0x46546c67, true); dv.setUint32(4, 2, true); dv.setUint32(8, content.length + off + 28, true);
  dv.setUint32(12, content.length, true); dv.setUint32(16, 0x4e4f534a, true);
  out.set(content, 20);
  dv.setUint32(20 + content.length, off, true); dv.setUint32(24 + content.length, 0x004e4942, true);
  let p = 28 + content.length;
  for (const b of bufList) { out.set(b, p); p += b.length; }
  return out;
}
