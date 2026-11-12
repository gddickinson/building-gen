// Types: the building templates, their layout kind and the notes written at the top of each YAML file.
import { route, app, esc, list } from './core.js';
import { loadData, typeLabel } from './building_data.js';

route('types', async () => {
  const data = await loadData();
  app().innerHTML = `<p class="kicker">Templates</p><h1 class="glow">Building types</h1>
  <p class="lead">Each type is a YAML template in <code>src/buildgen/program/templates/</code>. Reference (grid) templates place rooms
  in the cells of a rows × columns grid taken from real plans; the template (BSP) type builds a room program and splits the
  footprint into a hall column and two wings. The notes below are the comments at the top of each file.</p>
  ${list(data.types, t => {
    const tm = data.templates[t.name], fp = tm.footprint || {}, floors = (tm.grid ? tm.grid.floors : tm.floors) || [];
    return `<div class="panel"><h2 style="margin-top:0">${esc(typeLabel(t.name))} <span class="tag a">${esc(t.name)}</span> <span class="tag b">${esc(t.layout)}</span></h2>
    <p class="small mute">Footprint ${fp.width ?? '8'} ± ${fp.width_var ?? '1'} m wide, ${fp.depth ?? '12'} ± ${fp.depth_var ?? '1.5'} m deep,
    walls ${fp.wall_thickness ?? 0.3} m · ${floors.length} floors in the template · <a href="#/generate?type=${t.name}&seed=42">generate</a></p>
    <pre>${esc(t.notes)}</pre></div>`;
  })}`;
});
