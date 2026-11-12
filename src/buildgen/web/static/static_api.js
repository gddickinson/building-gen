// Static-site data layer: answers api() calls from the JSON files exported by scripts/build_static.py.
// The generator itself runs in the browser (bg_*.js); /building and /glb (Python's own result) need the local server.
const files = new Map();
async function file(rel) {
  if (!files.has(rel)) files.set(rel, fetch('api/' + rel + '.json').then(r => { if (!r.ok) throw new Error(`${r.status} ${rel}`); return r.json(); }));
  return files.get(rel);
}

export async function staticApi(path) {
  const clean = path.split('?')[0].replace(/^\/+/, '');
  if (clean === 'building' || clean === 'glb')
    throw new Error("Python's own result needs the local app (Python server); the browser generator gives the same building.");
  return file(clean);
}
