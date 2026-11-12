// Gallery: every building type at three seeds, generated and rendered in the browser.
import { route, app, esc } from './core.js';
import { loadData, generate, stats, typeLabel } from './building_data.js';
import { snapshots } from './snapshots.js';

const SEEDS = [42, 7, 1];

route('gallery', async () => {
  const data = await loadData();
  const items = Object.keys(data.templates).flatMap(type => SEEDS.map(seed => ({ type, seed })));
  app().innerHTML = `<p class="kicker">Gallery</p><h1 class="glow">Every type, three seeds</h1>
  <p class="lead">Generated in your browser just now with the default georgian style. Click one to open it in the generator.</p>
  <div class="grid gal" id="gal"><p class="mute">Rendering...</p></div>`;
  await new Promise(r => setTimeout(r, 30));
  let shots;
  try { shots = snapshots(data, items); } catch (e) { document.getElementById('gal').innerHTML = `<p class="err">${esc(e.message)}</p>`; return; }
  document.getElementById('gal').innerHTML = items.map((it, i) => {
    const s = stats(generate(data, it.type, it.seed));
    return `<a class="card" href="#/generate?type=${it.type}&seed=${it.seed}"><img src="${shots[i]}" alt="3D render of a ${esc(typeLabel(it.type))}, seed ${it.seed}">
      <b>${esc(typeLabel(it.type))}</b><small>seed ${it.seed} · ${s.floors} floors · ${s.rooms} rooms · ${s.footprint.toFixed(0)} m² footprint</small></a>`;
  }).join('');
});
