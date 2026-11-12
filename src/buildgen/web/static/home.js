// Home page: hero with a live 3D building, counts from the API, entry cards.
import { route, api, app, onLeave } from './core.js';
import { loadData, generate, typeLabel } from './building_data.js';
import { createViewer } from './gl_view.js';

const DOORS = [
  ['#/generate', 'Generator', 'Pick a building type and a seed, change the roof and storey heights, look around in 3D, read the floor plans and download the .glb.'],
  ['#/gallery', 'Gallery', 'Every building type at a few seeds, generated on the spot.'],
  ['#/types', 'Types', 'The six templates: grid (reference) layouts and the BSP townhouse, with the notes they carry.'],
  ['#/detail', 'Detailed model', 'The engineering builder (bricks, rafters, pipes): Python only, shown as the images the repo ships.'],
  ['#/verify', 'Verify', 'The browser generator against the Python package: same buildings, same .glb bytes.'],
  ['#/about', 'About', 'The pipeline, what runs where, known limitations, how to run it, credits.'],
];

route('home', async () => {
  const [info, data] = await Promise.all([api('/info'), loadData()]);
  app().innerHTML = `
  <section class="hero heroview">
    <div>
      <p class="kicker">Procedural architecture · seeded · glTF</p>
      <h1 class="glow">building-gen</h1>
      <p class="lead">A Python package that procedurally generates 3D buildings: a room program, floor plans with walls, doors and
      windows, then extruded walls, floor slabs, stairs and a roof, exported as glTF. Here the generator runs in your browser:
      same seed, same building as the Python, down to the bytes of the .glb file.</p>
      <a class="btn" href="#/generate">Open the generator</a><a class="btn alt" href="#/gallery">See the gallery</a>
    </div>
    <figure style="margin:0"><canvas id="hero" tabindex="0" style="width:100%;aspect-ratio:4/3;display:block;border:1px solid var(--line);border-radius:6px;touch-action:none" aria-label="3D view of a generated ${typeLabel('grosvenor_townhouse')}, seed 42. Drag to orbit."></canvas>
      <figcaption class="small mute">${typeLabel('grosvenor_townhouse')}, seed 42, roof hidden so the floors show. Drag to orbit.</figcaption></figure>
  </section>
  <div class="tiles">
    <div class="tile"><b>${info.types}</b><span>building types</span></div>
    <div class="tile"><b>${info.style_controls}</b><span>style parameters to change</span></div>
    <div class="tile"><b>${info.researched_types}</b><span>building types with researched design rules</span></div>
    <div class="tile"><b>${info.reference_cases}</b><span>reference buildings checked against Python</span></div>
  </div>
  <div class="grid wide">${DOORS.map(([h, t, d]) => `<a class="card door" href="${h}"><b>${t}</b><span>${d}</span></a>`).join('')}</div>`;
  try {
    const v = createViewer(document.getElementById('hero'));
    onLeave(() => v.destroy());
    const b = generate(data, 'grosvenor_townhouse', 42);
    v.setScene(b.nodes);
    v.setVisible(i => !['roof', 'ceiling_slab'].includes(b.nodes[i].name));
  } catch (e) { document.getElementById('hero').replaceWith(Object.assign(document.createElement('p'), { className: 'err', textContent: e.message })); }
});
