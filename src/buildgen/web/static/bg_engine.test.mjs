// Node test: the JS generator against the Python package on the cases in tests/fixtures/building_fixture.json
// (written by scripts/make_building_fixture.py). Same seed and parameters -> same rooms, walls, openings, the same
// meshes (vertex and face counts, coordinate sums to 1e-9) and the same .glb bytes (SHA-256).
// Run: node src/buildgen/web/static/bg_engine.test.mjs
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { generateBuilding, meshCounts } from './bg_pipeline.js';
import { exportGlb } from './bg_glb.js';
import { PyRandom } from './py_random.js';

const here = fileURLToPath(new URL('.', import.meta.url));
const fx = JSON.parse(readFileSync(here + '../../../../tests/fixtures/building_fixture.json', 'utf8'));
let fails = 0;
const close = (a, b, rtol = 1e-9) => Math.abs(a - b) <= rtol * Math.max(1, Math.abs(a), Math.abs(b));
const fail = msg => { fails++; if (fails < 25) console.log('FAIL', msg); };

for (const r of fx.random) {
  const g = new PyRandom(r.seed);
  const got = { random: r.random.map(() => g.random()), uniform: r.uniform.map(() => g.uniform(-0.3, 0.3)), choice: r.choice.map(() => g.choice(['tr', 'tl', 'br', 'bl'])) };
  for (const k of ['random', 'uniform', 'choice']) if (JSON.stringify(got[k]) !== JSON.stringify(r[k])) fail(`random seed ${r.seed} ${k}`);
}

let glbSame = 0;
for (const c of fx.cases) {
  const id = `${c.type} seed ${c.seed} ${JSON.stringify(c.overrides)}`;
  const b = generateBuilding(fx.templates, c.type, c.seed, c.overrides);
  if (b.num_floors !== c.num_floors) fail(`${id}: floors ${b.num_floors} vs ${c.num_floors}`);
  if (!close(b.footprint_area, c.footprint_area) || !close(b.total_floor_area, c.total_floor_area)) fail(`${id}: areas`);
  c.plans.forEach((p, i) => {
    const q = b.plans[i];
    if (!q || q.rooms.length !== p.rooms.length) return fail(`${id} floor ${p.floor}: rooms ${q && q.rooms.length} vs ${p.rooms.length}`);
    p.rooms.forEach((r, k) => {
      const s = q.rooms[k];
      if (s.name !== r.name || s.room_type !== r.type || !r.bounds.every((v, j) => close(v, s.b[j]))) fail(`${id} floor ${p.floor} room ${r.name}`);
      if (s.openings.length !== r.openings.length || !r.openings.every((o, j) => o.type === s.openings[j].type && close(o.position[0], s.openings[j].position[0]) && close(o.position[1], s.openings[j].position[1]))) fail(`${id} ${r.name} openings`);
      if (s.fixtures.length !== r.fixtures.length || !r.fixtures.every((o, j) => o.type === s.fixtures[j].type && close(o.x, s.fixtures[j].x) && close(o.y, s.fixtures[j].y))) fail(`${id} ${r.name} fixtures`);
    });
    if (q.walls.length !== p.walls.length || !p.walls.every((w, j) => w.type === q.walls[j].wall_type && close(w.start[0], q.walls[j].start[0]) && close(w.end[1], q.walls[j].end[1]))) fail(`${id} floor ${p.floor} walls`);
  });
  const n = meshCounts(b.nodes);
  if (n.vertices !== c.vertices || n.faces !== c.faces || b.nodes.length !== c.nodes.length) fail(`${id}: mesh ${n.nodes}/${n.vertices}/${n.faces} vs ${c.nodes.length}/${c.vertices}/${c.faces}`);
  c.nodes.forEach((nd, i) => {
    const m = b.nodes[i];
    if (!m || m.name !== nd.name || m.mesh.vertices.length !== nd.vertices || m.mesh.faces.length !== nd.faces) return fail(`${id} node ${nd.name}`);
    const sum = [0, 0, 0];
    for (const v of m.mesh.vertices) for (let k = 0; k < 3; k++) sum[k] += v[k];
    if (!sum.every((v, k) => close(v, nd.sum[k], 1e-9))) fail(`${id} node ${nd.name} coordinates`);
  });
  const glb = exportGlb(b.nodes);
  const sha = createHash('sha256').update(glb).digest('hex');
  if (glb.length !== c.glb_length || sha !== c.glb_sha256) fail(`${id}: glb ${glb.length} vs ${c.glb_length} bytes, sha differs`);
  else glbSame++;
}
console.log(`${fx.cases.length} cases, ${fx.random.length} RNG seeds; .glb byte-identical in ${glbSame}/${fx.cases.length}; ${fails} failures`);
process.exit(fails ? 1 : 0);
