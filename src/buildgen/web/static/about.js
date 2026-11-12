// About: what buildgen is, what runs in the browser and what does not, known limitations, how to run it, credits.
import { route, app } from './core.js';

route('about', async () => {
  app().innerHTML = `<p class="kicker">About</p><h1 class="glow">About building-gen</h1>
  <p class="lead">building-gen (<code>buildgen</code>) is a Python package that procedurally generates 3D buildings: interiors and
  exteriors, room layouts, walls, doors, windows, stairs and roofs, exported as glTF for game engines and world-building
  simulations. Generation is deterministic: the same type, style and seed always give the same building.</p>

  <h2>The pipeline</h2>
  <ol>
    <li><b>Building program</b> (<code>program/</code>): rooms per floor with size ranges and adjacencies, varied by the seed;
      optional rooms are kept or dropped at random.</li>
    <li><b>Floor plan layout</b> (<code>layout/</code>): reference types place rooms in a grid taken from real plans
      (<code>grid_layout.py</code>); the template townhouse splits the footprint into a hall column and two wings
      (<code>subdivide.py</code>). Walls are extracted from the room edges, doors go between adjacent rooms, windows along the
      outside, and fittings are placed against room walls.</li>
    <li><b>3D geometry</b> (<code>geometry/</code>): walls with their openings, floor slabs with stairwell holes, straight,
      L-shaped, U-shaped or spiral stairs, a top slab and a hip, gable or flat roof.</li>
    <li><b>Style</b> (<code>style/</code>): StyleParams (storey height, roof type and pitch, colours, ...). The package has one
      built-in style, <code>georgian</code>.</li>
  </ol>

  <h2>What runs where</h2>
  <ul>
    <li><b>Live in the browser</b>: stages 1-4 for all six types, every seed, the georgian style and the style parameters on the
      generator page, plus .glb export. The JavaScript files <code>bg_*.js</code> and <code>py_random.js</code> port the Python line by
      line, including Python's random number generator, so the rooms, the meshes and the .glb file are identical (see
      <a href="#/verify">Verify</a>).</li>
    <li><b>Python only</b>: the engineering builder with individual bricks, rafters and building systems
      (<a href="#/detail">Detailed model</a>, shown as the repository's images), the matplotlib plan sheets and the CLI.
      With the local app, the generator page can ask the Python server for the same building and compare.</li>
  </ul>

  <h2>Known limitations</h2>
  <ul>
    <li>One style for every type: a cottage and a tavern are built with georgian proportions, brick colours and roof.</li>
    <li>The fittings placed in rooms are modern (sofas, wardrobes, fridges, washing machines, fitted bathrooms) in every period.</li>
    <li>The building types are illustrations of a general plan type, not records of real buildings.</li>
  </ul>
  <p class="small mute">Fixed while this web version was made (each with a regression test in <code>tests/test_fixes.py</code>):
  door and window openings were only cut when Blender or manifold3d happened to be installed; floor slabs covered their stairwell
  holes; roofs always ran their ridge front to back (a pyramid on the wide cottage) and faced inward; reference-layout rooms sharing
  a facade got no windows; <code>--list-types</code> offered the design-rules file as a building type; rooms overlapped (carved
  closets, halls over stairwells, shared grid cells); automatic stairwells were below the stairwell minimum; and the 3D model was a
  mirror image of the floor plans (plan y now runs to −z, so seen from the street the plan's left is on the left).</p>

  <h2>Run it yourself</h2>
  <h3>Command line</h3>
  <pre>pip install -e ".[dev]"
buildgen --type townhouse --style georgian --seed 42 --output output/
buildgen --list-types</pre>
  <h3>Web app (this site, with the Python API)</h3>
  <pre>pip install -r requirements-web.txt
python run_web.py          # http://127.0.0.1:8228</pre>
  <p>The static GitHub Pages site is exported by <code>scripts/build_static.py</code>; there the generator runs entirely in the browser.</p>

  <h2>Credits</h2>
  <p>building-gen by George Dickinson, MIT licence. Built on Shapely, trimesh, NetworkX, NumPy, Matplotlib, PyYAML and Pillow.
  Web version built with AI assistance from <a href="https://claude.com/">Claude (Anthropic)</a>.</p>`;
});
