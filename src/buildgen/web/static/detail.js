// Detailed model: the engineering builder (individual bricks, rafters, sash windows, pipes) is Python only;
// shown here as the images the repository ships in docs/images (precomputed, not generated in the browser).
import { route, app, list } from './core.js';

const SHOTS = [
  ['front_elevation.png', 'Front elevation with individual bricks, sash windows and the panel front door.'],
  ['cross_section.png', 'Cross section through the structure: floors, joists, walls and roof.'],
  ['building_systems.png', 'The building systems broken out: structure, plumbing, heating, guttering and more.'],
];

route('detail', async () => {
  app().innerHTML = `<p class="kicker">Python only · precomputed images</p><h1 class="glow">The detailed model</h1>
  <p class="lead">Besides the four-stage pipeline that the generator page runs, the repository has an engineering builder
  (<code>src/buildgen/engineering/</code>, driven by <code>build_complete.py</code>) that models a Georgian townhouse element by
  element: brick walls in bond, floor joists and boards, rafters and slates, sash windows, a staircase, chimney, plumbing,
  heating and guttering, with load calculations from material properties. The README counts 82,470 elements.</p>
  <p class="callout">This part is not ported to the browser: its .glb files are 17-18 MB. The pictures below are the images in
  the repository's <code>docs/images/</code>, rendered by its matplotlib diagnostics. To build it yourself, run
  <code>python build_complete.py</code>, then <code>./view.sh</code> for the interactive viewer with toggleable systems.</p>
  ${list(SHOTS, ([f, c]) => `<figure style="margin:18px 0"><img class="shot" src="static/img/${f}" alt="${c}" loading="lazy"><figcaption class="small mute">${c} (docs/images/${f})</figcaption></figure>`)}`;
});
