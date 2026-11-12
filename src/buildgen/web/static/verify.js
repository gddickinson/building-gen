// Verify: rebuild every reference building in the browser and compare with the Python package's results
// (exported by the server: counts and the SHA-256 of the .glb it writes).
import { route, api, app, esc, isStatic } from './core.js';
import { loadData, generate, stats, sha256, typeLabel } from './building_data.js';
import { exportGlb } from './bg_glb.js';

route('verify', async () => {
  const [data, ref] = await Promise.all([loadData(), api('/verify')]);
  app().innerHTML = `<p class="kicker">Cross-check</p><h1 class="glow">Browser vs Python</h1>
  <p class="lead">The generator on this site is a JavaScript port of the Python package: Python's random number generator
  (Mersenne Twister, bit for bit), the room program, both layout engines, walls with their openings, slabs, stairs and roofs, and
  trimesh's .glb writer. Below, every reference building is generated again in your browser and compared with what Python
  produced${isStatic() ? ' when this site was built' : ' on this machine just now'}.</p>
  <p id="v-sum" class="mute">Checking...</p>
  <div class="scroll"><table id="v-table"><tr><th>Building</th><th>Seed</th><th>Style changes</th><th>Vertices</th><th>Triangles</th><th>.glb bytes</th><th>.glb SHA-256</th><th></th></tr></table></div>
  <p class="small mute">The same comparison runs as a node test (<code>bg_engine.test.mjs</code>, on rooms, walls, openings, fixtures,
  mesh sizes and coordinates too) in <code>tests/test_web.py</code>. ${isStatic() ? 'With the local app running, the generator page can also check any building you make against the Python server.' : 'The generator page can check any building you make against this server.'}</p>`;
  const table = document.getElementById('v-table');
  let same = 0;
  for (const c of ref) {
    const b = generate(data, c.type, c.seed, c.overrides), s = stats(b), glb = exportGlb(b.nodes), h = await sha256(glb);
    const ok = h === c.glb_sha256 && s.vertices === c.vertices && s.faces === c.faces;
    same += ok;
    const ov = Object.entries(c.overrides).map(([k, v]) => `${k}=${v}`).join(', ') || '—';
    table.insertAdjacentHTML('beforeend', `<tr><td><a href="#/generate?${new URLSearchParams({ type: c.type, seed: c.seed, ...c.overrides })}">${esc(typeLabel(c.type))}</a></td><td>${c.seed}</td><td class="small">${esc(ov)}</td>
      <td>${s.vertices} / ${c.vertices}</td><td>${s.faces} / ${c.faces}</td><td>${glb.length} / ${c.glb_length}</td><td class="mono small">${h.slice(0, 12)}…</td>
      <td class="${ok ? 'ok' : 'bad'}">${ok ? 'identical' : 'differs'}</td></tr>`);
  }
  document.getElementById('v-sum').innerHTML = `<b class="${same === ref.length ? 'ok' : 'err'}">${same} of ${ref.length}</b> buildings identical (browser / Python).`;
});
