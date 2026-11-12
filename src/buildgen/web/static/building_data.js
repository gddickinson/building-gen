// Shared data for the pages: templates and styles from the API (exported JSON on the static site), the in-browser
// generator, labels and a SHA-256 helper for comparing .glb files with the Python package.
import { api } from './core.js';
import { generateBuilding } from './bg_pipeline.js';

export const TYPE_LABELS = {
  townhouse: 'Georgian townhouse (template)', townhouse_reference: 'Georgian townhouse (reference)',
  grosvenor_townhouse: 'Grosvenor townhouse', victorian_terrace: 'Victorian terrace', cottage: 'English cottage',
  tavern: 'Medieval tavern',
};
export const typeLabel = t => TYPE_LABELS[t] || t.replace(/_/g, ' ');

export async function loadData() {
  const [templates, styles, types] = await Promise.all([api('/templates'), api('/styles'), api('/types')]);
  return { templates, styles, types };
}

export function generate(data, type, seed, overrides = {}, style = 'georgian') {
  return generateBuilding(data.templates, type, seed, overrides, style);
}

export function stats(b) {
  let rooms = 0, doors = 0, windows = 0, walls = 0, v = 0, f = 0;
  for (const p of b.plans) {
    rooms += p.rooms.length; walls += p.walls.length;
    for (const r of p.rooms) for (const o of r.openings) o.type === 'window' ? windows++ : doors++;
  }
  for (const n of b.nodes) { v += n.mesh.vertices.length; f += n.mesh.faces.length; }
  return { floors: b.num_floors, footprint: b.footprint_area, area: b.total_floor_area, rooms, walls, doors, windows, nodes: b.nodes.length, vertices: v, faces: f };
}

export async function sha256(bytes) {
  const d = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(d)].map(x => x.toString(16).padStart(2, '0')).join('');
}

// Which part of the building a scene node is: slab, wall (exterior/interior), stairs, ceiling, roof.
export function nodePart(name) {
  if (name === 'roof') return 'roof';
  if (name === 'ceiling_slab') return 'ceiling';
  if (name.endsWith('_slab')) return 'slab';
  if (name.endsWith('_stairs')) return 'stairs';
  return 'wall';
}
export const nodeFloor = name => { const m = /^floor_(-?\d+)_/.exec(name); return m ? +m[1] : null; };
