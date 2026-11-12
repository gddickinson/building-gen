// Generator page: the building generator running in the browser (JS port), with the parameters the Python has
// (type, style, seed) and the StyleParams that shape the 3D model, a WebGL view, the floor plans, stats and .glb export.
import { route, app, esc, list, onLeave, download, isStatic, api } from './core.js';
import { loadData, generate, stats, typeLabel, sha256, nodePart, nodeFloor } from './building_data.js';
import { createViewer } from './gl_view.js';
import { drawPlan } from './plan_view.js';
import { exportGlb } from './bg_glb.js';
import { roomArea } from './bg_util.js';

const SLIDERS = [['roof_pitch', 'Roof pitch (rise/run)', 0.05], ['roof_overhang', 'Roof overhang', 0.05, ' m'],
  ['floor_height', 'Floor height', 0.1, ' m'], ['slab_thickness', 'Slab thickness', 0.05, ' m'], ['stair_riser', 'Stair riser', 0.01, ' m']];
const PARTS = [['roof', 'Roof'], ['ceiling', 'Top slab'], ['wall', 'Walls'], ['slab', 'Floor slabs'], ['stairs', 'Stairs']];

route('generate', async (args, query) => {
  const data = await loadData();
  const types = Object.keys(data.templates);
  const base = data.styles.params.georgian, controls = data.styles.controls;
  const st = { type: types.includes(query.type) ? query.type : 'townhouse_reference', seed: Number.isInteger(+query.seed) && query.seed !== '' ? +query.seed : 42, style: 'georgian', ov: {} };
  for (const k of Object.keys(controls)) if (query[k] !== undefined) st.ov[k] = Array.isArray(controls[k]) ? query[k] : +query[k];
  const show = Object.fromEntries(PARTS.map(([k]) => [k, true]));
  let upTo = Infinity, building = null, planFloor = 0, viewer = null;

  app().innerHTML = `<p class="kicker">Generator · runs in your browser</p><h1 class="glow">Generate a building</h1>
  <div class="vw">
    <div class="controls">
      <h3>Building</h3>
      <label for="g-type">Type</label><select id="g-type">${list(types, t => `<option value="${t}">${esc(typeLabel(t))}</option>`)}</select>
      <p class="small mute" id="g-notes"></p>
      <label for="g-seed">Seed</label>
      <div class="seedrow"><button class="alt" id="g-prev" aria-label="Previous seed">−</button><input id="g-seed" type="number" step="1" min="0" value="${st.seed}"><button class="alt" id="g-next" aria-label="Next seed">+</button><button class="alt" id="g-rand">Random</button></div>
      <label for="g-style">Style</label><select id="g-style">${list(data.styles.styles, s => `<option>${esc(s)}</option>`)}</select>
      <h3>Style parameters</h3>
      <label>Roof type</label><div class="seg" id="g-roof">${list(controls.roof_type, r => `<button data-v="${r}">${r}</button>`)}</div>
      <div id="g-sliders"></div>
      <button class="alt" id="g-reset">Reset style</button>
      <h3>Show</h3>
      <div class="checks">${list(PARTS, ([k, l]) => `<label><input type="checkbox" data-part="${k}" checked> ${l}</label>`)}</div>
      <label for="g-upto">Floors shown <b id="g-upto-v">all</b></label><input id="g-upto" type="range" min="0" max="1" step="1" value="1">
      <h3>Export</h3>
      <button id="g-glb">Download .glb</button>${isStatic() ? '' : '<button class="alt" id="g-check">Check against Python</button>'}
      <p class="small mute" id="g-check-out">The .glb is written in the browser, byte for byte the file the <code>buildgen</code> CLI writes for these parameters.</p>
    </div>
    <div class="view">
      <canvas id="g-gl" tabindex="0" aria-label="3D view of the generated building. Drag to orbit, shift-drag to pan, wheel to zoom, arrow keys to orbit, F to frame."></canvas>
      <p class="small mute">Drag to orbit · shift / right-drag to pan · wheel or pinch to zoom · arrow keys, + / −, F to frame. <button class="alt mini" id="g-frame">Frame</button></p>
      <div class="tiles" id="g-stats"></div>
      <h2>Floor plans</h2>
      <div class="seg" id="g-floors"></div>
      <canvas id="g-plan" class="plan" role="img" aria-label="Floor plan of the selected storey"></canvas>
      <p class="small mute">Rooms coloured by function; <span style="color:#ffd23f">●</span> front / back door, <span style="color:#ff9f4f">●</span> door, <span style="color:#4fc3ff">●</span> window; outlines are the fittings the generator places (not drawn in 3D).</p>
      <div class="scroll"><table id="g-rooms"></table></div>
    </div>
  </div>`;

  const $ = s => document.querySelector(s);
  try { viewer = createViewer($('#g-gl')); } catch (e) { $('#g-gl').replaceWith(Object.assign(document.createElement('p'), { className: 'err', textContent: e.message })); }
  onLeave(() => viewer && viewer.destroy());

  const sl = $('#g-sliders');
  for (const [k, lab, step, unit = ''] of SLIDERS) {
    const c = controls[k];
    sl.insertAdjacentHTML('beforeend', `<div class="ctl"><label for="sl-${k}">${lab} <b id="v-${k}"></b></label><input type="range" id="sl-${k}" min="${c.min}" max="${c.max}" step="${step}"></div>`);
    $(`#sl-${k}`).addEventListener('input', e => { st.ov[k] = +e.target.value; schedule(true); });
  }

  function syncControls() {
    $('#g-type').value = st.type; $('#g-seed').value = st.seed; $('#g-style').value = st.style;
    const info = data.types.find(t => t.name === st.type);
    $('#g-notes').textContent = info ? `${info.layout} layout. ${info.notes.split('\n').filter(Boolean).slice(0, 3).join(' ')}` : '';
    const roof = st.ov.roof_type ?? base.roof_type;
    document.querySelectorAll('#g-roof button').forEach(b => b.classList.toggle('on', b.dataset.v === roof));
    for (const [k, , , unit = ''] of SLIDERS) { const v = st.ov[k] ?? base[k]; $(`#sl-${k}`).value = v; $(`#v-${k}`).textContent = (+v).toFixed(2) + unit; }
  }

  function visibleFn() {
    const nodes = building.nodes, top = Math.max(...building.plans.map(p => p.floor_index));
    return i => {
      const n = nodes[i].name, part = nodePart(n), f = nodeFloor(n);
      if (!show[part]) return false;
      if (part === 'roof' || part === 'ceiling') return upTo >= top;
      return f === null || f <= upTo;
    };
  }

  function render(keepCamera) {
    building = generate(data, st.type, st.seed, st.ov, st.style);
    const s = stats(building);
    $('#g-stats').innerHTML = [[s.floors, 'floors'], [s.footprint.toFixed(1) + ' m²', 'footprint'], [s.area.toFixed(1) + ' m²', 'room area (all floors)'],
      [s.rooms, 'rooms'], [`${s.doors} / ${s.windows}`, 'doors / windows'], [s.faces.toLocaleString('en'), 'triangles']]
      .map(([b, t]) => `<div class="tile"><b>${b}</b><span>${t}</span></div>`).join('');
    const floors = building.plans.map(p => p.floor_index);
    const up = $('#g-upto');
    up.min = Math.min(...floors); up.max = Math.max(...floors);
    if (upTo === Infinity || upTo > +up.max) upTo = +up.max;
    up.value = upTo; $('#g-upto-v').textContent = upTo >= +up.max ? 'all' : `up to ${upTo}`;
    if (!floors.includes(planFloor)) planFloor = floors[0];
    $('#g-floors').innerHTML = list(floors, f => `<button data-f="${f}" class="${f === planFloor ? 'on' : ''}">${f < 0 ? 'basement' : f === 0 ? 'ground' : 'floor ' + f}</button>`);
    drawPlanNow();
    if (viewer) { viewer.setScene(building.nodes, keepCamera); viewer.setVisible(visibleFn()); }
    const qs = new URLSearchParams({ type: st.type, seed: st.seed, ...st.ov });
    history.replaceState(null, '', '#/generate?' + qs);
    $('#g-check-out').textContent = 'The .glb is written in the browser, byte for byte the file the buildgen CLI writes for these parameters.';
  }

  function drawPlanNow() {
    const plan = building.plans.find(p => p.floor_index === planFloor);
    drawPlan($('#g-plan'), plan);
    $('#g-rooms').innerHTML = `<tr><th>Room</th><th>Type</th><th>Size (m)</th><th>Area</th><th>Doors</th><th>Windows</th></tr>` + list(plan.rooms, r =>
      `<tr><td>${esc(r.name)}</td><td>${esc(r.room_type)}</td><td>${(r.b[2] - r.b[0]).toFixed(2)} × ${(r.b[3] - r.b[1]).toFixed(2)}</td><td>${roomArea(r).toFixed(1)} m²${r.ring ? ' (L-shaped)' : ''}</td>
      <td>${r.openings.filter(o => o.type !== 'window').length}</td><td>${r.openings.filter(o => o.type === 'window').length}</td></tr>`);
  }

  let pending = 0;
  const schedule = keep => { syncControls(); if (!pending) pending = requestAnimationFrame(() => { pending = 0; render(keep); }); };
  const setSeed = v => { st.seed = Math.max(0, Math.trunc(v) || 0); schedule(true); };

  $('#g-type').addEventListener('change', e => { st.type = e.target.value; upTo = Infinity; schedule(false); });
  $('#g-style').addEventListener('change', e => { st.style = e.target.value; schedule(true); });
  $('#g-seed').addEventListener('change', e => setSeed(+e.target.value));
  $('#g-prev').addEventListener('click', () => setSeed(st.seed - 1));
  $('#g-next').addEventListener('click', () => setSeed(st.seed + 1));
  $('#g-rand').addEventListener('click', () => setSeed(Math.floor(Math.random() * 100000)));
  $('#g-roof').addEventListener('click', e => { const v = e.target.dataset.v; if (v) { st.ov.roof_type = v; schedule(true); } });
  $('#g-reset').addEventListener('click', () => { st.ov = {}; schedule(true); });
  $('#g-frame').addEventListener('click', () => viewer && viewer.frame());
  $('#g-upto').addEventListener('input', e => { upTo = +e.target.value; $('#g-upto-v').textContent = upTo >= +e.target.max ? 'all' : `up to ${upTo}`; viewer && viewer.setVisible(visibleFn()); });
  document.querySelectorAll('[data-part]').forEach(c => c.addEventListener('change', () => { show[c.dataset.part] = c.checked; viewer && viewer.setVisible(visibleFn()); }));
  $('#g-floors').addEventListener('click', e => { if (e.target.dataset.f !== undefined) { planFloor = +e.target.dataset.f; document.querySelectorAll('#g-floors button').forEach(b => b.classList.toggle('on', b === e.target)); drawPlanNow(); } });
  $('#g-glb').addEventListener('click', () => download(`${st.type}_${st.style}_s${st.seed}.glb`, new Blob([exportGlb(building.nodes)], { type: 'model/gltf-binary' })));
  const chk = $('#g-check');
  if (chk) chk.addEventListener('click', async () => {
    const out = $('#g-check-out');
    out.textContent = 'Asking the Python server...';
    try {
      const py = await api('/building?' + new URLSearchParams({ type: st.type, seed: st.seed, style: st.style, ...st.ov }), { fresh: true });
      const js = await sha256(exportGlb(building.nodes)), s = stats(building);
      const same = js === py.glb_sha256;
      out.innerHTML = `<span class="${same ? 'ok' : 'err'}">${same ? 'Identical' : 'Different'}</span>: Python ${py.vertices} vertices / ${py.faces} faces, .glb ${py.glb_sha256.slice(0, 12)}…; browser ${s.vertices} / ${s.faces}, ${js.slice(0, 12)}…`;
    } catch (e) { out.innerHTML = `<span class="err">${esc(e.message)}</span>`; }
  });
  window.addEventListener('resize', drawPlanNow);
  onLeave(() => { viewer && viewer.destroy(); window.removeEventListener('resize', drawPlanNow); });
  syncControls();
  render(false);
});
