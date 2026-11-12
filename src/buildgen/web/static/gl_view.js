// Raw WebGL viewer for generated buildings: flat-shaded triangles with face colours, two lights, a ground grid and
// an orbit camera (drag to orbit, shift/right-drag or two fingers to pan, wheel or pinch to zoom, arrow keys, + / -,
// F to frame). Draws only when something changed.
import { perspective, lookAt, multiply, orbitEye, cameraAxes } from './gl_math.js';

const VS = `attribute vec3 aPos; attribute vec3 aNor; attribute vec4 aCol; uniform mat4 uVP; uniform vec3 uEye;
varying vec3 vNor; varying vec4 vCol; varying vec3 vView;
void main() { gl_Position = uVP * vec4(aPos, 1.0); vNor = aNor; vCol = aCol; vView = normalize(uEye - aPos); }`;
const FS = `precision mediump float; varying vec3 vNor; varying vec4 vCol; varying vec3 vView; uniform float uFlat;
void main() {
  vec3 n = normalize(vNor); if (dot(n, vView) < 0.0) n = -n;
  float key = max(dot(n, normalize(vec3(0.45, 0.8, -0.35))), 0.0), fill = max(dot(n, normalize(vec3(-0.6, 0.3, 0.7))), 0.0);
  float l = mix(0.36 + 0.52 * key + 0.2 * fill, 1.0, uFlat);
  gl_FragColor = vec4(vCol.rgb * l, 1.0);
}`;

function compile(gl, type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src); gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
  return s;
}

// Expand indexed meshes into flat-shaded triangle arrays; returns arrays plus per-node [first, count] ranges.
export function flatten(nodes) {
  let tris = 0;
  for (const n of nodes) tris += n.mesh.faces.length;
  const pos = new Float32Array(tris * 9), nor = new Float32Array(tris * 9), col = new Uint8Array(tris * 12);
  const ranges = [], lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  let t = 0;
  for (const n of nodes) {
    const { vertices: V, faces: Fs, colors: C } = n.mesh, first = t * 3;
    Fs.forEach((f, fi) => {
      const a = V[f[0]], b = V[f[1]], c = V[f[2]];
      const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
      const nn = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
      for (let k = 0; k < 3; k++) {
        const p = V[f[k]];
        pos.set(p, t * 9 + k * 3); nor.set(nn, t * 9 + k * 3); col.set(C[fi], t * 12 + k * 4);
        for (let d = 0; d < 3; d++) { lo[d] = Math.min(lo[d], p[d]); hi[d] = Math.max(hi[d], p[d]); }
      }
      t++;
    });
    ranges.push([first, t * 3 - first]);
  }
  return { pos, nor, col, ranges, lo, hi };
}

export function createViewer(canvas) {
  const gl = canvas.getContext('webgl', { antialias: true, preserveDrawingBuffer: true });
  if (!gl) throw new Error('WebGL is not available in this browser.');
  const prog = gl.createProgram();
  gl.attachShader(prog, compile(gl, gl.VERTEX_SHADER, VS)); gl.attachShader(prog, compile(gl, gl.FRAGMENT_SHADER, FS));
  gl.linkProgram(prog);
  const loc = n => gl.getAttribLocation(prog, n), uni = n => gl.getUniformLocation(prog, n);
  const A = { pos: loc('aPos'), nor: loc('aNor'), col: loc('aCol') }, U = { vp: uni('uVP'), eye: uni('uEye'), flat: uni('uFlat') };
  const bufs = { pos: gl.createBuffer(), nor: gl.createBuffer(), col: gl.createBuffer(), gpos: gl.createBuffer(), gnor: gl.createBuffer(), gcol: gl.createBuffer() };
  const cam = { yaw: 0.6, pitch: 0.45, dist: 30, target: [0, 0, 0] };
  let ranges = [], visible = () => true, gridCount = 0, frameReq = 0, alive = true, home = null;

  function upload(b, data) { gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW); }
  function grid(lo, hi) {
    const cx = (lo[0] + hi[0]) / 2, cz = (lo[2] + hi[2]) / 2, half = Math.ceil(Math.max(hi[0] - lo[0], hi[2] - lo[2]) * 1.2 / 2) + 2, y = Math.min(lo[1], 0) - 0.01;
    const p = [];
    for (let i = -half; i <= half; i++) { p.push(cx + i, y, cz - half, cx + i, y, cz + half, cx - half, y, cz + i, cx + half, y, cz + i); }
    const n = p.length / 3, nor = new Float32Array(n * 3).fill(0), col = new Uint8Array(n * 4);
    for (let i = 0; i < n; i++) col.set([60, 80, 120, 255], i * 4);
    upload(bufs.gpos, new Float32Array(p)); upload(bufs.gnor, nor); upload(bufs.gcol, col);
    gridCount = n;
  }
  function attrib(a, b, size, type, normalized) { gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.enableVertexAttribArray(a); gl.vertexAttribPointer(a, size, type, normalized, 0, 0); }

  function draw() {
    frameReq = 0;
    if (!alive) return;
    const dpr = Math.min(2, window.devicePixelRatio || 1), w = Math.max(1, Math.round(canvas.clientWidth * dpr)), h = Math.max(1, Math.round(canvas.clientHeight * dpr));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    gl.viewport(0, 0, w, h);
    gl.clearColor(0.02, 0.025, 0.05, 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.enable(gl.DEPTH_TEST);
    gl.useProgram(prog);
    const eye = orbitEye(cam);
    gl.uniformMatrix4fv(U.vp, false, multiply(perspective(0.8, w / h, cam.dist / 200, cam.dist * 20), lookAt(eye, cam.target, [0, 1, 0])));
    gl.uniform3fv(U.eye, eye);
    gl.uniform1f(U.flat, 1);
    attrib(A.pos, bufs.gpos, 3, gl.FLOAT, false); attrib(A.nor, bufs.gnor, 3, gl.FLOAT, false); attrib(A.col, bufs.gcol, 4, gl.UNSIGNED_BYTE, true);
    if (gridCount) gl.drawArrays(gl.LINES, 0, gridCount);
    gl.uniform1f(U.flat, 0);
    attrib(A.pos, bufs.pos, 3, gl.FLOAT, false); attrib(A.nor, bufs.nor, 3, gl.FLOAT, false); attrib(A.col, bufs.col, 4, gl.UNSIGNED_BYTE, true);
    ranges.forEach(([first, count], i) => { if (count && visible(i)) gl.drawArrays(gl.TRIANGLES, first, count); });
  }
  const redraw = () => { if (!frameReq) frameReq = requestAnimationFrame(draw); };

  function frame() {
    if (!home) return;
    Object.assign(cam, structuredClone(home));
    redraw();
  }

  // pointer input: orbit / pan / pinch
  const pts = new Map();
  let last = null, pinch = 0;
  const pan = (dx, dy) => {
    const { right, up } = cameraAxes(cam), s = cam.dist * 0.0016;
    for (let k = 0; k < 3; k++) cam.target[k] += (-dx * right[k] + dy * up[k]) * s;
  };
  canvas.addEventListener('contextmenu', e => e.preventDefault());
  canvas.addEventListener('pointerdown', e => { canvas.setPointerCapture(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]); last = [e.clientX, e.clientY]; pinch = 0; });
  canvas.addEventListener('pointerup', e => { pts.delete(e.pointerId); last = null; pinch = 0; });
  canvas.addEventListener('pointercancel', e => { pts.delete(e.pointerId); last = null; });
  canvas.addEventListener('pointermove', e => {
    if (!pts.has(e.pointerId)) return;
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    if (pts.size === 2) {
      const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]);
      if (pinch) cam.dist = Math.min(400, Math.max(2, cam.dist * pinch / d));
      pinch = d; redraw(); return;
    }
    if (!last) return;
    const dx = e.clientX - last[0], dy = e.clientY - last[1];
    last = [e.clientX, e.clientY];
    if (e.shiftKey || e.buttons === 2) pan(dx, dy);
    else { cam.yaw -= dx * 0.008; cam.pitch = Math.min(1.5, Math.max(-0.2, cam.pitch + dy * 0.008)); }
    redraw();
  });
  canvas.addEventListener('wheel', e => { e.preventDefault(); cam.dist = Math.min(400, Math.max(2, cam.dist * Math.exp(e.deltaY * 0.001))); redraw(); }, { passive: false });
  canvas.addEventListener('keydown', e => {
    const k = e.key, step = 0.08;
    if (k === 'ArrowLeft') cam.yaw += step; else if (k === 'ArrowRight') cam.yaw -= step;
    else if (k === 'ArrowUp') cam.pitch = Math.min(1.5, cam.pitch + step); else if (k === 'ArrowDown') cam.pitch = Math.max(-0.2, cam.pitch - step);
    else if (k === '+' || k === '=') cam.dist = Math.max(2, cam.dist * 0.9); else if (k === '-' || k === '_') cam.dist = Math.min(400, cam.dist * 1.1);
    else if (k === 'f' || k === 'F') { frame(); return; } else return;
    e.preventDefault(); redraw();
  });
  const ro = new ResizeObserver(redraw);
  ro.observe(canvas);

  return {
    cam,
    // nodes: [{name, mesh}]; keepCamera keeps the current view (e.g. when only a parameter changed)
    setScene(nodes, keepCamera = false) {
      const f = flatten(nodes);
      upload(bufs.pos, f.pos); upload(bufs.nor, f.nor); upload(bufs.col, f.col);
      ranges = f.ranges;
      grid(f.lo, f.hi);
      const size = Math.max(f.hi[0] - f.lo[0], f.hi[1] - f.lo[1], f.hi[2] - f.lo[2]);
      home = { yaw: 0.6, pitch: 0.42, dist: size * 1.9, target: [(f.lo[0] + f.hi[0]) / 2, (f.lo[1] + f.hi[1]) / 2.4, (f.lo[2] + f.hi[2]) / 2] };
      if (!keepCamera) frame(); else redraw();
    },
    setVisible(fn) { visible = fn; redraw(); },
    frame, redraw,
    snapshot() { draw(); return canvas.toDataURL('image/png'); },
    destroy() { alive = false; ro.disconnect(); const ext = gl.getExtension('WEBGL_lose_context'); if (ext) ext.loseContext(); },
  };
}
